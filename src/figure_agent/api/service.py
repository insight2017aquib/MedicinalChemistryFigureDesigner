"""Public Figure Agent API service layer."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from figure_agent.core.constants import __version__
from figure_agent.api.exceptions import (
    APIError,
    CompilationAPIError,
    ExportAPIError,
    InvalidInputError,
    RenderAPIError,
    UnknownRendererError,
)
from figure_agent.api.requests import (
    ContentSlotSpec,
    ExportRequest,
    GenerateFSLRequest,
    RenderRequest,
    ValidateFSLRequest,
)
from figure_agent.api.responses import (
    CompileResponse,
    ExportResponse,
    GenerateFSLResponse,
    HealthResponse,
    RenderResponse,
    ValidationResponse,
    VersionResponse,
)
from figure_agent.compiler import compile_figure
from figure_agent.core.constants import SUPPORTED_FSL_VERSIONS
from figure_agent.fsl.exceptions import FSLError
from figure_agent.fsl.models import Figure
from figure_agent.fsl.parser import parse, validate_schema
from figure_agent.fsl.serializer import to_json, to_yaml
from figure_agent.fsl.validator import FSLValidator
from figure_agent.ontology.registry import graph_from_dict, graph_to_dict
from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers.base import RenderConfig, Renderer
from figure_agent.renderers.svg_renderer import SVGRenderer

FSLSource = dict[str, Any] | str | Figure
GraphSource = dict[str, Any] | OntologyGraph
PipelineSource = FSLSource | GraphSource

RendererFactory = Callable[[], Renderer]

_RENDERER_REGISTRY: dict[str, RendererFactory] = {}


def register_renderer(name: str, factory: RendererFactory) -> None:
    """Register a renderer backend by name.

    Future backends (``biorender``, ``gptimage``, ``pptx``, etc.) register
    here without changing the public API surface.

    Args:
        name: Renderer identifier (case-insensitive).
        factory: Callable returning a ``Renderer`` instance.
    """
    key = name.strip().lower()
    if not key:
        raise InvalidInputError("Renderer name must not be empty")
    _RENDERER_REGISTRY[key] = factory


def unregister_renderer(name: str) -> None:
    """Remove a renderer from the registry."""
    _RENDERER_REGISTRY.pop(name.strip().lower(), None)


def list_renderers() -> list[str]:
    """Return registered renderer identifiers."""
    return sorted(_RENDERER_REGISTRY)


def _ensure_default_renderers() -> None:
    if "svg" not in _RENDERER_REGISTRY:
        register_renderer("svg", SVGRenderer)


def _resolve_renderer(name: str) -> Renderer:
    _ensure_default_renderers()
    key = name.strip().lower()
    try:
        return _RENDERER_REGISTRY[key]()
    except KeyError as exc:
        raise UnknownRendererError(name, available=list_renderers()) from exc


def _load_raw_document(source: str) -> dict[str, Any]:
    text = source.strip()
    if not text:
        raise InvalidInputError("FSL source string is empty")

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise InvalidInputError(f"Invalid YAML or JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise InvalidInputError("FSL document root must be an object/mapping")
    return data


def _resolve_figure(source: FSLSource, *, semantic: bool = True) -> Figure:
    if isinstance(source, Figure):
        return source
    if isinstance(source, dict):
        return parse(source, run_semantic_validation=semantic)
    if isinstance(source, str):
        return parse(_load_raw_document(source), run_semantic_validation=semantic)
    raise InvalidInputError(
        f"Unsupported FSL source type: {type(source).__name__}",
    )


def _resolve_graph(source: GraphSource) -> OntologyGraph:
    if isinstance(source, OntologyGraph):
        return source
    if isinstance(source, dict):
        return graph_from_dict(source)
    raise InvalidInputError(
        f"Unsupported graph source type: {type(source).__name__}",
    )


def _is_ontology_graph_dict(source: dict[str, Any]) -> bool:
    return "entities" in source and "relationships" in source


def _resolve_pipeline_source(
    source: PipelineSource,
    *,
    semantic: bool = True,
) -> OntologyGraph:
    if isinstance(source, OntologyGraph):
        return source
    if isinstance(source, dict):
        if _is_ontology_graph_dict(source):
            return graph_from_dict(source)
        figure = _resolve_figure(source, semantic=semantic)
        return compile_figure(figure)
    figure = _resolve_figure(source, semantic=semantic)  # type: ignore[arg-type]
    return compile_figure(figure)


def _build_render_config(request: RenderRequest | ExportRequest | None) -> RenderConfig:
    if request is None:
        return RenderConfig()
    kwargs: dict[str, float] = {}
    if request.width is not None:
        kwargs["width"] = request.width
    if request.height is not None:
        kwargs["height"] = request.height
    if request.margin is not None:
        kwargs["margin"] = request.margin
    return RenderConfig(**kwargs) if kwargs else RenderConfig()


def _collect_fsl_errors(exc: BaseException) -> tuple[str, ...]:
    errors = getattr(exc, "errors", None)
    if errors:
        return tuple(str(item) for item in errors)
    return (str(exc),)


def generate_fsl(
    request: GenerateFSLRequest | None = None,
    *,
    figure_id: str | None = None,
    title: str | None = None,
    slots: list[ContentSlotSpec] | tuple[ContentSlotSpec, ...] | None = None,
) -> GenerateFSLResponse:
    """Generate a minimal valid FSL document from parameters.

    Args:
        request: Full generation request. When omitted, defaults are used.
        figure_id: Optional override for ``request.figure_id``.
        title: Optional override for ``request.title``.
        slots: Optional override for ``request.slots``.

    Returns:
        Generated document as dict plus serialized YAML and JSON strings.
    """
    req = request or GenerateFSLRequest()
    resolved_slots = tuple(slots) if slots is not None else req.slots
    resolved_id = figure_id or req.figure_id
    resolved_title = title or req.title

    document: dict[str, Any] = {
        "fsl_version": "0.3.0",
        "metadata": {
            "id": resolved_id,
            "title": resolved_title,
            "author": req.author,
            "provenance": [],
        },
        "template": {
            "ref": req.template_ref,
            "params": {"aspect_ratio": "4:3"},
        },
        "layout": {
            "type": req.layout_type,
            "panels": [
                {
                    "id": req.panel_id,
                    "zones": ["primary"],
                    "object_refs": [slot.id for slot in resolved_slots],
                }
            ],
        },
        "styles": {
            "refs": [{"ref": req.style_ref}],
            "overrides": {},
        },
        "content_slots": [
            {
                "id": slot.id,
                "label": slot.label,
                "type": slot.type,
                "value": slot.value,
            }
            for slot in resolved_slots
        ],
        "rules": {"refs": ["rules/composition.md"]},
        "validation": {
            "refs": ["validation/pre-export-checklist.md"],
            "required_checks": [],
        },
        "knowledge": {"packs": []},
        "integrations": {},
        "export": {
            "formats": list(req.export_formats),
            "naming": "fig-{id}",
        },
    }

    figure = parse(document)
    return GenerateFSLResponse(
        document=figure.model_dump(mode="json"),
        yaml=to_yaml(figure),
        json=to_json(figure),
    )


def validate_fsl(
    source: FSLSource,
    *,
    request: ValidateFSLRequest | None = None,
    semantic: bool | None = None,
) -> ValidationResponse:
    """Validate an FSL document without raising on failure.

    Accepts a ``Figure``, dictionary, YAML string, or JSON string.

    Args:
        source: FSL input to validate.
        request: Validation options.
        semantic: Override for semantic validation (default ``True``).

    Returns:
        ``ValidationResponse`` with ``valid`` flag and any error messages.
    """
    opts = request or ValidateFSLRequest()
    run_semantic = semantic if semantic is not None else opts.semantic

    try:
        if isinstance(source, Figure):
            figure = source
        elif isinstance(source, dict):
            figure = validate_schema(source)
            if run_semantic:
                FSLValidator().validate(figure)
        elif isinstance(source, str):
            figure = validate_schema(_load_raw_document(source))
            if run_semantic:
                FSLValidator().validate(figure)
        else:
            return ValidationResponse(
                valid=False,
                errors=(f"Unsupported FSL source type: {type(source).__name__}",),
            )

        return ValidationResponse(
            valid=True,
            figure=figure.model_dump(mode="json"),
        )
    except FSLError as exc:
        return ValidationResponse(valid=False, errors=_collect_fsl_errors(exc))
    except InvalidInputError as exc:
        return ValidationResponse(valid=False, errors=_collect_fsl_errors(exc))


def compile(
    source: FSLSource,
    *,
    semantic: bool = True,
    raise_on_error: bool = False,
) -> CompileResponse:
    """Compile an FSL figure into an ontology graph.

    Args:
        source: FSL document as ``Figure``, dict, or YAML/JSON string.
        semantic: Run semantic validation before compilation.
        raise_on_error: Raise ``CompilationAPIError`` instead of returning errors.

    Returns:
        ``CompileResponse`` with serialized graph on success.
    """
    try:
        figure = _resolve_figure(source, semantic=semantic)
        graph = compile_figure(figure)
        payload = graph_to_dict(graph)
        return CompileResponse(
            success=True,
            graph=payload,
            entity_count=len(graph.entities),
            relationship_count=len(graph.relationships),
        )
    except (FSLError, APIError) as exc:
        errors = _collect_fsl_errors(exc)
        if raise_on_error:
            raise CompilationAPIError("Compilation failed", errors=list(errors)) from exc
        return CompileResponse(success=False, errors=errors)
    except Exception as exc:
        errors = (str(exc),)
        if raise_on_error:
            raise CompilationAPIError("Compilation failed", errors=list(errors)) from exc
        return CompileResponse(success=False, errors=errors)


def render(
    source: PipelineSource,
    *,
    renderer: str = "svg",
    request: RenderRequest | None = None,
    semantic: bool = True,
    raise_on_error: bool = False,
) -> RenderResponse:
    """Render an FSL figure or ontology graph using a registered backend.

    Args:
        source: FSL document or compiled ontology graph.
        renderer: Registered renderer name (e.g. ``"svg"``).
        request: Optional render configuration.
        semantic: Validate FSL before compile when source is FSL.
        raise_on_error: Raise ``RenderAPIError`` instead of returning errors.

    Returns:
        ``RenderResponse`` with rendered content on success.
    """
    render_opts = request or RenderRequest(renderer=renderer)
    resolved_renderer = render_opts.renderer or renderer

    try:
        graph = _resolve_pipeline_source(source, semantic=semantic)
        backend = _resolve_renderer(resolved_renderer)
        config = _build_render_config(render_opts)
        result = backend.render(graph, config=config)
        return RenderResponse(
            success=True,
            content=result.content,
            width=result.width,
            height=result.height,
            mime_type=result.mime_type,
            renderer=resolved_renderer,
        )
    except (APIError, FSLError) as exc:
        errors = _collect_fsl_errors(exc)
        if raise_on_error:
            raise RenderAPIError("Render failed", errors=list(errors)) from exc
        return RenderResponse(success=False, renderer=resolved_renderer, errors=errors)
    except Exception as exc:
        errors = (str(exc),)
        if raise_on_error:
            raise RenderAPIError("Render failed", errors=list(errors)) from exc
        return RenderResponse(success=False, renderer=resolved_renderer, errors=errors)


def render_svg(
    source: PipelineSource,
    *,
    request: RenderRequest | None = None,
    semantic: bool = True,
    raise_on_error: bool = False,
) -> RenderResponse:
    """Render using the SVG backend (shortcut for ``render(..., renderer='svg')``)."""
    opts = request or RenderRequest(renderer="svg")
    return render(
        source,
        renderer="svg",
        request=opts,
        semantic=semantic,
        raise_on_error=raise_on_error,
    )


def export(
    source: PipelineSource,
    output_path: str | Path | None = None,
    *,
    request: ExportRequest | None = None,
    renderer: str = "svg",
    semantic: bool = True,
    raise_on_error: bool = False,
) -> ExportResponse:
    """Compile (if needed), render, and write output to disk.

    Args:
        source: FSL document or ontology graph.
        output_path: Destination file path. Optional when ``request`` is provided.
        request: Optional export parameters.
        renderer: Renderer name when ``request`` is omitted.
        semantic: Validate FSL before compile when source is FSL.
        raise_on_error: Raise ``ExportAPIError`` instead of returning errors.

    Returns:
        ``ExportResponse`` with written path on success.
    """
    if request is None:
        if output_path is None:
            raise InvalidInputError(
                "export() requires output_path or an ExportRequest",
            )
        export_opts = ExportRequest(output_path=str(output_path), renderer=renderer)
    else:
        export_opts = request
    render_result = render(
        source,
        renderer=export_opts.renderer,
        request=RenderRequest(
            renderer=export_opts.renderer,
            width=export_opts.width,
            height=export_opts.height,
            margin=export_opts.margin,
        ),
        semantic=semantic,
        raise_on_error=raise_on_error,
    )

    if not render_result.success or render_result.content is None:
        if raise_on_error:
            raise ExportAPIError(
                "Export failed",
                errors=list(render_result.errors),
            )
        return ExportResponse(
            success=False,
            renderer=export_opts.renderer,
            errors=render_result.errors,
        )

    path = Path(export_opts.output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_result.content, encoding="utf-8")
    except OSError as exc:
        errors = (str(exc),)
        if raise_on_error:
            raise ExportAPIError("Export failed", errors=list(errors)) from exc
        return ExportResponse(
            success=False,
            renderer=export_opts.renderer,
            errors=errors,
        )

    output_format = export_opts.format or export_opts.renderer
    return ExportResponse(
        success=True,
        path=str(path),
        format=output_format,
        renderer=export_opts.renderer,
    )


def health() -> HealthResponse:
    """Report service health and registered capabilities."""
    _ensure_default_renderers()
    return HealthResponse(
        status="ok",
        version=__version__,
        components={
            "fsl": "ready",
            "ontology": "ready",
            "compiler": "ready",
            "renderers": "ready",
        },
        renderers=tuple(list_renderers()),
    )


def version() -> VersionResponse:
    """Return package and API version metadata."""
    _ensure_default_renderers()
    return VersionResponse(
        version=__version__,
        api_version="0.7",
        fsl_versions=tuple(sorted(SUPPORTED_FSL_VERSIONS)),
        renderers=tuple(list_renderers()),
    )


_ensure_default_renderers()