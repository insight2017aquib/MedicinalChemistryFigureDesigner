"""GPT Image raster renderer using the shared prompt builder."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers.base import RenderConfig, RenderResult, Renderer
from figure_agent.renderers.gpt_image.backend import (
    ImageGenerationBackend,
    ImageGenerationRequest,
)
from figure_agent.renderers.gpt_image.exceptions import (
    GPTImagePromptBuildError,
    GPTImageRenderError,
)
from figure_agent.renderers.gpt_image.openai_backend import OpenAIImageBackend
from figure_agent.renderers.gpt_image.prompt_builder import (
    GPTImagePromptBuilder,
    ImagePromptSpec,
)
from figure_agent.renderers.gpt_image.retry import call_with_retries
from figure_agent.renderers.gpt_image.storage import (
    build_metadata_payload,
    save_render_artifacts,
)
from figure_agent.renderers.scene.builder import build_visual_scene
from figure_agent.renderers.scene.exceptions import SceneBuildError
from figure_agent.renderers.scene.models import VisualScene

IMAGE_PNG_MIME_TYPE = "image/png"


@dataclass(frozen=True)
class GPTImageRenderOptions:
    """Options specific to raster GPT Image rendering."""

    output_dir: Path | None = None
    filename_stem: str | None = None
    max_retries: int = 3
    initial_backoff_seconds: float = 0.5
    max_backoff_seconds: float = 8.0
    model: str = "gpt-image-1"


@dataclass(frozen=True)
class GPTImageRenderResult:
    """Full output from a GPT Image raster render."""

    render_result: RenderResult
    prompt_spec: ImagePromptSpec
    image_path: Path | None
    metadata_path: Path | None
    metadata: dict[str, Any]
    attempts: int


class GPTImageRenderer(Renderer):
    """Render visual scenes to raster images via a pluggable generation backend.

    Uses ``GPTImagePromptBuilder`` for deterministic prompt construction, then
    calls an ``ImageGenerationBackend`` (OpenAI API by default, stub for tests).
    """

    def __init__(
        self,
        *,
        builder: GPTImagePromptBuilder | None = None,
        backend: ImageGenerationBackend | None = None,
        options: GPTImageRenderOptions | None = None,
    ) -> None:
        self._builder = builder or GPTImagePromptBuilder()
        self._backend = backend
        self._options = options or GPTImageRenderOptions()

    @property
    def backend(self) -> ImageGenerationBackend:
        """Return the configured backend, defaulting to OpenAI when unset."""
        if self._backend is None:
            self._backend = OpenAIImageBackend(model=self._options.model)
        return self._backend

    def render(
        self,
        graph: OntologyGraph,
        *,
        config: RenderConfig | None = None,
    ) -> RenderResult:
        """Render an ontology graph to a raster image."""
        if not graph.entities:
            raise GPTImageRenderError("Cannot render an empty ontology graph")

        try:
            scene = build_visual_scene(graph, config=config)
        except SceneBuildError as exc:
            raise GPTImageRenderError(str(exc)) from exc

        return self.render_scene(scene).render_result

    def render_scene(
        self,
        scene: VisualScene,
        *,
        options: GPTImageRenderOptions | None = None,
    ) -> GPTImageRenderResult:
        """Render a visual scene to a raster image."""
        opts = options or self._options
        try:
            prompt_spec = self._builder.build_from_scene(scene)
        except GPTImagePromptBuildError as exc:
            raise GPTImageRenderError(str(exc)) from exc

        backend = self.backend
        request = ImageGenerationRequest(
            prompt=prompt_spec.prompt,
            width=int(prompt_spec.width),
            height=int(prompt_spec.height),
            model=opts.model,
        )

        attempts = 0

        def _generate() -> Any:
            nonlocal attempts
            attempts += 1
            return backend.generate(request)

        generation = call_with_retries(
            _generate,
            max_attempts=opts.max_retries,
            initial_backoff_seconds=opts.initial_backoff_seconds,
            max_backoff_seconds=opts.max_backoff_seconds,
        )

        image_path: Path | None = None
        metadata_path: Path | None = None
        metadata = build_metadata_payload(
            figure_id=scene.figure_id or "figure",
            prompt=prompt_spec.prompt,
            prompt_version=prompt_spec.version,
            width=prompt_spec.width,
            height=prompt_spec.height,
            mime_type=generation.mime_type,
            model=generation.model,
            backend=backend.__class__.__name__,
            revised_prompt=generation.revised_prompt,
            attempts=attempts,
        )

        if opts.output_dir is not None:
            stem = opts.filename_stem or scene.figure_id or "figure"
            image_path, metadata_path = save_render_artifacts(
                opts.output_dir,
                stem=stem,
                image_bytes=generation.image_bytes,
                mime_type=generation.mime_type,
                metadata=metadata,
            )
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        encoded = base64.b64encode(generation.image_bytes).decode("ascii")
        render_result = RenderResult(
            content=encoded,
            width=prompt_spec.width,
            height=prompt_spec.height,
            mime_type=generation.mime_type,
        )
        return GPTImageRenderResult(
            render_result=render_result,
            prompt_spec=prompt_spec,
            image_path=image_path,
            metadata_path=metadata_path,
            metadata=metadata,
            attempts=attempts,
        )


def create_gpt_image_renderer(
    *,
    backend: ImageGenerationBackend | None = None,
    output_dir: Path | str | None = None,
    **kwargs: Any,
) -> GPTImageRenderer:
    """Factory helper for configuring a GPT Image renderer."""
    options_kwargs: dict[str, Any] = {}
    if output_dir is not None:
        options_kwargs["output_dir"] = Path(output_dir)
    options_kwargs.update(kwargs)
    options = GPTImageRenderOptions(**options_kwargs)
    return GPTImageRenderer(backend=backend, options=options)