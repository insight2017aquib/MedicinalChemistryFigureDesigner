"""Tests for renderer layout computation."""

from __future__ import annotations

from figure_agent import compile_figure, parse
from figure_agent.renderers.base import RenderConfig
from figure_agent.renderers.layout import compute_layout, resolve_item_rects
from helpers import valid_document


def test_layout_positions_panel_items_vertically() -> None:
    """Panel children should be stacked vertically."""
    figure = parse(valid_document())
    graph = compile_figure(figure)
    layout = compute_layout(graph, RenderConfig())

    assert len(layout.panels) == 1
    panel = layout.panels[0]
    assert len(panel.items) == 1
    assert panel.items[0].rect.y < panel.rect.y + panel.rect.height


def test_multi_panel_layout_has_multiple_panels() -> None:
    """Multi-panel graphs should produce multiple panel layouts."""
    document = valid_document()
    document["layout"]["type"] = "multi-panel"
    document["layout"]["panels"] = [
        {"id": "panel-a", "zones": ["left"], "object_refs": ["slot-1"]},
        {
            "id": "panel-b",
            "zones": ["right"],
            "object_refs": ["slot-2"],
        },
    ]
    document["content_slots"].append(
        {
            "id": "slot-2",
            "label": "Secondary",
            "type": "shape",
            "value": None,
        }
    )

    graph = compile_figure(parse(document))
    layout = compute_layout(graph, RenderConfig())

    assert len(layout.panels) == 2
    assert layout.panels[0].rect.x < layout.panels[1].rect.x


def test_empty_graph_layout() -> None:
    """Empty graphs should return a minimal canvas layout."""
    from figure_agent.ontology.relationships import OntologyGraph

    layout = compute_layout(OntologyGraph(), RenderConfig())

    assert layout.root is None
    assert layout.panels == []
    assert layout.canvas_size.width == RenderConfig().width


def test_resolve_item_rects_maps_entity_ids() -> None:
    """Resolved item rectangles should be keyed by entity ID."""
    figure = parse(valid_document())
    graph = compile_figure(figure)
    layout = compute_layout(graph, RenderConfig())
    rects = resolve_item_rects(layout)

    assert layout.panels[0].entity.id in rects
    assert layout.panels[0].items[0].entity.id in rects
