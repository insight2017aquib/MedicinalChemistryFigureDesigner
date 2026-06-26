"""Tests for GPT Image raster renderer, backends, and end-to-end pipeline."""

from __future__ import annotations

import base64
import json
from pathlib import Path

import pytest

from figure_agent import compile_figure, load_yaml, parse, render
from figure_agent.api import list_renderers, register_renderer, unregister_renderer
from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers import build_visual_scene
from figure_agent.renderers.base import Renderer
from figure_agent.renderers.gpt_image import (
    GPTImageAPIError,
    GPTImageRenderOptions,
    GPTImageRenderer,
    GPTImageRetryExhaustedError,
    MINIMAL_PNG_BYTES,
    OpenAIImageBackend,
    StubImageBackend,
    create_gpt_image_renderer,
    resolve_openai_image_size,
)
from figure_agent.renderers.gpt_image.exceptions import GPTImageRenderError
from figure_agent.renderers.gpt_image.retry import call_with_retries
from figure_agent.renderers.gpt_image.storage import save_render_artifacts
from helpers import valid_document

REPO_ROOT = Path(__file__).resolve().parents[1]
MINIMAL_FIGURE = REPO_ROOT / "examples" / "minimal_figure.yaml"


def _compiled_graph():
    figure = parse(load_yaml(MINIMAL_FIGURE))
    return compile_figure(figure)


def _renderer_with_stub(
    tmp_path: Path,
    *,
    fail_until_attempt: int = 0,
) -> GPTImageRenderer:
    backend = StubImageBackend(fail_until_attempt=fail_until_attempt)
    return create_gpt_image_renderer(
        backend=backend,
        output_dir=tmp_path,
        max_retries=3,
        initial_backoff_seconds=0.01,
    )


def test_openai_size_resolution() -> None:
    """Scene aspect ratios should map to supported OpenAI size tokens."""
    assert resolve_openai_image_size(800, 800) == "1024x1024"
    assert resolve_openai_image_size(900, 600) == "1536x1024"
    assert resolve_openai_image_size(600, 900) == "1024x1536"


def test_openai_backend_requires_api_key() -> None:
    """OpenAI backend should fail fast without credentials."""
    with pytest.raises(GPTImageAPIError, match="API key"):
        OpenAIImageBackend(api_key="")


def test_retry_recovers_from_transient_failure() -> None:
    """Retry helper should succeed after transient backend failures."""
    attempts = {"count": 0}

    def operation() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("transient")
        return "ok"

    assert call_with_retries(operation, max_attempts=3, initial_backoff_seconds=0.01) == "ok"
    assert attempts["count"] == 3


def test_retry_exhaustion_raises() -> None:
    """Non-recoverable retry loops should raise GPTImageRetryExhaustedError."""

    def operation() -> None:
        raise RuntimeError("always fails")

    with pytest.raises(GPTImageRetryExhaustedError):
        call_with_retries(operation, max_attempts=2, initial_backoff_seconds=0.01)


def test_save_render_artifacts_writes_image_and_metadata(tmp_path: Path) -> None:
    """Storage helper should persist image bytes and metadata sidecar."""
    metadata = {"figure_id": "fig-001", "prompt": "test"}
    image_path, metadata_path = save_render_artifacts(
        tmp_path,
        stem="fig-001",
        image_bytes=MINIMAL_PNG_BYTES,
        mime_type="image/png",
        metadata=metadata,
    )

    assert image_path.exists()
    assert metadata_path.exists()
    assert image_path.read_bytes() == MINIMAL_PNG_BYTES
    saved = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert saved["figure_id"] == "fig-001"
    assert saved["image_path"] == str(image_path)


def test_render_scene_generates_image_and_metadata(tmp_path: Path) -> None:
    """Visual scene rendering should call backend and save artifacts."""
    scene = build_visual_scene(_compiled_graph())
    renderer = _renderer_with_stub(tmp_path)
    result = renderer.render_scene(scene)

    assert result.image_path is not None
    assert result.metadata_path is not None
    assert result.image_path.exists()
    assert result.metadata_path.exists()
    assert result.render_result.mime_type == "image/png"
    assert base64.b64decode(result.render_result.content) == MINIMAL_PNG_BYTES

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["figure_id"] == "fig-001"
    assert metadata["prompt_version"] == "1.0"
    assert "PROMPT_VERSION:" in metadata["prompt"]
    assert metadata["backend"] == "StubImageBackend"
    assert metadata["attempts"] == 1

    backend = renderer.backend
    assert isinstance(backend, StubImageBackend)
    assert len(backend.requests) == 1
    assert "structural_schematic_diagram" in backend.requests[0].prompt


