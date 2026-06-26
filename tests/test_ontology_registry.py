"""Tests for the ontology entity registry."""

from __future__ import annotations

import pytest

from figure_agent.ontology import (
    Arrow,
    EntityRegistry,
    EntityType,
    Label,
    OntologyRegistryError,
    Protein,
    create_entity,
)


def test_registry_lists_builtin_entity_types() -> None:
    """Registry should expose all built-in entity types."""
    registry = EntityRegistry()
    types = registry.list_entity_types()

    assert EntityType.MOLECULE in types
    assert EntityType.PROTEIN in types
    assert EntityType.IMAGE_ASSET in types


def test_registry_entity_lookup() -> None:
    """Registered entities should be retrievable by ID."""
    registry = EntityRegistry()
    entity = create_entity(EntityType.PROTEIN, "prot-1")
    registry.add_entity(entity)

    retrieved = registry.get_entity("prot-1")

    assert retrieved.id == "prot-1"
    assert isinstance(retrieved, Protein)


def test_duplicate_entity_registration_raises() -> None:
    """Duplicate entity IDs should be rejected by the registry."""
    registry = EntityRegistry()
    registry.add_entity(Label(id="lbl-1"))

    with pytest.raises(OntologyRegistryError) as exc_info:
        registry.add_entity(Arrow(id="lbl-1"))

    assert "already registered" in str(exc_info.value)


def test_unknown_entity_reference_raises() -> None:
    """Registry reference validation should fail for unknown IDs."""
    registry = EntityRegistry()

    with pytest.raises(OntologyRegistryError) as exc_info:
        registry.validate_entity_reference("missing")

    assert "Invalid entity reference" in str(exc_info.value)


def test_get_entity_type_returns_model_class() -> None:
    """Entity type lookup should return the model class."""
    registry = EntityRegistry()
    model = registry.get_entity_type(EntityType.LABEL)

    assert model.__name__ == "Label"


def test_unknown_entity_type_lookup_raises() -> None:
    """Unknown entity types should raise registry errors."""
    registry = EntityRegistry()
    registry._entity_types.clear()

    with pytest.raises(OntologyRegistryError):
        registry.get_entity_type(EntityType.CELL)
