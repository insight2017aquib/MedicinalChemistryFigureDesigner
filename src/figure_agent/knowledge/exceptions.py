"""Exception hierarchy for knowledge pack loading and validation."""

from __future__ import annotations


class KnowledgePackError(Exception):
    """Base exception for knowledge pack operations."""


class KnowledgePackParseError(KnowledgePackError):
    """Raised when a pack manifest cannot be parsed."""

    def __init__(self, message: str, *, source: str | None = None) -> None:
        detail = f"{message} (source: {source})" if source else message
        super().__init__(detail)
        self.source = source


class KnowledgePackSchemaError(KnowledgePackError):
    """Raised when a pack fails structural schema validation."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        if self.errors:
            joined = "; ".join(self.errors)
            super().__init__(f"{message}: {joined}")
        else:
            super().__init__(message)


class KnowledgePackValidationError(KnowledgePackError):
    """Raised when a pack fails semantic validation."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        if self.errors:
            joined = "; ".join(self.errors)
            super().__init__(f"{message}: {joined}")
        else:
            super().__init__(message)


class KnowledgePackResolutionError(KnowledgePackError):
    """Raised when inheritance or dependency resolution fails."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        if self.errors:
            joined = "; ".join(self.errors)
            super().__init__(f"{message}: {joined}")
        else:
            super().__init__(message)