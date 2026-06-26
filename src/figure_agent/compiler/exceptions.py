"""Exception hierarchy for the figure compilation layer."""

from __future__ import annotations


class CompilationError(Exception):
    """Base exception for figure compilation errors."""


class CompilationMappingError(CompilationError):
    """Raised when an FSL object cannot be mapped to an ontology entity."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        if self.errors:
            joined = "; ".join(self.errors)
            super().__init__(f"{message}: {joined}")
        else:
            super().__init__(message)


class CompilationValidationError(CompilationError):
    """Raised when compiled output fails structural validation."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        if self.errors:
            joined = "; ".join(self.errors)
            super().__init__(f"{message}: {joined}")
        else:
            super().__init__(message)
