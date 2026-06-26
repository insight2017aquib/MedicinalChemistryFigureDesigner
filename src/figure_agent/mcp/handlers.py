"""MCP tool handlers that orchestrate the existing Figure Agent API."""

from __future__ import annotations

import base64
import re
from dataclasses import asdict, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from figure_agent.api.requests import ContentSlotSpec, GenerateFSLRequest, RenderRequest
from figure_agent.api.service import (
    compile,
    generate_fsl,
    health,
    render,
    render_svg,
    validate_fsl,
    version,
)
from figure_agent.mcp.config import MCPServerConfig
from figure_agent.mcp.exceptions import MCPToolError
from figure_agent.mcp.models import MCPToolResult
from figure_agent.mcp.registry import list_tool_names
from figure_agent.ontology.registry import graph_from_dict
from figure_agent.renderers.base import RenderConfig
from figure_agent.renderers.gpt_image import (
    GPTImageRenderOptions,
    create_gpt_image_renderer,
)
from figure_agent.renderers.scene.builder import build_visual_scene
from figure_agent.renderers.scene.models import VisualScene


def _json_safe(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _json_safe(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def serialize_visual_scene(scene: VisualScene) -> dict[str, Any]:
    """Convert a Visual Scene to a JSON-serializable dictionary."""
    return _json_safe(scene)


def parse_natural_language_description(description: str) -> GenerateFSLRequest:
    """Map a natural-language brief to structured FSL generation parameters."""
    text = description.strip()
    if not text:
        raise MCPToolError(
            "Description must not be empty",
            tool="generate_fsl",
            errors=("Provide a natural-language figure description.",),
        )

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = _extract_title(lines[0])
    slot_lines = lines[1:] if len(lines) > 1 else []

    slots: list[ContentSlotSpec] = []
    for index, line in enumerate(slot_lines, start=1):
        label = _normalize_slot_line(line)
        if label:
            slots.append(ContentSlotSpec(id=f"slot-{index}", label=label))

    if not slots:
        slots = [ContentSlotSpec(id="slot-1", label=title)]

    # generate_fsl() currently emits a single panel containing all slots.
    layout_type = "single-panel"
    figure_id = _slugify(title) or "fig-001"

    return GenerateFSLRequest(
        figure_id=figure_id,
        title=title,
        layout_type=layout_type,
        slots=tuple(slots),
    )


def _extract_title(line: str) -> str:
    cleaned = re.sub(
        r"^(create|design|generate|build)\s+(a|an)\s+figure\s+(for|about|showing)?\s*",
        "",
        line,
        flags=re.IGNORECASE,
    ).strip()
    return cleaned or line


def _normalize_slot_line(line: str) -> str:
    return re.sub(r"^[-*•\d.)\s]+", "", line).strip()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return f"fig-{slug[:40]}" if slug else ""


def _resolve_source(
    *,
    fsl: dict[str, Any] | str | None,
    graph: dict[str, Any] | None,
    tool: str,
) -> dict[str, Any] | str:
    if graph is not None:
        return graph
    if fsl is not None:
        return fsl
    raise MCPToolError(
        "Either fsl or graph must be provided",
        tool=tool,
        errors=("Pass an FSL document or compiled ontology graph.",),
    )


def _select_renderer(*, format: str | None, fsl: dict[str, Any] | str | None) -> str:
    if format:
        normalized = format.strip().lower()
        if normalized in {"png", "gpt-image", "gptimage", "image"}:
            return "gpt-image"
        if normalized in {"svg", "vector"}:
            return "svg"

    if isinstance(fsl, dict):
        export_formats = fsl.get("export", {}).get("formats", [])
        if isinstance(export_formats, list):
            lowered = [str(item).lower() for item in export_formats]
            if any(item in {"png", "gpt-image", "image"} for item in lowered):
                if "svg" not in lowered:
                    return "gpt-image"

    return "svg"


class MCPHandlers:
    """Orchestration layer for Figure Agent MCP tools."""

    def __init__(self, config: MCPServerConfig | None = None) -> None:
        self._config = config or MCPServerConfig()

    @property
    def config(self) -> MCPServerConfig:
        return self._config

    def generate_fsl(
        self,
        description: str,
        *,
        figure_id: str | None = None,
        title: str | None = None,
    ) -> MCPToolResult:
        """Generate valid FSL from a natural-language description."""
        try:
            request = parse_natural_language_description(description)
            response = generate_fsl(
                request,
                figure_id=figure_id,
                title=title,
            )
        except MCPToolError:
            raise
        except Exception as exc:
            raise MCPToolError(
                f"Failed to generate FSL: {exc}",
                tool="generate_fsl",
                errors=(str(exc),),
            ) from exc

        return MCPToolResult(
            success=True,
            tool="generate_fsl",
            data={
                "document": response.document,
                "yaml": response.yaml,
                "json": response.json,
            },
        )

    def validate_fsl(
        self,
        fsl: dict[str, Any] | str,
        *,
        semantic: bool = True,
    ) -> MCPToolResult:
        """Validate FSL and return a structured report."""
        result = validate_fsl(fsl, semantic=semantic)
        return MCPToolResult(
            success=result.valid,
            tool="validate_fsl",
            data={
                "valid": result.valid,
                "figure": result.figure,
                "errors": list(result.errors),
            },
            errors=result.errors,
        )

    def compile(
        self,
        fsl: dict[str, Any] | str,
        *,
        semantic: bool = True,
    ) -> MCPToolResult:
        """Compile FSL into an ontology graph."""
        result = compile(fsl, semantic=semantic)
        return MCPToolResult(
            success=result.success,
            tool="compile",
            data={
                "graph": result.graph,
                "entity_count": result.entity_count,
                "relationship_count": result.relationship_count,
                "errors": list(result.errors),
            },
            errors=result.errors,
        )

    def build_scene(
        self,
        *,
        fsl: dict[str, Any] | str | None = None,
        graph: dict[str, Any] | None = None,
        width: float | None = None,
        height: float | None = None,
        margin: float | None = None,
    ) -> MCPToolResult:
        """Build a Visual Scene from FSL or a graph."""
        source = _resolve_source(fsl=fsl, graph=graph, tool="build_scene")
        try:
            if graph is not None:
                ontology_graph = graph_from_dict(graph)
            else:
                compiled = compile(fsl, semantic=True)
                if not compiled.success or compiled.graph is None:
                    return MCPToolResult(
                        success=False,
                        tool="build_scene",
                        data={"errors": list(compiled.errors)},
                        errors=compiled.errors,
                    )
                ontology_graph = graph_from_dict(compiled.graph)

            config = _build_render_config(width=width, height=height, margin=margin)
            scene = build_visual_scene(ontology_graph, config=config)
        except Exception as exc:
            raise MCPToolError(
                f"Failed to build visual scene: {exc}",
                tool="build_scene",
                errors=(str(exc),),
            ) from exc

        return MCPToolResult(
            success=True,
            tool="build_scene",
            data={"scene": serialize_visual_scene(scene)},
        )

    def render_svg(
        self,
        *,
        fsl: dict[str, Any] | str | None = None,
        graph: dict[str, Any] | None = None,
        width: float | None = None,
        height: float | None = None,
        margin: float | None = None,
    ) -> MCPToolResult:
        """Render SVG from FSL or a graph."""
        source = _resolve_source(fsl=fsl, graph=graph, tool="render_svg")
        request = RenderRequest(
            renderer="svg",
            width=width,
            height=height,
            margin=margin,
        )
        result = render_svg(source, request=request)
        return MCPToolResult(
            success=result.success,
            tool="render_svg",
            data={
                "content": result.content,
                "width": result.width,
                "height": result.height,
                "mime_type": result.mime_type,
                "renderer": result.renderer,
                "errors": list(result.errors),
            },
            errors=result.errors,
        )

    def render_gpt_image(
        self,
        *,
        fsl: dict[str, Any] | str | None = None,
        graph: dict[str, Any] | None = None,
        width: float | None = None,
        height: float | None = None,
        margin: float | None = None,
        output_dir: str | None = None,
    ) -> MCPToolResult:
        """Render PNG via the Figure Agent GPT Image pipeline."""
        source = _resolve_source(fsl=fsl, graph=graph, tool="render_gpt_image")
        try:
            if graph is not None:
                ontology_graph = graph_from_dict(graph)
            else:
                compiled = compile(fsl, semantic=True)
                if not compiled.success or compiled.graph is None:
                    return MCPToolResult(
                        success=False,
                        tool="render_gpt_image",
                        data={"errors": list(compiled.errors)},
                        errors=compiled.errors,
                    )
                ontology_graph = graph_from_dict(compiled.graph)

            config = _build_render_config(width=width, height=height, margin=margin)
            scene = build_visual_scene(ontology_graph, config=config)
            target_dir = (
                Path(output_dir) if output_dir else self._config.output_dir
            )
            renderer = create_gpt_image_renderer(
                backend=self._config.gpt_image_backend_factory(),
                output_dir=target_dir,
                initial_backoff_seconds=0.01,
            )
            render_result = renderer.render_scene(
                scene,
                options=GPTImageRenderOptions(output_dir=target_dir),
            )
        except Exception as exc:
            raise MCPToolError(
                f"Failed to render GPT image: {exc}",
                tool="render_gpt_image",
                errors=(str(exc),),
            ) from exc

        image_bytes = base64.b64decode(render_result.render_result.content)
        return MCPToolResult(
            success=True,
            tool="render_gpt_image",
            data={
                "image_base64": render_result.render_result.content,
                "width": render_result.render_result.width,
                "height": render_result.render_result.height,
                "mime_type": render_result.render_result.mime_type,
                "renderer": "gpt-image",
                "image_path": (
                    str(render_result.image_path)
                    if render_result.image_path is not None
                    else None
                ),
                "metadata_path": (
                    str(render_result.metadata_path)
                    if render_result.metadata_path is not None
                    else None
                ),
                "metadata": render_result.metadata,
                "prompt_version": render_result.prompt_spec.version,
                "image_bytes_length": len(image_bytes),
            },
        )

    def render(
        self,
        *,
        fsl: dict[str, Any] | str | None = None,
        graph: dict[str, Any] | None = None,
        format: str | None = None,
        renderer: str | None = None,
        width: float | None = None,
        height: float | None = None,
        margin: float | None = None,
    ) -> MCPToolResult:
        """Render using an automatically selected renderer."""
        source = _resolve_source(fsl=fsl, graph=graph, tool="render")
        selected = renderer or _select_renderer(format=format, fsl=fsl)
        if selected == "gpt-image":
            return self.render_gpt_image(
                fsl=fsl,
                graph=graph,
                width=width,
                height=height,
                margin=margin,
            )

        request = RenderRequest(
            renderer="svg",
            width=width,
            height=height,
            margin=margin,
        )
        result = render(source, renderer="svg", request=request)
        return MCPToolResult(
            success=result.success,
            tool="render",
            data={
                "content": result.content,
                "width": result.width,
                "height": result.height,
                "mime_type": result.mime_type,
                "renderer": result.renderer,
                "errors": list(result.errors),
            },
            errors=result.errors,
        )

    def health(self) -> MCPToolResult:
        """Return server health status."""
        result = health()
        return MCPToolResult(
            success=result.status == "ok",
            tool="health",
            data={
                "status": result.status,
                "version": result.version,
                "components": result.components,
                "renderers": list(result.renderers),
                "mcp_tools": list_tool_names(),
            },
        )

    def version(self) -> MCPToolResult:
        """Return package version metadata."""
        result = version()
        return MCPToolResult(
            success=True,
            tool="version",
            data={
                "version": result.version,
                "api_version": result.api_version,
                "fsl_versions": list(result.fsl_versions),
                "renderers": list(result.renderers),
            },
        )


def _build_render_config(
    *,
    width: float | None,
    height: float | None,
    margin: float | None,
) -> RenderConfig:
    kwargs: dict[str, float] = {}
    if width is not None:
        kwargs["width"] = width
    if height is not None:
        kwargs["height"] = height
    if margin is not None:
        kwargs["margin"] = margin
    return RenderConfig(**kwargs) if kwargs else RenderConfig()