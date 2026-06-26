"""Tests for the knowledge pack framework."""

from __future__ import annotations

from pathlib import Path

import pytest

from figure_agent.knowledge import (
    KnowledgePackRegistry,
    KnowledgePackResolutionError,
    KnowledgePackSchemaError,
    KnowledgePackValidationError,
    KnowledgePackValidator,
    SemanticVersion,
    discover_pack_directories,
    load_pack_directory,
    parse_pack_manifest,
    satisfies,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_ROOT = REPO_ROOT / "knowledge"
FIXTURES_ROOT = REPO_ROOT / "tests" / "fixtures" / "knowledge_packs"


def test_semantic_version_parsing_and_constraints() -> None:
    """Semantic versions and constraints should parse predictably."""
    version = SemanticVersion.parse("1.2.3")
    assert str(version) == "1.2.3"
    assert satisfies(version, "^1.2.0")
    assert satisfies(version, ">=1.0.0,<2.0.0")
    assert not satisfies(version, "<1.0.0")


def test_discover_repository_knowledge_packs() -> None:
    """Repository knowledge directories should expose pack.yaml manifests."""
    directories = discover_pack_directories(KNOWLEDGE_ROOT)
    names = {path.name for path in directories}
    assert "GeneralDesign" in names
    assert "MedicinalChemistry" in names
    assert len(directories) >= 5


def test_load_repository_pack_scaffolds_without_entries() -> None:
    """Skeleton packs should load and contain no curated entries."""
    manifest = load_pack_directory(KNOWLEDGE_ROOT / "GeneralDesign")
    assert manifest.id == "general-design"
    assert manifest.entries == []
    assert manifest.semantic_version == "0.1.0"
    assert manifest.provenance.maintainer == "platform"


def test_domain_pack_declares_dependency_on_general_design() -> None:
    """Domain packs should depend on the general-design base pack."""
    manifest = load_pack_directory(KNOWLEDGE_ROOT / "MedicinalChemistry")
    assert manifest.extends == "general-design"
    assert manifest.depends_on
    assert manifest.depends_on[0].id == "general-design"


def test_registry_loads_repository_root() -> None:
    """Registry should load and validate all repository packs."""
    registry = KnowledgePackRegistry()
    loaded = registry.load_root(KNOWLEDGE_ROOT)
    assert len(loaded) >= 5
    registry.validate()
    assert "general-design" in registry.pack_ids
    assert "medicinal-chemistry" in registry.pack_ids


def test_inheritance_merges_entries_aliases_and_dependencies() -> None:
    """Derived packs should overlay parent content."""
    registry = KnowledgePackRegistry()
    registry.load_directory(FIXTURES_ROOT / "base")
    registry.load_directory(FIXTURES_ROOT / "derived")
    registry.validate()

    resolved = registry.resolve("derived")
    assert resolved.inherited_from == ["base"]
    entry_ids = {entry.id for entry in resolved.entries}
    assert entry_ids == {"conv-base", "conv-derived"}

    overridden = next(entry for entry in resolved.entries if entry.id == "conv-base")
    assert overridden.title == "Overridden base convention"
    assert resolved.aliases["panel"] == ["zone", "region"]
    assert resolved.aliases["content_slot"] == ["slot"]


def test_alias_resolution_returns_canonical_term() -> None:
    """Alias resolver should map synonyms to canonical terms."""
    registry = KnowledgePackRegistry()
    registry.load_directory(FIXTURES_ROOT / "base")
    registry.load_directory(FIXTURES_ROOT / "derived")

    assert registry.resolve_alias("derived", "zone") == "panel"
    assert registry.resolve_alias("derived", "slot") == "content_slot"


def test_optional_dependency_allows_missing_pack() -> None:
    """Optional dependencies should not fail when target pack is absent."""
    registry = KnowledgePackRegistry()
    registry.load_directory(FIXTURES_ROOT / "optional_dep")
    registry.validate()
    resolved = registry.resolve("optional-dep")
    assert resolved.resolved_dependencies == []


def test_missing_required_dependency_fails_validation() -> None:
    """Required dependencies must be present in the registry."""
    registry = KnowledgePackRegistry()
    manifest = load_pack_directory(FIXTURES_ROOT / "derived")
    registry.register(manifest)
    with pytest.raises(KnowledgePackValidationError):
        registry.validate()


def test_inheritance_cycle_is_rejected() -> None:
    """Circular inheritance should fail registry validation."""
    registry = KnowledgePackRegistry()
    base = load_pack_directory(FIXTURES_ROOT / "base").model_copy(
        update={"extends": "derived"},
    )
    derived = load_pack_directory(FIXTURES_ROOT / "derived")
    registry.register(base)
    registry.register(derived)

    errors = KnowledgePackValidator().collect_registry_errors(registry._manifests)
    assert any("cycle" in error for error in errors)


def test_invalid_manifest_rejected_by_schema() -> None:
    """Invalid manifests should raise schema errors."""
    with pytest.raises(KnowledgePackSchemaError):
        parse_pack_manifest(
            {
                "pack_format_version": "9.9.9",
                "id": "bad",
                "semantic_version": "1.0.0",
                "name": "Bad",
                "domain": "test",
                "provenance": {
                    "maintainer": "test",
                    "created_at": "2026-01-01",
                    "updated_at": "2026-01-01",
                },
            }
        )


def test_duplicate_entry_ids_rejected() -> None:
    """Duplicate entry ids within a pack should fail schema validation."""
    base = load_pack_directory(FIXTURES_ROOT / "base")
    payload = base.model_dump(mode="json")
    payload["entries"].append(payload["entries"][0])
    with pytest.raises(KnowledgePackSchemaError):
        parse_pack_manifest(payload)


def test_unknown_pack_resolution_raises() -> None:
    """Resolving unknown pack ids should raise resolution errors."""
    registry = KnowledgePackRegistry()
    with pytest.raises(KnowledgePackResolutionError):
        registry.resolve("missing-pack")


def test_version_mismatch_on_parent_constraint_fails() -> None:
    """Child packs must satisfy parent version constraints."""
    registry = KnowledgePackRegistry()
    base = load_pack_directory(FIXTURES_ROOT / "base").model_copy(
        update={"semantic_version": "2.0.0"},
    )
    derived = load_pack_directory(FIXTURES_ROOT / "derived")
    registry.register(base)
    registry.register(derived)

    with pytest.raises(KnowledgePackValidationError):
        registry.validate()