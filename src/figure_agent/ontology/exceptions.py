"""Exception hierarchy for the ontology layer."""

from __future__ import annotations


class OntologyError(Exception):
    """Base exception for ontology layer errors."""


class OntologyRegistryError(OntologyError):
    """Raised when entity type registration or lookup fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class OntologyValidationError(OntologyError):
    """Raised when an ontology graph fails structural validation."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        self.errors = errors or []
        if self.errors:
            joined = "; ".join(self.errors)
            super().__init__(f"{message}: {joined}")
        else:
            super().__init__(message)


class OntologySerializationError(OntologyError):
    """Raised when ontology serialization or deserialization fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
