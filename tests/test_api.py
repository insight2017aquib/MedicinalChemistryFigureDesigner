"""Tests for the Figure Agent public API."""

from __future__ import annotations

from pathlib import Path

import pytest

from figure_agent.api import (
    CompilationAPIError,
    ContentSlotSpec,
    ExportRequest,
    GenerateFSLRequest,
    RenderAPIError,
    compile,
    export,
    generate_fsl,
    health,
    list_renderers,
    register_renderer,
    render,
    render_svg,
    unregister_renderer,
    validate_fsl,
    version,
)
from figure_agent.renderers.base import RenderConfig, RenderResult, Renderer
from helpers import valid_document

REPO_ROOT = Path(__file__).resolve().parents[1]
MINIMAL_FIGURE = REPO_ROOT / "examples" / "minimal_figure.yaml"


def test_health_reports_ok() -> None:
    """Health endpoint should report ready status and renderers."""
    result = health()
    assert result.status == "ok"
    assert result.version
    assert "svg" in result.renderers
    assert result.components["compiler"] == "ready"


def test_version_metadata() -> None:
    """Version endpoint should expose API and renderer metadata."""
    result = version()
    assert result.version
    assert result.api_version == "0.7"
    assert "svg" in result.renderers
    assert result.fsl_versions


def test_generate_fsl_produces_valid_document() -> None:
    """Generated FSL should pass validation."""
    generated = generate_fsl(
        GenerateFSLRequest(
            figure_id="fig-api-001",
            title="API Generated Figure",
            slots=(ContentSlotSpec(id="slot-a", label="Slot A"),),
        )
    )
    validation = validate_fsl(generated.document)
    assert validation.valid is True
    assert generated.yaml
    assert generated.json


def test_validate_fsl_valid_request() -> None:
    """Valid FSL documents should return valid=True."""
    result = validate_fsl(valid_document())
    assert result.valid is True
    assert result.figure is not None
    assert not result.errors


def test_validate_fsl_invalid_request() -> None:
    """Invalid FSL should return structured errors without raising."""
    invalid = valid_document()
    invalid["layout"]["panels"][0]["object_refs"] = ["missing-slot"]
    result = validate_fsl(invalid)
    assert result.valid is False
    assert result.errors
    assert result.figure is None


def test_validate_fsl_from_yaml_string() -> None:
    """API should accept YAML string input."""
    yaml_text = MINIMAL_FIGURE.read_text(encoding="utf-8")
    result = validate_fsl(yaml_text)
    assert result.valid is True


def test_compile_from_valid_fsl() -> None:
    """Compile should return ontology graph payload."""
    result = compile(valid_document())
    assert result.success is True
    assert result.graph is not None
    assert result.entity_count > 0
    assert result.relationship_count >= 0
    assert "entities" in result.graph


def test_compile_invalid_fsl_returns_errors() -> None:
    """Compile failures should return success=False."""
    invalid = valid_document()
    invalid["template"]["ref"] = "templates/unknown.md"
    result = compile(invalid)
    assert result.success is False
    assert result.errors


def test_compile_raise_on_error() -> None:
    """Compile can optionally raise CompilationAPIError."""
    invalid = valid_document()
    invalid["metadata"] = {}
    with pytest.raises(CompilationAPIError):
        compile(invalid, raise_on_error=True)


def test_render_svg_from_fsl() -> None:
    """render_svg should produce SVG content from FSL."""
    result = render_svg(valid_document())
    assert result.success is True
    assert result.content
    assert "<svg" in result.content
    assert result.mime_type == "image/svg+xml"
    assert result.renderer == "svg"


def test_render_with_named_renderer() -> None:
    """render() should dispatch to registered backends."""
    compiled = compile(valid_document())
    assert compiled.graph is not None
    result = render(compiled.graph, renderer="svg")
    assert result.success is True
    assert result.content


def test_render_unknown_renderer_returns_error() -> None:
    """Unknown renderer names should return structured errors."""
    result = render(valid_document(), renderer="biorender")
    assert result.success is False
    assert result.errors
    assert any("biorender" in error.lower() for error in result.errors)


def test_render_raise_on_error_for_unknown_renderer() -> None:
    """render can raise RenderAPIError for unknown backends."""
    with pytest.raises(RenderAPIError):
        render(valid_document(), renderer="pptx", raise_on_error=True)


def test_renderer_registration() -> None:
    """Custom renderers should register without API changes."""

    class StubRenderer(Renderer):
        def render(self, graph, *, config: RenderConfig | None = None) -> RenderResult:
            return RenderResult(
                content="<stub />",
                width=10,
                height=10,
                mime_type="image/stub",
            )

    register_renderer("stub", StubRenderer)
    try:
        assert "stub" in list_renderers()
        result = render(valid_document(), renderer="stub")
        assert result.success is True
        assert result.content == "<stub />"
        assert result.mime_type == "image/stub"
    finally:
        unregister_renderer("stub")


def test_export_writes_svg_file(tmp_path: Path) -> None:
    """Export should write rendered SVG to disk."""
    output = tmp_path / "figure.svg"
    result = export(valid_document(), output)
    assert result.success is True
    assert result.path == str(output)
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert content.startswith("<svg")


def test_export_with_request_object(tmp_path: Path) -> None:
    """ExportRequest should configure output path and renderer."""
    output = tmp_path / "nested" / "out.svg"
    result = export(
        valid_document(),
        request=ExportRequest(output_path=str(output), renderer="svg", format="svg"),
    )
    assert result.success is True
    assert output.exists()


def test_full_pipeline_generate_compile_render_export(tmp_path: Path) -> None:
    """End-to-end API flow from generation through export."""
    generated = generate_fsl(
        GenerateFSLRequest(figure_id="fig-pipeline", title="Pipeline Test")
    )
    validation = validate_fsl(generated.document)
    assert validation.valid is True

    compiled = compile(generated.document)
    assert compiled.success is True

    rendered = render_svg(compiled.graph)
    assert rendered.success is True

    output = tmp_path / "pipeline.svg"
    exported = export(compiled.graph, output)
    assert exported.success is True
    assert exported.format == "svg"