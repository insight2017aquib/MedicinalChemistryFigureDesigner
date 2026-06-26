"""Exception hierarchy for GPT Image prompt and raster rendering."""

from __future__ import annotations

from figure_agent.renderers.exceptions import GPTImagePromptError, RenderError


class GPTImagePromptBuildError(GPTImagePromptError):
    """Raised when an ontology graph cannot be converted to a prompt."""


class GPTImageRenderError(RenderError):
    """Raised when raster GPT Image rendering fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class GPTImageAPIError(GPTImageRenderError):
    """Raised when an image generation API call fails."""

    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status_code = status_code


class GPTImageRetryExhaustedError(GPTImageAPIError):
    """Raised when retry attempts are exhausted."""


class GPTImageStorageError(GPTImageRenderError):
    """Raised when image or metadata persistence fails."""