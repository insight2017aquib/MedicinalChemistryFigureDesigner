"""Semantic validation for knowledge packs."""

from __future__ import annotations

from figure_agent.knowledge.exceptions import KnowledgePackValidationError
from figure_agent.knowledge.models import KnowledgePackManifest
from figure_agent.knowledge.semver import satisfies


class KnowledgePackValidator:
    """Validate pack manifests and inter-pack relationships."""

    def validate_manifest(self, manifest: KnowledgePackManifest) -> None:
        """Validate a single pack manifest."""
        errors = list(self.collect_manifest_errors(manifest))
        if errors:
            raise KnowledgePackValidationError(
                "Knowledge pack validation failed",
                errors=errors,
            )

    def collect_manifest_errors(
        self,
        manifest: KnowledgePackManifest,
    ) -> list[str]:
        """Return validation errors for a manifest."""
        errors: list[str] = []

        if manifest.inheritance and manifest.inheritance.id == manifest.id:
            errors.append("pack cannot extend itself")

        dependency_ids = [dependency.id for dependency in manifest.depends_on]
        if len(dependency_ids) != len(set(dependency_ids)):
            errors.append("depends_on contains duplicate pack ids")

        if manifest.inheritance and manifest.inheritance.id in dependency_ids:
            errors.append("depends_on must not duplicate extends target")

        for entry in manifest.entries:
            if not entry.summary and not entry.content:
                errors.append(
                    f"entry {entry.id!r} must include summary or content",
                )

        return errors

    def validate_registry(
        self,
        manifests: dict[str, KnowledgePackManifest],
    ) -> None:
        """Validate a registry of co-loaded manifests."""
        errors = list(self.collect_registry_errors(manifests))
        if errors:
            raise KnowledgePackValidationError(
                "Knowledge pack registry validation failed",
                errors=errors,
            )

    def collect_registry_errors(
        self,
        manifests: dict[str, KnowledgePackManifest],
    ) -> list[str]:
        """Return cross-pack validation errors."""
        errors: list[str] = []

        for pack_id, manifest in manifests.items():
            if pack_id != manifest.id:
                errors.append(
                    f"registry key {pack_id!r} does not match manifest id {manifest.id!r}",
                )

            if manifest.inheritance:
                parent_id = manifest.inheritance.id
                if parent_id not in manifests:
                    errors.append(
                        f"pack {manifest.id!r} extends missing pack {parent_id!r}",
                    )
                else:
                    parent = manifests[parent_id]
                    constraint = manifest.inheritance.version_constraint
                    if constraint and not satisfies(parent.version, constraint):
                        errors.append(
                            f"pack {manifest.id!r} requires parent "
                            f"{parent_id}@{constraint}, found {parent.semantic_version}",
                        )

            for dependency in manifest.depends_on:
                if dependency.optional:
                    continue
                if dependency.id not in manifests:
                    errors.append(
                        f"pack {manifest.id!r} depends on missing pack {dependency.id!r}",
                    )
                    continue
                target = manifests[dependency.id]
                if not satisfies(target.version, dependency.version_constraint):
                    errors.append(
                        f"pack {manifest.id!r} dependency {dependency.id} "
                        f"requires {dependency.version_constraint}, "
                        f"found {target.semantic_version}",
                    )

        errors.extend(_collect_inheritance_cycles(manifests))
        errors.extend(_collect_alias_conflicts(manifests))
        return errors


def _collect_inheritance_cycles(
    manifests: dict[str, KnowledgePackManifest],
) -> list[str]:
    errors: list[str] = []

    def visit(pack_id: str, trail: list[str]) -> None:
        if pack_id in trail:
            cycle = " -> ".join([*trail, pack_id])
            errors.append(f"inheritance cycle detected: {cycle}")
            return
        manifest = manifests.get(pack_id)
        if manifest is None or manifest.inheritance is None:
            return
        visit(manifest.inheritance.id, [*trail, pack_id])

    for pack_id in manifests:
        visit(pack_id, [])

    return errors


def _collect_alias_conflicts(
    manifests: dict[str, KnowledgePackManifest],
) -> list[str]:
    canonical_owner: dict[str, str] = {}
    alias_owner: dict[str, str] = {}
    errors: list[str] = []

    for pack_id, manifest in manifests.items():
        for canonical, aliases in manifest.aliases.items():
            if canonical in canonical_owner and canonical_owner[canonical] != pack_id:
                errors.append(
                    f"canonical alias {canonical!r} defined in multiple packs",
                )
            canonical_owner[canonical] = pack_id

            for alias in aliases:
                if alias in alias_owner and alias_owner[alias] != pack_id:
                    errors.append(
                        f"alias {alias!r} defined in multiple packs",
                    )
                alias_owner[alias] = pack_id

                if alias in canonical_owner:
                    errors.append(
                        f"alias {alias!r} conflicts with canonical term",
                    )

    return errors