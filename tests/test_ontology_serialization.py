"""Tests for ontology graph serialization."""

from __future__ import annotations

import json

import yaml

from figure_agent.ontology import (
    Cell,
    EntityRegistry,
    Label,
    OntologyValidator,
    Relationship,
    RelationshipType,
    graph_from_dict,
    graph_to_dict,
    graph_to_json,
    graph_to_yaml,
)


def _build_registry() -> EntityRegistry:
    registry = EntityRegistry()
    registry.add_entity(Cell(id="cell-1", label="Container"))
    registry.add_entity(Label(id="lbl-1", text="Placeholder"))
    registry.add_relationship(
        Relationship(
            id="rel-1",
            type=RelationshipType.LOCATED_IN,
            source_id="lbl-1",
            target_id="cell-1",
        )
    )
    return registry


def test_graph_to_dict_contains_entities_and_relationships() -> None:
    """Serialized dicts should include entities and relationships."""
    graph = _build_registry().build_graph()
    data = graph_to_dict(graph)

    assert data["ontology_version"] == "0.4.0"
    assert len(data["entities"]) == 2
    assert len(data["relationships"]) == 1


def test_json_round_trip_preserves_structure() -> None:
    """JSON serialization should round-trip without semantic loss."""
    original = _build_registry().build_graph()
    restored = graph_from_dict(json.loads(graph_to_json(original)))

    OntologyValidator().validate(restored)
    assert graph_to_dict(original) == graph_to_dict(restored)


def test_yaml_round_trip_preserves_structure() -> None:
    """YAML serialization should round-trip without semantic loss."""
    original = _build_registry().build_graph()
    restored = graph_from_dict(yaml.safe_load(graph_to_yaml(original)))

    OntologyValidator().validate(restored)
    assert graph_to_dict(original) == graph_to_dict(restored)


def test_registry_load_graph_round_trip() -> None:
    """Registry should rebuild an equivalent graph after load."""
    registry = _build_registry()
    original = registry.build_graph()

    new_registry = EntityRegistry()
    new_registry.load_graph(original)
    restored = new_registry.build_graph()

    assert graph_to_dict(original) == graph_to_dict(restored)
