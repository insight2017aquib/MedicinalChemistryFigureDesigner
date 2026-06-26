"""Registry for loading, resolving, and querying knowledge packs."""

from __future__ import annotations

from pathlib import Path

from figure_agent.knowledge.exceptions import KnowledgePackResolutionError
from figure_agent.knowledge.loader import discover_pack_directories, load_pack_directory
from figure_agent.knowledge.models import (
    KnowledgeEntry,
    KnowledgePackManifest,
    PackDependency,
    ResolvedKnowledgePack,
)
from figure_agent.knowledge.semver import satisfies
from figure_agent.knowledge.validator import KnowledgePackValidator

PathLike = str | Path


class KnowledgePackRegistry:
    """Index of knowledge packs with inheritance and alias resolution."""

    def __init__(self, *, validator: KnowledgePackValidator | None = None) -> None:
        self._validator = validator or KnowledgePackValidator()
        self._manifests: dict[str, KnowledgePackManifest] = {}
        self._paths: dict[str, Path] = {}

    @property
    def pack_ids(self) -> tuple[str, ...]:
        """Return registered pack identifiers."""
        return tuple(sorted(self._manifests))

    def register(
        self,
        manifest: KnowledgePackManifest,
        *,
        source_path: Path | None = None,
    ) -> None:
        """Register a pack manifest."""
        self._manifests[manifest.id] = manifest
        if source_path is not None:
            self._paths[manifest.id] = source_path

    def get(self, pack_id: str) -> KnowledgePackManifest | None:
        """Return a manifest by id."""
        return self._manifests.get(pack_id)

    def load_directory(self, directory: PathLike) -> KnowledgePackManifest:
        """Load and register a pack from a directory."""
        path = Path(directory)
        manifest = load_pack_directory(path)
        self.register(manifest, source_path=path)
        return manifest

    def load_root(self, root: PathLike) -> list[KnowledgePackManifest]:
        """Discover and register all packs under a root directory."""
        loaded: list[KnowledgePackManifest] = []
        for directory in discover_pack_directories(root):
            loaded.append(self.load_directory(directory))
        return loaded

    def validate(self) -> None:
        """Validate all registered packs and their relationships."""
        self._validator.validate_registry(self._manifests)

    def resolve(self, pack_id: str) -> ResolvedKnowledgePack:
        """Resolve a pack with inheritance merged and dependencies checked."""
        errors = list(self._collect_resolution_errors(pack_id))
        if errors:
            raise KnowledgePackResolutionError(
                f"Failed to resolve knowledge pack {pack_id!r}",
                errors=errors,
            )
        return self._resolve_pack(pack_id, visited=[])

    def resolve_alias(self, pack_id: str, term: str) -> str:
        """Resolve a term to its canonical alias within a resolved pack."""
        resolved = self.resolve(pack_id)
        lowered = term.strip().lower()
        for canonical, aliases in resolved.aliases.items():
            if lowered == canonical.lower():
                return canonical
            if any(lowered == alias.lower() for alias in aliases):
                return canonical
        return term

    def _resolve_pack(
        self,
        pack_id: str,
        *,
        visited: list[str],
    ) -> ResolvedKnowledgePack:
        if pack_id in visited:
            raise KnowledgePackResolutionError(
                f"inheritance cycle detected for pack {pack_id!r}",
            )

        manifest = self._manifests[pack_id]
        inherited_from: list[str] = []
        merged_entries: dict[str, KnowledgeEntry] = {}
        merged_aliases: dict[str, list[str]] = {}
        merged_dependencies: dict[str, PackDependency] = {}

        if manifest.inheritance is not None:
            parent = self._resolve_pack(
                manifest.inheritance.id,
                visited=[*visited, pack_id],
            )
            inherited_from.extend([*parent.inherited_from, parent.id])
            merged_entries.update({entry.id: entry for entry in parent.entries})
            merged_aliases.update(parent.aliases)
            merged_dependencies.update(
                {dependency.id: dependency for dependency in parent.depends_on},
            )

        for entry in manifest.entries:
            merged_entries[entry.id] = entry
        merged_aliases.update(manifest.aliases)
        for dependency in manifest.depends_on:
            merged_dependencies[dependency.id] = dependency

        resolved_dependencies = [
            dependency.id
            for dependency in merged_dependencies.values()
            if dependency.id in self._manifests
        ]

        return ResolvedKnowledgePack(
            id=manifest.id,
            semantic_version=manifest.semantic_version,
            name=manifest.name,
            description=manifest.description,
            domain=manifest.domain,
            status=manifest.status,
            provenance=manifest.provenance,
            depends_on=list(merged_dependencies.values()),
            aliases=merged_aliases,
            entries=list(merged_entries.values()),
            inherited_from=inherited_from,
            resolved_dependencies=resolved_dependencies,
            source_path=(
                str(self._paths[pack_id]) if pack_id in self._paths else None
            ),
        )

    def _collect_resolution_errors(self, pack_id: str) -> list[str]:
        if pack_id not in self._manifests:
            return [f"unknown pack id: {pack_id!r}"]

        errors: list[str] = []
        manifest = self._manifests[pack_id]

        if manifest.inheritance is not None:
            parent_id = manifest.inheritance.id
            if parent_id not in self._manifests:
                errors.append(f"missing parent pack: {parent_id!r}")
            else:
                parent = self._manifests[parent_id]
                constraint = manifest.inheritance.version_constraint
                if constraint and not satisfies(parent.version, constraint):
                    errors.append(
                        f"parent {parent_id} version {parent.semantic_version} "
                        f"does not satisfy {constraint}",
                    )
                errors.extend(self._collect_resolution_errors(parent_id))

        for dependency in manifest.depends_on:
            if dependency.optional and dependency.id not in self._manifests:
                continue
            if dependency.id not in self._manifests:
                errors.append(f"missing dependency: {dependency.id!r}")
                continue
            target = self._manifests[dependency.id]
            if not satisfies(target.version, dependency.version_constraint):
                errors.append(
                    f"dependency {dependency.id} version "
                    f"{target.semantic_version} does not satisfy "
                    f"{dependency.version_constraint}",
                )

        return errors