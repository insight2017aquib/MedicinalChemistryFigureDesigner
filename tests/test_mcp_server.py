"""Integration tests for the Figure Agent MCP server."""

from __future__ import annotations

import base64
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from figure_agent.mcp import (
    MCPHandlers,
    MCPServerConfig,
    create_mcp_server,
    list_tool_names,
    parse_natural_language_description,
)
from figure_agent.mcp.exceptions import MCPToolError
from figure_agent.mcp.registry import TOOL_DEFINITIONS, get_tool_definition
from figure_agent.renderers.gpt_image import MINIMAL_PNG_BYTES, StubImageBackend
from helpers import valid_document

pytest.importorskip("mcp")


def _handlers(tmp_path: Path) -> MCPHandlers:
    return MCPHandlers(
        MCPServerConfig(
            output_dir=tmp_path,
            gpt_image_backend_factory=StubImageBackend,
        )
    )


def test_tool_registry_lists_required_tools() -> None:
    """All milestone tools must be registered."""
    names = list_tool_names()
    assert names == [
        "generate_fsl",
        "validate_fsl",
        "compile",
        "build_scene",
        "render_svg",
        "render_gpt_image",
        "render",
        "health",
        "version",
    ]
    assert len(TOOL_DEFINITIONS) == 9
    assert get_tool_definition("render_gpt_image") is not None


def test_create_mcp_server_registers_tools() -> None:
    """FastMCP server should expose every registered tool."""
    server = create_mcp_server(
        MCPServerConfig(gpt_image_backend_factory=StubImageBackend)
    )
    tool_names = {tool.name for tool in server._tool_manager.list_tools()}  # type: ignore[attr-defined]
    assert tool_names == set(list_tool_names())


def test_parse_natural_language_description() -> None:
    """Natural-language briefs should map to structured generation parameters."""
    request = parse_natural_language_description(
        "Mechanism schematic\n- Receptor binding\n- Downstream signaling"
    )
    assert request.title == "Mechanism schematic"
    assert request.layout_type == "single-panel"
    assert len(request.slots) == 2
    assert request.slots[0].label == "Receptor binding"


def test_generate_fsl_from_natural_language(tmp_path: Path) -> None:
    """generate_fsl should return valid FSL from natural language."""
    handlers = _handlers(tmp_path)
    result = handlers.generate_fsl(
        "Create a figure showing assay workflow with primary readout"
    )

    assert result.success is True
    assert "document" in result.data
    assert "yaml" in result.data
    validation = handlers.validate_fsl(result.data["document"])
    assert validation.success is True
    assert validation.data["valid"] is True


def test_generate_fsl_empty_description_raises(tmp_path: Path) -> None:
    """Empty descriptions should produce a tool error."""
    handlers = _handlers(tmp_path)
    with pytest.raises(MCPToolError):
        handlers.generate_fsl("   ")


def test_validate_fsl_reports_errors(tmp_path: Path) -> None:
    """Invalid FSL should return a structured validation report."""
    handlers = _handlers(tmp_path)
    invalid = valid_document()
    invalid["layout"]["panels"][0]["object_refs"] = ["missing-slot"]

    result = handlers.validate_fsl(invalid)
    assert result.success is False
    assert result.data["valid"] is False
    assert result.errors


def test_compile_returns_graph(tmp_path: Path) -> None:
    """compile should return an ontology graph payload."""
    handlers = _handlers(tmp_path)
    result = handlers.compile(valid_document())

    assert result.success is True
    assert result.data["graph"] is not None
    assert result.data["entity_count"] > 0


def test_build_scene_returns_visual_scene(tmp_path: Path) -> None:
    """build_scene should return a serialized visual scene."""
    handlers = _handlers(tmp_path)
    fsl = valid_document()
    result = handlers.build_scene(fsl=fsl)

    assert result.success is True
    scene = result.data["scene"]
    assert scene["figure_id"] == "fig-001"
    assert scene["panels"]
    assert scene["primitives"]


