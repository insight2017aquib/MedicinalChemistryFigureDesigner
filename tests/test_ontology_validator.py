"""Tests for ontology structural validation."""

from __future__ import annotations

import pytest

from figure_agent.ontology import (
    Cell,
    Label,
    OntologyGraph,
    OntologyValidationError,
    OntologyValidator,
    Relationship,
    RelationshipType,
)


def test_valid_graph_passes_validation() -> None:
    """A structurally valid graph should pass validation."""
    graph = OntologyGraph(
        entities=[
            Cell(id="cell-1"),
            Label(id="lbl-1"),
        ],
        relationships=[
            Relationship(
                id="rel-1",
                type=RelationshipType.CONNECTED_TO,
                source_id="cell-1",
                target_id="lbl-1",
            )
        ],
    )

    OntologyValidator().validate(graph)


def test_duplicate_entity_id_raises_validation_error() -> None:
    """Duplicate entity IDs should fail validation."""
    graph = OntologyGraph(
        entities=[
            Cell(id="dup"),
            Label(id="dup"),
        ],
        relationships=[],
    )

    with pytest.raises(OntologyValidationError) as exc_info:
        OntologyValidator().validate(graph)

    assert "duplicate entity id 'dup'" in str(exc_info.value)


def test_duplicate_relationship_id_raises_validation_error() -> None:
    """Duplicate relationship IDs should fail validation."""
    graph = OntologyGraph(
        entities=[Cell(id="cell-1"), Label(id="lbl-1")],
        relationships=[
            Relationship(
                id="dup",
                type=RelationshipType.REFERENCES,
                source_id="cell-1",
                target_id="lbl-1",
            ),
            Relationship(
                id="dup",
                type=RelationshipType.ANNOTATES,
                source_id="lbl-1",
                target_id="cell-1",
            ),
        ],
    )

    with pytest.raises(OntologyValidationError) as exc_info:
        OntologyValidator().validate(graph)

    assert "duplicate relationship id 'dup'" in str(exc_info.value)


def test_disallowed_relationship_type_raises_validation_error() -> None:
    """Relationship types outside the allowed set should fail validation."""
    graph = OntologyGraph(
        entities=[Cell(id="cell-1"), Label(id="lbl-1")],
        relationships=[
            Relationship(
                id="rel-1",
                type=RelationshipType.INTERACTS_WITH,
                source_id="cell-1",
                target_id="lbl-1",
            )
        ],
    )

    allowed = {RelationshipType.CONTAINS}
    with pytest.raises(OntologyValidationError) as exc_info:
        OntologyValidator(known_relationship_types=allowed).validate(graph)

    assert "invalid type" in str(exc_info.value)
