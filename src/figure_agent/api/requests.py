"""Request models for the Figure Agent public API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ContentSlotSpec:
    """Specification for a content slot in a generated FSL document."""

    id: str
    label: str | None = None
    type: str = "placeholder"
    value: Any = None


@dataclass(frozen=True)
class GenerateFSLRequest:
    """Parameters for generating a minimal valid FSL document."""

    figure_id: str = "fig-001"
    title: str = "Untitled Figure"
    author: str | None = "maintainer"
    layout_type: str = "single-panel"
    template_ref: str = "templates/single-panel.md"
    panel_id: str = "panel-a"
    slots: tuple[ContentSlotSpec, ...] = (
        ContentSlotSpec(id="slot-1", label="Primary content"),
    )
    style_ref: str = "styles/color-system.md"
    export_formats: tuple[str, ...] = ("svg",)


@dataclass(frozen=True)
class RenderRequest:
    """Parameters for rendering an ontology graph or FSL source."""

    renderer: str = "svg"
    width: float | None = None
    height: float | None = None
    margin: float | None = None


@dataclass(frozen=True)
class ExportRequest:
    """Parameters for exporting a rendered figure to disk."""

    output_path: str
    renderer: str = "svg"
    format: str | None = None
    width: float | None = None
    height: float | None = None
    margin: float | None = None


@dataclass(frozen=True)
class ValidateFSLRequest:
    """Options for FSL validation."""

    semantic: bool = True