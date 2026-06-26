"""Tests for ontology relationships and graph containers."""

from __future__ import annotations

import pytest

from figure_agent.ontology import (
    Cell,
    EntityRegistry,
    Label,
    OntologyGraph,
    OntologyValidationError,
    OntologyValidator,
    Relationship,
    RelationshipType,
)


def _sample_graph() -> OntologyGraph:
    return OntologyGraph(
        entities=[
            Cell(id="cell-1", label="Container"),
            Label(id="lbl-1", text="Placeholder"),
        ],
        relationships=[
            Relationship(
                id="rel-1",
                type=RelationshipType.CONTAINS,
                source_id="cell-1",
                target_id="lbl-1",
            )
        ],
    )


def test_relationship_links_entities() -> None:
    """Relationships should connect source and target entity IDs."""
    graph = _sample_graph()

    assert len(graph.relationships) == 1
    assert graph.relationships[0].type == RelationshipType.CONTAINS


def test_registry_builds_graph_from_entities() -> None:
    """Registry should assemble a graph from registered entities."""
    registry = EntityRegistry()
    registry.add_entity(Cell(id="cell-1"))
    registry.add_entity(Label(id="lbl-1"))
    registry.add_relationship(
        Relationship(
            id="rel-1",
            type=RelationshipType.ANNOTATES,
            source_id="lbl-1",
            target_id="cell-1",
        )
    )

    graph = registry.build_graph()

    assert len(graph.entities) == 2
    assert len(graph.relationships) == 1


def test_missing_reference_raises_validation_error() -> None:
    """Relationships referencing unknown entities should fail validation."""
    graph = OntologyGraph(
        entities=[Cell(id="cell-1")],
        relationships=[
            Relationship(
                id="rel-1",
                type=RelationshipType.REFERENCES,
                source_id="cell-1",
                target_id="missing-entity",
            )
        ],
    )

    with pytest.raises(OntologyValidationError) as exc_info:
        OntologyValidator().validate(graph)

    assert "unknown target entity 'missing-entity'" in str(exc_info.value)


def test_cyclic_parent_relationship_raises_validation_error() -> None:
    """Cyclic hierarchical relationships should fail validation."""
    graph = OntologyGraph(
        entities=[
            Cell(id="entity-a"),
            Cell(id="entity-b"),
        ],
        relationships=[
            Relationship(
                id="rel-1",
                type=RelationshipType.CONTAINS,
                source_id="entity-a",
                target_id="entity-b",
            ),
            Relationship(
                id="rel-2",
                type=RelationshipType.CONTAINS,
                source_id="entity-b",
                target_id="entity-a",
            ),
        ],
    )

    with pytest.raises(OntologyValidationError) as exc_info:
        OntologyValidator().validate(graph)

    assert "cyclic parent relationship" in str(exc_info.value)