def test_render_scene_retries_transient_backend_errors(tmp_path: Path) -> None:
    """Renderer should retry transient backend failures before succeeding."""
    scene = build_visual_scene(_compiled_graph())
    renderer = _renderer_with_stub(tmp_path, fail_until_attempt=2)
    result = renderer.render_scene(scene)

    assert result.attempts == 3
    backend = renderer.backend
    assert isinstance(backend, StubImageBackend)
    assert backend.attempts == 3
    assert result.image_path is not None


def test_render_graph_backward_compatible_with_renderer_interface(
    tmp_path: Path,
) -> None:
    """Graph-based render should satisfy the shared Renderer contract."""
    renderer = _renderer_with_stub(tmp_path)
    assert isinstance(renderer, Renderer)

    result = renderer.render(_compiled_graph())
    assert result.mime_type == "image/png"
    assert base64.b64decode(result.content) == MINIMAL_PNG_BYTES


def test_empty_graph_raises_render_error(tmp_path: Path) -> None:
    """Empty graphs cannot be rendered to raster images."""
    renderer = _renderer_with_stub(tmp_path)
    with pytest.raises(GPTImageRenderError):
        renderer.render(OntologyGraph())


def test_end_to_end_fsl_to_saved_image(tmp_path: Path) -> None:
    """Full pipeline: FSL -> graph -> scene -> prompt -> image + metadata on disk."""
    graph = compile_figure(parse(valid_document()))
    renderer = _renderer_with_stub(tmp_path, fail_until_attempt=0)

    scene = build_visual_scene(graph)
    prompt_spec = renderer._builder.build_from_scene(scene)
    result = renderer.render_scene(
        scene,
        options=GPTImageRenderOptions(
            output_dir=tmp_path,
            filename_stem="fig-001",
            max_retries=3,
            initial_backoff_seconds=0.01,
        ),
    )

    assert "PANEL[1]" in prompt_spec.prompt
    assert result.image_path == tmp_path / "fig-001.png"
    assert result.metadata_path == tmp_path / "fig-001.metadata.json"

    metadata = json.loads(result.metadata_path.read_text(encoding="utf-8"))
    assert metadata["figure_id"] == "fig-001"
    assert metadata["prompt"] == prompt_spec.prompt
    assert metadata["width"] == prompt_spec.width
    assert metadata["height"] == prompt_spec.height


def test_api_registers_gpt_image_renderer() -> None:
    """Public renderer registry should expose the raster GPT Image backend."""
    assert "gpt-image" in list_renderers()


def test_api_render_gpt_image_with_stub_backend(tmp_path: Path) -> None:
    """API render dispatch should work with a registered stub GPT Image renderer."""
    register_renderer(
        "gpt-image-test",
        lambda: create_gpt_image_renderer(
            backend=StubImageBackend(),
            output_dir=tmp_path,
            initial_backoff_seconds=0.01,
        ),
    )
    try:
        graph = _compiled_graph()
        response = render(
            graph.model_dump(mode="json"),
            renderer="gpt-image-test",
        )
        assert response.success is True
        assert response.mime_type == "image/png"
        assert base64.b64decode(response.content or "") == MINIMAL_PNG_BYTES
        assert (tmp_path / "fig-001.png").exists()
        assert (tmp_path / "fig-001.metadata.json").exists()
    finally:
        unregister_renderer("gpt-image-test")


def test_non_retryable_api_error_propagates(tmp_path: Path) -> None:
    """Non-retryable API errors should not be retried."""

    class FailingBackend(StubImageBackend):
        def generate(self, request):  # type: ignore[no-untyped-def]
            raise GPTImageAPIError("bad request", retryable=False)

    renderer = create_gpt_image_renderer(
        backend=FailingBackend(),
        output_dir=tmp_path,
        max_retries=3,
        initial_backoff_seconds=0.01,
    )
    scene = build_visual_scene(_compiled_graph())

    with pytest.raises(GPTImageAPIError, match="bad request"):
        renderer.render_scene(scene)