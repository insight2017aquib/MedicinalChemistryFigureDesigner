"""Tests for SVG renderer output."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from figure_agent import compile_figure, load_yaml, parse
from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers import SVGRenderer
from figure_agent.renderers.base import RenderConfig
from helpers import valid_document

REPO_ROOT = Path(__file__).resolve().parents[1]
MINIMAL_FIGURE = REPO_ROOT / "examples" / "minimal_figure.yaml"


def _parse_svg(content: str) -> ET.Element:
    return ET.fromstring(content)


def test_svg_generation_contains_core_elements() -> None:
    """SVG output should include panel, label box, and grouped elements."""
    figure = parse(load_yaml(MINIMAL_FIGURE))
    graph = compile_figure(figure)
    result = SVGRenderer().render(graph)
    root = _parse_svg(result.content)

    assert root.tag.endswith("svg")
    assert root.get("width")
    assert root.get("height")
    assert root.find(".//*[@id='canvas-background']") is not None

    groups = [elem for elem in root.iter() if elem.tag.endswith("g")]
    assert groups
    text_nodes = [elem for elem in root.iter() if elem.tag.endswith("text")]
    assert text_nodes
    rect_nodes = [elem for elem in root.iter() if elem.tag.endswith("rect")]
    assert len(rect_nodes) >= 2


def test_svg_label_placement_is_centered() -> None:
    """Label text nodes should use centered text anchors."""
    figure = parse(valid_document())
    graph = compile_figure(figure)
    result = SVGRenderer().render(graph)
    root = _parse_svg(result.content)

    centered = [
        elem
        for elem in root.iter()
        if elem.tag.endswith("text") and elem.get("text-anchor") == "middle"
    ]
    assert centered


def test_svg_arrow_placement_for_arrow_entity() -> None:
    """Arrow entities should produce arrow line and head primitives."""
    document = valid_document()
    document["content_slots"][0]["type"] = "arrow"

    graph = compile_figure(parse(document))
    result = SVGRenderer().render(graph)
    root = _parse_svg(result.content)

    lines = [elem for elem in root.iter() if elem.tag.endswith("line")]
    polygons = [elem for elem in root.iter() if elem.tag.endswith("polygon")]
    assert lines
    assert polygons


def test_empty_graph_renders_minimal_svg() -> None:
    """Empty graphs should still produce a valid SVG canvas."""
    result = SVGRenderer().render(OntologyGraph())
    root = _parse_svg(result.content)

    assert root.tag.endswith("svg")
    assert float(root.get("width", "0")) > 0


def test_multi_panel_graph_renders_multiple_panel_groups() -> None:
    """Multi-panel graphs should render multiple panel groups."""
    document = valid_document()
    document["layout"]["type"] = "multi-panel"
    document["layout"]["panels"] = [
        {"id": "panel-a", "zones": ["left"], "object_refs": ["slot-1"]},
        {"id": "panel-b", "zones": ["right"], "object_refs": ["slot-2"]},
    ]
    document["content_slots"].append(
        {"id": "slot-2", "label": "Secondary", "type": "shape", "value": None}
    )

    graph = compile_figure(parse(document))
    result = SVGRenderer().render(graph)
    root = _parse_svg(result.content)

    panel_groups = [
        elem
        for elem in root.iter()
        if elem.tag.endswith("g")
        and ("panel-a" in (elem.get("id") or "") or "panel-b" in (elem.get("id") or ""))
    ]
    assert len(panel_groups) == 2


def test_render_config_width_and_height() -> None:
    """Renderer should honor configured canvas dimensions."""
    figure = parse(valid_document())
    graph = compile_figure(figure)
    result = SVGRenderer().render(graph, config=RenderConfig(width=900, height=700))

    assert result.width >= 900
    assert result.height >= 700
