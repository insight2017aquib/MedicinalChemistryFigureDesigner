"""Minimal SVG renderer for ontology graphs."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers.base import RenderConfig, RenderResult, Renderer
from figure_agent.renderers.exceptions import SVGRenderError
from figure_agent.renderers.geometry import (
    ArrowSegment,
    Point,
    Rect,
    center_text_position,
)
from figure_agent.renderers.scene.builder import build_visual_scene
from figure_agent.renderers.scene.exceptions import SceneBuildError
from figure_agent.renderers.scene.models import (
    LabelAnchor,
    PrimitiveKind,
    SceneStyle,
    VisualLabel,
    VisualPrimitive,
    VisualScene,
)
from figure_agent.renderers.styling import (
    DEFAULT_PALETTE,
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


def _palette_from_scene(scene: VisualScene) -> MonochromePalette:
    palette = scene.style.palette
    return MonochromePalette(
        background=palette.background,
        stroke=palette.stroke,
        fill=palette.fill,
        fill_container=palette.fill_container,
        text=palette.text,
        arrow=palette.arrow,
    )


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
            scene = build_visual_scene(graph, config=cfg, palette=self._palette)
            return self.render_scene(scene)
        except SceneBuildError as exc:
            raise SVGRenderError(str(exc)) from exc
        except Exception as exc:
            if exc.__class__.__module__.startswith("figure_agent.renderers"):
                raise
            raise SVGRenderError(f"Failed to render SVG: {exc}") from exc

    def render_scene(self, scene: VisualScene) -> RenderResult:
        """Render a visual scene to SVG."""
        try:
            svg_root = self._build_svg(scene)
            content = ET.tostring(svg_root, encoding="unicode")
            return RenderResult(
                content=content,
                width=scene.canvas_width,
                height=scene.canvas_height,
                mime_type="image/svg+xml",
            )
        except Exception as exc:
            if exc.__class__.__module__.startswith("figure_agent.renderers"):
                raise
            raise SVGRenderError(f"Failed to render SVG: {exc}") from exc

    def _build_svg(self, scene: VisualScene) -> ET.Element:
        palette = _palette_from_scene(scene)
        style = scene.style
        primitive_by_id = scene.primitive_by_id()

        svg = ET.Element(
            "svg",
            {
                "xmlns": SVG_NS,
                "width": str(scene.canvas_width),
                "height": str(scene.canvas_height),
                "viewBox": f"0 0 {scene.canvas_width} {scene.canvas_height}",
            },
        )

        _sub(
            svg,
            "rect",
            id="canvas-background",
            x=0,
            y=0,
            width=scene.canvas_width,
            height=scene.canvas_height,
            fill=palette.background,
            stroke="none",
        )

        for panel in scene.panels:
            panel_group = ET.SubElement(svg, "g", id=_sanitize_id(panel.id))
            boundary = primitive_by_id[panel.id]
            self._draw_panel_boundary(panel_group, boundary, palette, style)

            for member_id in panel.primitive_ids:
                if member_id == panel.id:
                    continue
                primitive = primitive_by_id[member_id]
                item_group = ET.SubElement(
                    panel_group,
                    "g",
                    id=_sanitize_id(primitive.id),
                )
                self._draw_primitive(item_group, primitive, palette, style)

        arrow_group = ET.SubElement(svg, "g", id="arrows")
        for connector in scene.connectors:
            source_rect = primitive_by_id.get(connector.source_id)
            target_rect = primitive_by_id.get(connector.target_id)
            if source_rect is None or target_rect is None:
                continue
            self._draw_arrow(
                arrow_group,
                source_rect.bounds,
                target_rect.bounds,
                palette,
                style,
                arrow_id=connector.id,
            )

        if scene.style_references:
            group = ET.SubElement(svg, "g", id="style-references")
            for style_ref in scene.style_references:
                primitive = primitive_by_id[style_ref.id]
                self._draw_primitive(group, primitive, palette, style)

        return svg

    def _draw_panel_boundary(
        self,
        parent: ET.Element,
        primitive: VisualPrimitive,
        palette: MonochromePalette,
        style: SceneStyle,
    ) -> None:
        rect = primitive.bounds
        _sub(
            parent,
            "rect",
            x=rect.x,
            y=rect.y,
            width=rect.width,
            height=rect.height,
            rx=style.corner_radius,
            ry=style.corner_radius,
            fill=palette.fill_container,
            stroke=palette.stroke,
            stroke_width=style.stroke_width,
        )
        if primitive.label is not None:
            self._draw_label(parent, primitive, primitive.label, palette, style)

    def _draw_primitive(
        self,
        parent: ET.Element,
        primitive: VisualPrimitive,
        palette: MonochromePalette,
        style: SceneStyle,
    ) -> None:
        rect = primitive.bounds

        if primitive.kind == PrimitiveKind.ARROW:
            self._draw_inline_arrow(parent, rect, palette, style, arrow_id="inline-arrow")
            return

        rounded = primitive.kind in {
            PrimitiveKind.ROUNDED_RECTANGLE,
            PrimitiveKind.STYLE_REFERENCE,
        }
        self._draw_rectangle(parent, rect, palette, style, rounded=rounded)

        if primitive.label is not None:
            self._draw_label(parent, primitive, primitive.label, palette, style)

    def _draw_rectangle(
        self,
        parent: ET.Element,
        rect: Rect,
        palette: MonochromePalette,
        style: SceneStyle,
        *,
        rounded: bool,
    ) -> None:
        attrs: dict[str, str | float] = {
            "x": rect.x,
            "y": rect.y,
            "width": rect.width,
            "height": rect.height,
            "fill": palette.fill,
            "stroke": palette.stroke,
            "stroke_width": style.stroke_width,
        }
        if rounded:
            attrs["rx"] = style.corner_radius
            attrs["ry"] = style.corner_radius
        _sub(parent, "rect", **attrs)

    def _label_point(
        self,
        primitive: VisualPrimitive,
        label: VisualLabel,
        style: SceneStyle,
    ) -> Point:
        if label.anchor == LabelAnchor.MIDDLE:
            return center_text_position(
                primitive.bounds,
                label.text,
                font_size=style.font_size,
            )
        return label.position

    def _draw_label(
        self,
        parent: ET.Element,
        primitive: VisualPrimitive,
        label: VisualLabel,
        palette: MonochromePalette,
        style: SceneStyle,
    ) -> None:
        point = self._label_point(primitive, label, style)
        anchor_map = {
            LabelAnchor.START: "start",
            LabelAnchor.MIDDLE: "middle",
            LabelAnchor.END: "end",
        }
        _sub(
            parent,
            "text",
            x=point.x,
            y=point.y,
            fill=palette.text,
            font_family=style.font_family,
            font_size=style.font_size,
            text_anchor=anchor_map[label.anchor],
        ).text = label.text

    def _draw_arrow(
        self,
        parent: ET.Element,
        source_rect: Rect,
        target_rect: Rect,
        palette: MonochromePalette,
        style: SceneStyle,
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
            stroke=palette.arrow,
            stroke_width=style.stroke_width,
        )
        left, tip, right = segment.head_points()
        points = f"{left.x},{left.y} {tip.x},{tip.y} {right.x},{right.y}"
        _sub(
            parent,
            "polygon",
            points=points,
            fill=palette.arrow,
            stroke=palette.arrow,
            stroke_width=1,
        )

    def _draw_inline_arrow(
        self,
        parent: ET.Element,
        rect: Rect,
        palette: MonochromePalette,
        style: SceneStyle,
        *,
        arrow_id: str,
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
            stroke=palette.arrow,
            stroke_width=style.stroke_width,
        )
        left, tip, right = segment.head_points()
        points = f"{left.x},{left.y} {tip.x},{tip.y} {right.x},{right.y}"
        _sub(
            parent,
            "polygon",
            points=points,
            fill=palette.arrow,
            stroke=palette.arrow,
            stroke_width=1,
        )