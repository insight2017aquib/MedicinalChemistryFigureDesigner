"""Configuration for the Figure Agent MCP server."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from figure_agent.renderers.gpt_image.backend import ImageGenerationBackend, StubImageBackend


def _default_gpt_image_backend_factory() -> ImageGenerationBackend:
    """Return OpenAI backend when configured, otherwise a deterministic stub."""
    if os.environ.get("OPENAI_API_KEY"):
        from figure_agent.renderers.gpt_image.openai_backend import OpenAIImageBackend

        return OpenAIImageBackend()
    return StubImageBackend()


@dataclass(frozen=True)
class MCPServerConfig:
    """Runtime configuration for MCP tool orchestration."""

    output_dir: Path = field(default_factory=lambda: Path("output/mcp"))
    default_renderer: str = "svg"
    api_version: str = "1.0"
    gpt_image_backend_factory: Callable[[], ImageGenerationBackend] = field(
        default_factory=lambda: _default_gpt_image_backend_factory
    )

    def __post_init__(self) -> None:
        if not self.default_renderer.strip():
            raise ValueError("default_renderer must not be empty")