"""Minimal SVG renderer for ontology graphs."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from figure_agent.ontology.entities import BaseEntity
from figure_agent.ontology.enums import EntityType
from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers.base import RenderConfig, RenderResult, Renderer
from figure_agent.renderers.exceptions import SVGRenderError
from figure_agent.renderers.geometry import (
    ArrowSegment,
    Point,
    Rect,
    center_text_position,
)
from figure_agent.renderers.layout import (
    GraphLayout,
    LayoutItem,
    compute_layout,
    resolve_item_rects,
)
from figure_agent.renderers.styling import (
    DEFAULT_CORNER_RADIUS,
    DEFAULT_FONT_FAMILY,
    DEFAULT_FONT_SIZE,
    DEFAULT_PALETTE,
    DEFAULT_STROKE_WIDTH,
    MonochromePalette,
)

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def _sanitize_id(value: str) -> str:
    return value.replace(":", "-").replace(" ", "-").replace("/", "-")


def _sub(parent: ET.Element, tag: str, **attrs: str | float) -> ET.Element:
    element = ET.SubElement(parent, tag)
    for key, value in attrs.items():
        element.set(key.replace("_", "-"), str(value))
    return element


def _display_label(entity: BaseEntity) -> str:
    if entity.label:
        return entity.label
    text = getattr(entity, "text", None)
    if isinstance(text, str) and text:
        return text
    return entity.id.split(":")[-1]


class SVGRenderer(Renderer):
    """Proof-of-concept renderer that outputs simple monochrome SVG."""

    def __init__(self, *, palette: MonochromePalette | None = None) -> None:
        self._palette = palette or DEFAULT_PALETTE

    def render(
        self,
        graph: OntologyGraph,
        *,
        config: RenderConfig | None = None,
    ) -> RenderResult:
        """Render an ontology graph to SVG."""
        cfg = config or RenderConfig()
        try:
            layout = compute_layout(graph, cfg)
            svg_root = self._build_svg(layout, graph, cfg)
            content = ET.tostring(svg_root, encoding="unicode")
            return RenderResult(
                content=content,
                width=layout.canvas_size.width,
                height=layout.canvas_size.height,
                mime_type="image/svg+xml",
            )
        except Exception as exc:
            if exc.__class__.__module__.startswith("figure_agent.renderers"):
                raise
            raise SVGRenderError(f"Failed to render SVG: {exc}") from exc

    def _build_svg(
        self,
        layout: GraphLayout,
        graph: OntologyGraph,
        config: RenderConfig,
    ) -> ET.Element:
        svg = ET.Element(
            "svg",
            {
                "xmlns": SVG_NS,
                "width": str(layout.canvas_size.width),
                "height": str(layout.canvas_size.height),
                "viewBox": f"0 0 {layout.canvas_size.width} {layout.canvas_size.height}",
            },
        )

        _sub(
            svg,
            "rect",
            id="canvas-background",
            x=0,
            y=0,
            width=layout.canvas_size.width,
            height=layout.canvas_size.height,
            fill=self._palette.background,
            stroke="none",
        )

        rects = resolve_item_rects(layout)
        for panel in layout.panels:
            panel_group = ET.SubElement(svg, "g", id=_sanitize_id(panel.entity.id))
            self._draw_panel_boundary(panel_group, panel.entity, panel.rect)

            for item in panel.items:
                item_group = ET.SubElement(
                    panel_group,
                    "g",
                    id=_sanitize_id(item.entity.id),
                )
                self._draw_item(item_group, item)

        arrow_group = ET.SubElement(svg, "g", id="arrows")
        for index, (source_id, target_id) in enumerate(layout.arrows):
            if source_id not in rects or target_id not in rects:
                continue
            self._draw_arrow(
                arrow_group,
                rects[source_id],
                rects[target_id],
                arrow_id=f"arrow-{index}",
            )

        self._draw_style_annotations(svg, graph, layout, config.margin)
        return svg

    def _draw_panel_boundary(
        self,
        parent: ET.Element,
        entity: BaseEntity,
        rect: Rect,
    ) -> None:
        _sub(
            parent,
            "rect",
            x=rect.x,
            y=rect.y,
            width=rect.width,
            height=rect.height,
            rx=DEFAULT_CORNER_RADIUS,
            ry=DEFAULT_CORNER_RADIUS,
            fill=self._palette.fill_container,
            stroke=self._palette.stroke,
            stroke_width=DEFAULT_STROKE_WIDTH,
        )
        title = _display_label(entity)
        _sub(
            parent,
            "text",
            x=rect.x + 8,
            y=rect.y + 16,
            fill=self._palette.text,
            font_family=DEFAULT_FONT_FAMILY,
            font_size=DEFAULT_FONT_SIZE,
            text_anchor="start",
        ).text = title

    def _draw_item(self, parent: ET.Element, item: LayoutItem) -> None:
        entity = item.entity
        rect = item.rect
        label = _display_label(entity)

        if item.shape == "text_label":
            self._draw_rectangle(parent, rect, rounded=False)
            self._draw_centered_text(parent, rect, label)
            return

        if item.shape == "arrow":
            self._draw_inline_arrow(parent, rect, arrow_id="inline-arrow")
            return

        if item.shape == "rounded_rectangle":
            self._draw_rectangle(parent, rect, rounded=True)
            self._draw_centered_text(parent, rect, label)
            return

        self._draw_rectangle(parent, rect, rounded=False)
        self._draw_centered_text(parent, rect, label)

    def _draw_rectangle(self, parent: ET.Element, rect: Rect, *, rounded: bool) -> None:
        attrs: dict[str, str | float] = {
            "x": rect.x,
            "y": rect.y,
            "width": rect.width,
            "height": rect.height,
            "fill": self._palette.fill,
            "stroke": self._palette.stroke,
            "stroke_width": DEFAULT_STROKE_WIDTH,
        }
        if rounded:
            attrs["rx"] = DEFAULT_CORNER_RADIUS
            attrs["ry"] = DEFAULT_CORNER_RADIUS
        _sub(parent, "rect", **attrs)

    def _draw_centered_text(self, parent: ET.Element, rect: Rect, text: str) -> None:
        point = center_text_position(rect, text, font_size=DEFAULT_FONT_SIZE)
        _sub(
            parent,
            "text",
            x=point.x,
            y=point.y,
            fill=self._palette.text,
            font_family=DEFAULT_FONT_FAMILY,
            font_size=DEFAULT_FONT_SIZE,
            text_anchor="middle",
        ).text = text

    def _draw_arrow(
        self,
        parent: ET.Element,
        source_rect: Rect,
        target_rect: Rect,
        *,
        arrow_id: str,
    ) -> None:
        start = source_rect.bottom_center
        end = target_rect.top_center
        if start.y >= end.y:
            start = Point(source_rect.center.x, source_rect.y)
            end = Point(target_rect.center.x, target_rect.y + target_rect.height)

        segment = ArrowSegment(
            start=Point(start.x, start.y + 4), end=Point(end.x, end.y - 4)
        )
        line_start, line_end = segment.line_points()
        _sub(
            parent,
            "line",
            id=arrow_id,
            x1=line_start.x,
            y1=line_start.y,
            x2=line_end.x,
            y2=line_end.y,
            stroke=self._palette.arrow,
            stroke_width=DEFAULT_STROKE_WIDTH,
        )
        left, tip, right = segment.head_points()
        points = f"{left.x},{left.y} {tip.x},{tip.y} {right.x},{right.y}"
        _sub(
            parent,
            "polygon",
            points=points,
            fill=self._palette.arrow,
            stroke=self._palette.arrow,
            stroke_width=1,
        )

    def _draw_inline_arrow(
        self, parent: ET.Element, rect: Rect, *, arrow_id: str
    ) -> None:
        segment = ArrowSegment(
            start=Point(rect.x + 12, rect.center.y),
            end=Point(rect.x + rect.width - 12, rect.center.y),
        )
        line_start, line_end = segment.line_points()
        _sub(
            parent,
            "line",
            id=arrow_id,
            x1=line_start.x,
            y1=line_start.y,
            x2=line_end.x,
            y2=line_end.y,
            stroke=self._palette.arrow,
            stroke_width=DEFAULT_STROKE_WIDTH,
        )
        left, tip, right = segment.head_points()
        points = f"{left.x},{left.y} {tip.x},{tip.y} {right.x},{right.y}"
        _sub(
            parent,
            "polygon",
            points=points,
            fill=self._palette.arrow,
            stroke=self._palette.arrow,
            stroke_width=1,
        )

    def _draw_style_annotations(
        self,
        svg: ET.Element,
        graph: OntologyGraph,
        layout: GraphLayout,
        margin: float,
    ) -> None:
        annotations = [
            entity
            for entity in graph.entities
            if entity.entity_type == EntityType.ANNOTATION and ":style:" in entity.id
        ]
        if not annotations:
            return

        group = ET.SubElement(svg, "g", id="style-references")
        base_y = layout.canvas_size.height - margin - 28
        x = margin
        for index, entity in enumerate(annotations):
            rect = Rect(x + index * 140, base_y, 130, 24)
            self._draw_rectangle(group, rect, rounded=True)
            self._draw_centered_text(group, rect, _display_label(entity))