def test_render_svg_returns_vector_output(tmp_path: Path) -> None:
    """render_svg should return SVG content."""
    handlers = _handlers(tmp_path)
    result = handlers.render_svg(fsl=valid_document())

    assert result.success is True
    assert "<svg" in (result.data["content"] or "")
    assert result.data["mime_type"] == "image/svg+xml"


def test_render_gpt_image_returns_png(tmp_path: Path) -> None:
    """render_gpt_image should return PNG bytes via Figure Agent."""
    handlers = _handlers(tmp_path)
    result = handlers.render_gpt_image(fsl=valid_document())

    assert result.success is True
    assert result.data["mime_type"] == "image/png"
    image_bytes = base64.b64decode(result.data["image_base64"])
    assert image_bytes == MINIMAL_PNG_BYTES
    assert (tmp_path / "fig-001.png").exists()
    assert (tmp_path / "fig-001.metadata.json").exists()


def test_render_auto_selects_png_format(tmp_path: Path) -> None:
    """render should choose GPT Image when PNG is requested."""
    handlers = _handlers(tmp_path)
    result = handlers.render(fsl=valid_document(), format="png")

    assert result.success is True
    assert result.data["renderer"] == "gpt-image"
    assert result.data["mime_type"] == "image/png"


def test_render_auto_selects_svg_by_default(tmp_path: Path) -> None:
    """render should default to SVG when no format is specified."""
    handlers = _handlers(tmp_path)
    document = valid_document()
    document["export"]["formats"] = ["svg"]
    result = handlers.render(fsl=document)

    assert result.success is True
    assert result.data["renderer"] == "svg"


def test_health_and_version(tmp_path: Path) -> None:
    """health and version should report MCP capabilities."""
    handlers = _handlers(tmp_path)

    health_result = handlers.health()
    assert health_result.success is True
    assert health_result.data["status"] == "ok"
    assert "generate_fsl" in health_result.data["mcp_tools"]

    version_result = handlers.version()
    assert version_result.success is True
    assert version_result.data["version"] == "1.0.0"
    assert version_result.data["api_version"] == "1.0"


def test_round_trip_natural_language_to_png(tmp_path: Path) -> None:
    """End-to-end workflow: NL -> FSL -> validate -> compile -> scene -> PNG."""
    handlers = _handlers(tmp_path)

    generated = handlers.generate_fsl(
        "Drug discovery pipeline\n- Target identification\n- Lead optimization"
    )
    assert generated.success is True
    document = generated.data["document"]

    validated = handlers.validate_fsl(document)
    assert validated.success is True

    compiled = handlers.compile(document)
    assert compiled.success is True

    scene = handlers.build_scene(graph=compiled.data["graph"])
    assert scene.success is True

    png = handlers.render_gpt_image(graph=compiled.data["graph"])
    assert png.success is True
    assert base64.b64decode(png.data["image_base64"]) == MINIMAL_PNG_BYTES


def test_missing_source_returns_tool_error_payload(tmp_path: Path) -> None:
    """Tools requiring input should fail gracefully without source data."""
    handlers = _handlers(tmp_path)
    server = create_mcp_server(
        MCPServerConfig(
            output_dir=tmp_path,
            gpt_image_backend_factory=StubImageBackend,
        )
    )
    tool = server._tool_manager.get_tool("build_scene")  # type: ignore[attr-defined]
    payload = json.loads(json.dumps(tool.fn()))  # type: ignore[attr-defined]

    assert payload["success"] is False
    assert payload["tool"] == "build_scene"
    assert payload["errors"]


def test_concurrent_handler_requests(tmp_path: Path) -> None:
    """Concurrent MCP handler calls should remain deterministic."""
    handlers = _handlers(tmp_path)
    document = valid_document()

    def _render_svg() -> bool:
        return handlers.render_svg(fsl=document).success

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda _: _render_svg(), range(16)))

    assert all(results)