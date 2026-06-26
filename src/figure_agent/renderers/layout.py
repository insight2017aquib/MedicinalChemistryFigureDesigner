"""Simple automatic layout for ontology graphs."""

from __future__ import annotations

from dataclasses import dataclass, field

from figure_agent.ontology.entities import BaseEntity
from figure_agent.ontology.enums import EntityType, RelationshipType
from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers.base import RenderConfig
from figure_agent.renderers.exceptions import LayoutError
from figure_agent.renderers.geometry import Point, Rect, Size, stack_rects


@dataclass
class LayoutItem:
    """A positioned ontology entity."""

    entity: BaseEntity
    rect: Rect
    shape: str


@dataclass
class PanelLayout:
    """Layout for a panel and its child objects."""

    entity: BaseEntity
    rect: Rect
    items: list[LayoutItem] = field(default_factory=list)


@dataclass
class GraphLayout:
    """Complete layout for an ontology graph."""

    root: BaseEntity | None
    canvas_size: Size
    panels: list[PanelLayout] = field(default_factory=list)
    arrows: list[tuple[str, str]] = field(default_factory=list)


def _contains_children(graph: OntologyGraph, parent_id: str) -> list[str]:
    return [
        rel.target_id
        for rel in graph.relationships
        if rel.type == RelationshipType.CONTAINS and rel.source_id == parent_id
    ]


def _entity_by_id(graph: OntologyGraph) -> dict[str, BaseEntity]:
    return {entity.id: entity for entity in graph.entities}


def _is_panel(entity: BaseEntity) -> bool:
    return ":panel:" in entity.id


def _is_figure_root(entity: BaseEntity) -> bool:
    return ":figure:" in entity.id


def _shape_for_entity(entity: BaseEntity) -> str:
    if _is_panel(entity) or entity.entity_type == EntityType.CELL:
        return "panel_boundary"
    if entity.entity_type == EntityType.LABEL:
        return "text_label"
    if entity.entity_type == EntityType.ARROW:
        return "arrow"
    if entity.entity_type in {EntityType.ANNOTATION, EntityType.SHAPE}:
        return "rounded_rectangle"
    return "rectangle"


def compute_layout(graph: OntologyGraph, config: RenderConfig) -> GraphLayout:
    """Compute a simple stacked layout for panels and contained objects."""
    entities = _entity_by_id(graph)
    if not entities:
        return GraphLayout(root=None, canvas_size=Size(config.width, config.height))

    root = next((e for e in graph.entities if _is_figure_root(e)), None)
    if root is None:
        root = graph.entities[0]

    panel_entities = [
        entities[child_id]
        for child_id in _contains_children(graph, root.id)
        if child_id in entities and _is_panel(entities[child_id])
    ]

    item_size = Size(config.item_width, config.item_height)
    panels: list[PanelLayout] = []
    current_x = config.margin

    for panel in panel_entities:
        child_ids = [
            cid
            for cid in _contains_children(graph, panel.id)
            if cid in entities and not _is_panel(entities[cid])
        ]
        child_entities = [entities[cid] for cid in child_ids]

        stack_count = max(len(child_entities), 1)
        content_height = (
            stack_count * item_size.height
            + max(stack_count - 1, 0) * config.item_spacing
        )
        panel_height = content_height + 2 * config.panel_padding + 24
        panel_width = item_size.width + 2 * config.panel_padding

        panel_rect = Rect(current_x, config.margin, panel_width, panel_height)
        item_origin = Point(
            current_x + config.panel_padding,
            config.margin + config.panel_padding + 20,
        )
        item_rects = stack_rects(
            item_origin,
            item_size,
            len(child_entities),
            spacing=config.item_spacing,
        )

        items = [
            LayoutItem(
                entity=entity,
                rect=rect,
                shape=_shape_for_entity(entity),
            )
            for entity, rect in zip(child_entities, item_rects, strict=False)
        ]

        panels.append(PanelLayout(entity=panel, rect=panel_rect, items=items))
        current_x += panel_width + config.panel_gap

    if not panels:
        panels.append(
            PanelLayout(
                entity=root,
                rect=Rect(
                    config.margin, config.margin, config.item_width, config.item_height
                ),
                items=[],
            )
        )

    max_panel_bottom = max(panel.rect.y + panel.rect.height for panel in panels)
    canvas_width = max(current_x, config.width)
    canvas_height = max(max_panel_bottom + config.margin, config.height)

    has_style_annotations = any(
        entity.entity_type == EntityType.ANNOTATION and ":style:" in entity.id
        for entity in graph.entities
    )
    if has_style_annotations:
        canvas_height += 40

    arrows: list[tuple[str, str]] = []
    for rel in graph.relationships:
        if rel.type in {
            RelationshipType.CONNECTED_TO,
            RelationshipType.INTERACTS_WITH,
        }:
            arrows.append((rel.source_id, rel.target_id))

    for entity in graph.entities:
        if (
            entity.entity_type == EntityType.ARROW
            and len(panels) == 1
            and panels[0].items
        ):
            target = panels[0].items[-1].entity.id
            arrows.append((entity.id, target))

    return GraphLayout(
        root=root,
        canvas_size=Size(canvas_width, canvas_height),
        panels=panels,
        arrows=arrows,
    )


def resolve_item_rects(layout: GraphLayout) -> dict[str, Rect]:
    """Map entity IDs to their computed layout rectangles."""
    mapping: dict[str, Rect] = {}
    for panel in layout.panels:
        mapping[panel.entity.id] = panel.rect
        for item in panel.items:
            mapping[item.entity.id] = item.rect
    return mapping


def validate_layout(layout: GraphLayout) -> None:
    """Raise if the layout is empty or invalid."""
    if layout.root is None and not layout.panels:
        raise LayoutError("Cannot layout an empty ontology graph")
