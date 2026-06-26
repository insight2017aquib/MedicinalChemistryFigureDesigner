"""Tests for ontology entity models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from figure_agent.ontology import (
    Arrow,
    Cell,
    EntityType,
    Label,
    Ligand,
    Molecule,
    Protein,
    create_entity,
)


def test_create_molecule_entity() -> None:
    """Molecule entities should instantiate with required fields."""
    entity = create_entity(EntityType.MOLECULE, "mol-1", label="Placeholder")

    assert entity.id == "mol-1"
    assert entity.entity_type == EntityType.MOLECULE
    assert entity.label == "Placeholder"


def test_protein_inherits_from_macromolecule() -> None:
    """Protein should be a structural/macromolecular entity subtype."""
    entity = Protein(id="prot-1")

    assert isinstance(entity, Protein)
    assert entity.entity_type == EntityType.PROTEIN


def test_ligand_inherits_from_molecule() -> None:
    """Ligand should inherit from the molecule entity branch."""
    entity = Ligand(id="lig-1")

    assert isinstance(entity, Ligand)
    assert entity.entity_type == EntityType.LIGAND


def test_graphical_entities_support_optional_fields() -> None:
    """Graphical entities should accept optional display fields."""
    label = Label(id="lbl-1", text="Placeholder")
    arrow = Arrow(id="arr-1")

    assert label.text == "Placeholder"
    assert arrow.entity_type == EntityType.ARROW


def test_cell_entity_creation() -> None:
    """Cell entities should be creatable without scientific metadata."""
    entity = Cell(id="cell-1", label="Container")

    assert entity.entity_type == EntityType.CELL
    assert entity.label == "Container"


def test_entity_requires_non_empty_id() -> None:
    """Entity IDs must be non-empty strings."""
    with pytest.raises(ValidationError):
        Molecule(id="")
