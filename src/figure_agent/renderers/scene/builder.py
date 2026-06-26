"""Build renderer-independent visual scenes from ontology graphs."""

from __future__ import annotations

from figure_agent.ontology.entities import BaseEntity
from figure_agent.ontology.enums import EntityType
from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers.base import RenderConfig
from figure_agent.renderers.exceptions import LayoutError
from figure_agent.renderers.geometry import Point, Rect
from figure_agent.renderers.layout import GraphLayout, compute_layout, validate_layout
from figure_agent.renderers.scene.exceptions import SceneBuildError
from figure_agent.renderers.scene.models import (
    SCENE_VERSION,
    ConnectorKind,
    LabelAnchor,
    PrimitiveKind,
    ScenePalette,
    SceneStyle,
    StyleReference,
    VisualConnector,
    VisualGroup,
    VisualLabel,
    VisualPanel,
    VisualPrimitive,
    VisualScene,
)
from figure_agent.renderers.styling import (
    DEFAULT_CORNER_RADIUS,
    DEFAULT_FONT_FAMILY,
    DEFAULT_FONT_SIZE,
    DEFAULT_PALETTE,
    DEFAULT_STROKE_WIDTH,
    MonochromePalette,
)

_SHAPE_TO_PRIMITIVE: dict[str, PrimitiveKind] = {
    "panel_boundary": PrimitiveKind.PANEL_BOUNDARY,
    "text_label": PrimitiveKind.TEXT_LABEL,
    "arrow": PrimitiveKind.ARROW,
    "rounded_rectangle": PrimitiveKind.ROUNDED_RECTANGLE,
    "rectangle": PrimitiveKind.RECTANGLE,
}


def _display_label(entity: BaseEntity) -> str:
    if entity.label:
        return entity.label
    text = getattr(entity, "text", None)
    if isinstance(text, str) and text:
        return text
    return entity.id.split(":")[-1]


def _is_panel_entity(entity: BaseEntity) -> bool:
    return ":panel:" in entity.id


def _primitive_kind(shape: str) -> PrimitiveKind:
    return _SHAPE_TO_PRIMITIVE.get(shape, PrimitiveKind.RECTANGLE)


def _scene_style_from_palette(palette: MonochromePalette) -> SceneStyle:
    return SceneStyle(
        palette=ScenePalette(
            background=palette.background,
            fill=palette.fill,
            fill_container=palette.fill_container,
            stroke=palette.stroke,
            text=palette.text,
            arrow=palette.arrow,
        ),
        stroke_width=DEFAULT_STROKE_WIDTH,
        corner_radius=DEFAULT_CORNER_RADIUS,
        font_family=DEFAULT_FONT_FAMILY,
        font_size=DEFAULT_FONT_SIZE,
    )


def _panel_title_label(entity: BaseEntity, rect: Rect) -> VisualLabel:
    return VisualLabel(
        text=_display_label(entity),
        anchor=LabelAnchor.START,
        position=Point(rect.x + 8, rect.y + 16),
    )


def _centered_label(text: str, rect: Rect) -> VisualLabel:
    return VisualLabel(
        text=text,
        anchor=LabelAnchor.MIDDLE,
        position=Point(rect.center.x, rect.center.y),
    )


def _style_reference_path(entity: BaseEntity) -> str:
    style_ref = entity.metadata.get("style_ref")
    if isinstance(style_ref, str) and style_ref:
        return style_ref
    if entity.label:
        return entity.label
    return entity.id


def _empty_scene(
    *,
    config: RenderConfig,
    palette: MonochromePalette,
) -> VisualScene:
    return VisualScene(
        version=SCENE_VERSION,
        figure_id="",
        title="",
        layout_type="unknown",
        canvas_width=config.width,
        canvas_height=config.height,
        style=_scene_style_from_palette(palette),
        panels=(),
        primitives=(),
        connectors=(),
        groups=(),
        style_references=(),
    )


