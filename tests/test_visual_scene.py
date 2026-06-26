"""Tests for the renderer-independent visual scene layer."""

from __future__ import annotations

from pathlib import Path

import pytest

from figure_agent import compile_figure, load_yaml, parse
from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers import build_visual_scene
from figure_agent.renderers.scene.exceptions import SceneBuildError
from figure_agent.renderers.scene.models import (
    ConnectorKind,
    PrimitiveKind,
    SCENE_VERSION,
)
from helpers import valid_document

REPO_ROOT = Path(__file__).resolve().parents[1]
MINIMAL_FIGURE = REPO_ROOT / "examples" / "minimal_figure.yaml"


def _compiled_graph():
    figure = parse(load_yaml(MINIMAL_FIGURE))
    return compile_figure(figure)


def test_build_visual_scene_returns_scene_model() -> None:
    """Scene builder should produce a versioned visual scene."""
    scene = build_visual_scene(_compiled_graph())

    assert scene.version == SCENE_VERSION
    assert scene.figure_id == "fig-001"
    assert scene.title == "Placeholder Figure"
    assert scene.layout_type == "single-panel"
    assert scene.canvas_width > 0
    assert scene.canvas_height > 0


def test_scene_contains_panel_primitives_and_groups() -> None:
    """Panels should include boundaries and grouped child primitives."""
    scene = build_visual_scene(_compiled_graph())
    primitive_by_id = scene.primitive_by_id()

    assert len(scene.panels) == 1
    panel = scene.panels[0]
    assert ":panel:" in panel.id
    assert panel.id in primitive_by_id
    assert primitive_by_id[panel.id].kind == PrimitiveKind.PANEL_BOUNDARY

    child_ids = [member_id for member_id in panel.primitive_ids if member_id != panel.id]
    assert len(child_ids) == 1
    assert primitive_by_id[child_ids[0]].kind == PrimitiveKind.TEXT_LABEL
    assert len(scene.groups) == 1
    assert scene.groups[0].member_ids == panel.primitive_ids


def test_scene_includes_style_references() -> None:
    """Style annotation entities should appear as style references."""
    scene = build_visual_scene(_compiled_graph())

    assert len(scene.style_references) == 1
    assert scene.style_references[0].path == "styles/color-system.md"
    style_primitive = scene.primitive_by_id()[scene.style_references[0].id]
    assert style_primitive.kind == PrimitiveKind.STYLE_REFERENCE


def test_empty_graph_returns_minimal_scene() -> None:
    """Empty graphs should produce a canvas-only scene without raising."""
    scene = build_visual_scene(OntologyGraph())

    assert scene.panels == ()
    assert scene.primitives == ()
    assert scene.connectors == ()
    assert scene.canvas_width > 0
    assert scene.canvas_height > 0


def test_multi_panel_scene_has_sorted_panel_ids() -> None:
    """Multi-panel graphs should expose both panel regions."""
    document = valid_document()
    document["layout"]["type"] = "multi-panel"
    document["layout"]["panels"] = [
        {"id": "panel-b", "zones": ["right"], "object_refs": ["slot-2"]},
        {"id": "panel-a", "zones": ["left"], "object_refs": ["slot-1"]},
    ]
    document["content_slots"].append(
        {"id": "slot-2", "label": "Secondary", "type": "shape", "value": None}
    )

    graph = compile_figure(parse(document))
    scene = build_visual_scene(graph)
    panel_ids = [panel.id for panel in scene.panels]

    assert len(panel_ids) == 2
    assert any("panel-a" in panel_id for panel_id in panel_ids)
    assert any("panel-b" in panel_id for panel_id in panel_ids)


def test_arrow_slot_maps_to_arrow_primitive() -> None:
    """Arrow slots should become arrow primitives without labels."""
    document = valid_document()
    document["content_slots"][0]["type"] = "arrow"
    document["content_slots"][0]["label"] = "Connection"

    graph = compile_figure(parse(document))
    scene = build_visual_scene(graph)
    child_primitives = [
        primitive
        for primitive in scene.primitives
        if primitive.kind == PrimitiveKind.ARROW
    ]

    assert len(child_primitives) == 1
    assert child_primitives[0].label is None


def test_connectors_use_straight_kind() -> None:
    """Relationship arrows should appear as straight connectors."""
    document = valid_document()
    document["content_slots"][0]["type"] = "arrow"

    graph = compile_figure(parse(document))
    scene = build_visual_scene(graph)

    assert scene.connectors
    assert all(connector.kind == ConnectorKind.STRAIGHT for connector in scene.connectors)