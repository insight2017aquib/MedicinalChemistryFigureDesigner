"""GPT Image prompt renderer implementing the shared Renderer interface."""

from __future__ import annotations

from figure_agent.ontology.relationships import OntologyGraph
from figure_agent.renderers.base import RenderConfig, RenderResult, Renderer
from figure_agent.renderers.gpt_image.exceptions import GPTImagePromptBuildError
from figure_agent.renderers.gpt_image.prompt_builder import GPTImagePromptBuilder

IMAGE_PROMPT_MIME_TYPE = "text/vnd.figure-agent.image-prompt"


class GPTImagePromptRenderer(Renderer):
    """Renderer that emits deterministic image prompts instead of raster output.

    Implements ``Renderer`` so the prompt builder plugs into ``render(renderer=...)``
    alongside SVG and future backends.
    """

    def __init__(self, *, builder: GPTImagePromptBuilder | None = None) -> None:
        self._builder = builder or GPTImagePromptBuilder()

    def render(
        self,
        graph: OntologyGraph,
        *,
        config: RenderConfig | None = None,
    ) -> RenderResult:
        """Render an ontology graph to a deterministic image prompt."""
        try:
            spec = self._builder.build(graph, config=config)
        except GPTImagePromptBuildError:
            raise
        except Exception as exc:
            raise GPTImagePromptBuildError(
                f"Failed to build image prompt: {exc}"
            ) from exc
        else:
            return RenderResult(
                content=spec.prompt,
                width=spec.width,
                height=spec.height,
                mime_type=IMAGE_PROMPT_MIME_TYPE,
            )