def _build_scene_from_layout(
    graph: OntologyGraph,
    layout: GraphLayout,
    *,
    config: RenderConfig,
    palette: MonochromePalette,
) -> VisualScene:
    root = layout.root
    if root is None:
        return _empty_scene(config=config, palette=palette)

    figure_id = root.id.split(":")[-1]
    layout_type = str(root.metadata.get("layout_type", "unknown"))

    primitives: list[VisualPrimitive] = []
    panels: list[VisualPanel] = []
    groups: list[VisualGroup] = []

    for panel_layout in layout.panels:
        panel_entity = panel_layout.entity
        panel_id = panel_entity.id
        member_ids: list[str] = []

        boundary = VisualPrimitive(
            id=panel_id,
            kind=PrimitiveKind.PANEL_BOUNDARY,
            bounds=panel_layout.rect,
            label=_panel_title_label(panel_entity, panel_layout.rect),
            panel_id=panel_id,
            entity_type=panel_entity.entity_type,
        )
        primitives.append(boundary)
        member_ids.append(panel_id)

        for item in panel_layout.items:
            entity = item.entity
            label_text = _display_label(entity)
            centered = _centered_label(label_text, item.rect)
            primitive = VisualPrimitive(
                id=entity.id,
                kind=_primitive_kind(item.shape),
                bounds=item.rect,
                label=None if item.shape == "arrow" else centered,
                panel_id=panel_id,
                entity_type=entity.entity_type,
            )
            primitives.append(primitive)
            member_ids.append(entity.id)

        panels.append(
            VisualPanel(
                id=panel_id,
                bounds=panel_layout.rect,
                title=_panel_title_label(panel_entity, panel_layout.rect),
                primitive_ids=tuple(member_ids),
            )
        )
        groups.append(VisualGroup(id=panel_id, member_ids=tuple(member_ids)))

    connectors = [
        VisualConnector(
            id=f"arrow-{index}",
            kind=ConnectorKind.STRAIGHT,
            source_id=source_id,
            target_id=target_id,
        )
        for index, (source_id, target_id) in enumerate(layout.arrows)
    ]

    annotations = [
        entity
        for entity in graph.entities
        if entity.entity_type == EntityType.ANNOTATION and ":style:" in entity.id
    ]
    base_y = layout.canvas_size.height - config.margin - 28
    style_references: list[StyleReference] = []
    for index, entity in enumerate(annotations):
        bounds = Rect(config.margin + index * 140, base_y, 130, 24)
        path = _style_reference_path(entity)
        style_references.append(
            StyleReference(id=entity.id, path=path, bounds=bounds)
        )
        primitives.append(
            VisualPrimitive(
                id=entity.id,
                kind=PrimitiveKind.STYLE_REFERENCE,
                bounds=bounds,
                label=_centered_label(path, bounds),
                panel_id=None,
                entity_type=entity.entity_type,
            )
        )

    return VisualScene(
        version=SCENE_VERSION,
        figure_id=figure_id,
        title=_display_label(root),
        layout_type=layout_type,
        canvas_width=layout.canvas_size.width,
        canvas_height=layout.canvas_size.height,
        style=_scene_style_from_palette(palette),
        panels=tuple(panels),
        primitives=tuple(primitives),
        connectors=tuple(connectors),
        groups=tuple(groups),
        style_references=tuple(style_references),
    )


def build_visual_scene(
    graph: OntologyGraph,
    *,
    config: RenderConfig | None = None,
    palette: MonochromePalette | None = None,
) -> VisualScene:
    """Convert an ontology graph into a renderer-independent visual scene.

    Args:
        graph: Compiled ontology graph.
        config: Layout configuration.
        palette: Optional palette override for scene style tokens.

    Returns:
        ``VisualScene`` describing panels, primitives, connectors, and styling.

    Raises:
        SceneBuildError: If layout or scene assembly fails.
    """
    cfg = config or RenderConfig()
    resolved_palette = palette or DEFAULT_PALETTE

    if not graph.entities:
        return _empty_scene(config=cfg, palette=resolved_palette)

    try:
        layout = compute_layout(graph, cfg)
        validate_layout(layout)
    except LayoutError as exc:
        raise SceneBuildError(str(exc)) from exc

    return _build_scene_from_layout(
        graph,
        layout,
        config=cfg,
        palette=resolved_palette,
    )


def build_visual_scene_from_layout(
    graph: OntologyGraph,
    layout: GraphLayout,
    *,
    config: RenderConfig | None = None,
    palette: MonochromePalette | None = None,
) -> VisualScene:
    """Build a visual scene using a precomputed ``GraphLayout``.

    Primarily for tests that need to decouple layout from scene assembly.
    """
    cfg = config or RenderConfig()
    resolved_palette = palette or DEFAULT_PALETTE

    if not graph.entities:
        return _empty_scene(config=cfg, palette=resolved_palette)

    try:
        validate_layout(layout)
    except LayoutError as exc:
        raise SceneBuildError(str(exc)) from exc

    return _build_scene_from_layout(
        graph,
        layout,
        config=cfg,
        palette=resolved_palette,
    )