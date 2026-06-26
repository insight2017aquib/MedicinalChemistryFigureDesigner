"""Exception hierarchy for the FSL engine."""

from __future__ import annotations


class FSLError(Exception):
    """Base exception for all FSL engine errors."""


class FSLParseError(FSLError):
    """Raised when raw input cannot be parsed into a data structure."""

    def __init__(self, message: str, *, source: str | None = None) -> None:
        detail = f"{message} (source: {source})" if source else message
        super().__init__(detail)
        self.source = source


class FSLSchemaError(FSLError):
    """Raised when data fails structural or type schema validation."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        if self.errors:
            joined = "; ".join(self.errors)
            super().__init__(f"{message}: {joined}")
        else:
            super().__init__(message)


class FSLValidationError(FSLError):
    """Raised when a parsed figure fails semantic validation."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        if self.errors:
            joined = "; ".join(self.errors)
            super().__init__(f"{message}: {joined}")
        else:
            super().__init__(message)
