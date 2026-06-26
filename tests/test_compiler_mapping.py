"""Tests for FSL-to-ontology mapping helpers."""

from __future__ import annotations

from figure_agent.compiler.context import CompilationContext
from figure_agent.compiler.mapping import (
    map_content_slot,
    map_figure_root,
    map_panel,
    resolve_slot_entity_type,
)
from figure_agent.fsl.models import ContentSlot
from figure_agent.ontology.enums import EntityType
from figure_agent.ontology import Label
from helpers import valid_document
from figure_agent.fsl.models import Figure


def _figure() -> Figure:
    from figure_agent.fsl.parser import parse

    return parse(valid_document())


def test_resolve_placeholder_slot_type() -> None:
    """Placeholder slots should map to label entities."""
    slot = ContentSlot(id="slot-1", type="placeholder")
    assert resolve_slot_entity_type(slot) == EntityType.LABEL


def test_resolve_unknown_slot_type_defaults_to_shape() -> None:
    """Unknown slot types should fall back to shape entities."""
    slot = ContentSlot(id="slot-1", type="unknown-type")
    assert resolve_slot_entity_type(slot) == EntityType.SHAPE


def test_map_content_slot_creates_label() -> None:
    """Placeholder content slots should instantiate Label entities."""
    figure = _figure()
    context = CompilationContext(figure=figure)
    slot = figure.content_slots[0]

    entity = map_content_slot(slot, context)

    assert isinstance(entity, Label)
    assert entity.id == "fig-001:slot:slot-1"
    assert context.get_entity_id("slot", "slot-1") == entity.id


def test_map_panel_creates_cell_with_zones() -> None:
    """Panels should map to cell entities with zone metadata."""
    figure = _figure()
    context = CompilationContext(figure=figure)
    panel = figure.layout.panels[0]

    entity = map_panel(panel, figure, context)

    assert entity.metadata["zones"] == ["primary"]
    assert entity.metadata["layout_type"] == "single-panel"


def test_map_figure_root_registers_figure_mapping() -> None:
    """Figure root mapping should register the figure metadata identifier."""
    figure = _figure()
    context = CompilationContext(figure=figure)

    root = map_figure_root(figure, context)

    assert root.id == "fig-001:figure:fig-001"
    assert context.get_entity_id("figure", "fig-001") == root.id
