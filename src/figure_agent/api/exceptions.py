"""Exception hierarchy for the Figure Agent public API."""

from __future__ import annotations


class APIError(Exception):
    """Base exception for Figure Agent API failures."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "api_error",
        errors: list[str] | None = None,
    ) -> None:
        self.code = code
        self.errors = errors or []
        detail = message
        if self.errors:
            detail = f"{message}: {'; '.join(self.errors)}"
        super().__init__(detail)


class InvalidInputError(APIError):
    """Raised when API input cannot be parsed or coerced."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        super().__init__(message, code="invalid_input", errors=errors)


class CompilationAPIError(APIError):
    """Raised when FSL compilation fails."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        super().__init__(message, code="compilation_error", errors=errors)


class RenderAPIError(APIError):
    """Raised when rendering fails."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        super().__init__(message, code="render_error", errors=errors)


class UnknownRendererError(APIError):
    """Raised when a renderer name is not registered."""

    def __init__(self, renderer: str, *, available: list[str]) -> None:
        self.renderer = renderer
        self.available = available
        message = (
            f"Unknown renderer '{renderer}'; "
            f"available renderers: {', '.join(sorted(available)) or '(none)'}"
        )
        super().__init__(message, code="unknown_renderer")


class ExportAPIError(APIError):
    """Raised when export to disk fails."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        super().__init__(message, code="export_error", errors=errors)