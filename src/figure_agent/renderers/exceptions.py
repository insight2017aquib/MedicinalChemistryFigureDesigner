"""Exception hierarchy for the rendering layer."""

from __future__ import annotations


class RenderError(Exception):
    """Base exception for renderer errors."""


class LayoutError(RenderError):
    """Raised when an ontology graph cannot be laid out."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class SVGRenderError(RenderError):
    """Raised when SVG generation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class GPTImagePromptError(RenderError):
    """Raised when image prompt generation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
