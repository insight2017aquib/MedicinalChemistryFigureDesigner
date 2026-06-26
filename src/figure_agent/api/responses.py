"""Response models for the Figure Agent public API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationResponse:
    """Result of FSL validation."""

    valid: bool
    errors: tuple[str, ...] = ()
    figure: dict[str, Any] | None = None


@dataclass(frozen=True)
class GenerateFSLResponse:
    """Result of FSL document generation."""

    document: dict[str, Any]
    yaml: str
    json: str


@dataclass(frozen=True)
class CompileResponse:
    """Result of compiling an FSL figure into an ontology graph."""

    success: bool
    graph: dict[str, Any] | None = None
    entity_count: int = 0
    relationship_count: int = 0
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class RenderResponse:
    """Result of rendering an ontology graph."""

    success: bool
    content: str | None = None
    width: float = 0.0
    height: float = 0.0
    mime_type: str = ""
    renderer: str = ""
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExportResponse:
    """Result of exporting a rendered figure to disk."""

    success: bool
    path: str | None = None
    format: str | None = None
    renderer: str = ""
    errors: tuple[str, ...] = ()


@dataclass(frozen=True)
class HealthResponse:
    """Service health and capability report."""

    status: str
    version: str
    components: dict[str, str] = field(default_factory=dict)
    renderers: tuple[str, ...] = ()


@dataclass(frozen=True)
class VersionResponse:
    """Package version and API surface metadata."""

    version: str
    api_version: str
    fsl_versions: tuple[str, ...]
    renderers: tuple[str, ...]