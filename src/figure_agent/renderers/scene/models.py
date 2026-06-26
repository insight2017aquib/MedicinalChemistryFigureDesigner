"""Renderer-independent visual scene model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from figure_agent.ontology.enums import EntityType
from figure_agent.renderers.geometry import Point, Rect

SCENE_VERSION = "1.0"


class PrimitiveKind(StrEnum):
    """Structural primitive types independent of any renderer backend."""

    PANEL_BOUNDARY = "panel_boundary"
    RECTANGLE = "rectangle"
    ROUNDED_RECTANGLE = "rounded_rectangle"
    TEXT_LABEL = "text_label"
    ARROW = "arrow"
    STYLE_REFERENCE = "style_reference"


class ConnectorKind(StrEnum):
    """Connector types between scene elements."""

    STRAIGHT = "straight"
    INLINE = "inline"


class LabelAnchor(StrEnum):
    """Text label anchor positions."""

    START = "start"
    MIDDLE = "middle"
    END = "end"


@dataclass(frozen=True)
class ScenePalette:
    """Renderer-agnostic color palette for a scene."""

    background: str
    fill: str
    fill_container: str
    stroke: str
    text: str
    arrow: str


@dataclass(frozen=True)
class SceneStyle:
    """Styling metadata carried with a visual scene."""

    palette: ScenePalette
    stroke_width: float
    corner_radius: float
    font_family: str
    font_size: float


@dataclass(frozen=True)
class VisualLabel:
    """Text label attached to a primitive or panel."""

    text: str
    anchor: LabelAnchor
    position: Point


@dataclass(frozen=True)
class VisualPrimitive:
    """A drawable primitive with bounds and optional label."""

    id: str
    kind: PrimitiveKind
    bounds: Rect
    label: VisualLabel | None = None
    panel_id: str | None = None
    entity_type: EntityType | None = None


@dataclass(frozen=True)
class VisualConnector:
    """A connector between two primitives by identifier."""

    id: str
    kind: ConnectorKind
    source_id: str
    target_id: str


@dataclass(frozen=True)
class VisualGroup:
    """Logical grouping of primitives (e.g. panel contents)."""

    id: str
    member_ids: tuple[str, ...]


@dataclass(frozen=True)
class VisualPanel:
    """Panel region containing child primitives."""

    id: str
    bounds: Rect
    title: VisualLabel
    primitive_ids: tuple[str, ...]


@dataclass(frozen=True)
class StyleReference:
    """External style file reference displayed in the scene."""

    id: str
    path: str
    bounds: Rect


@dataclass(frozen=True)
class VisualScene:
    """Complete renderer-independent visual description of a figure."""

    version: str
    figure_id: str
    title: str
    layout_type: str
    canvas_width: float
    canvas_height: float
    style: SceneStyle
    panels: tuple[VisualPanel, ...]
    primitives: tuple[VisualPrimitive, ...]
    connectors: tuple[VisualConnector, ...]
    groups: tuple[VisualGroup, ...]
    style_references: tuple[StyleReference, ...]

    def primitive_by_id(self) -> dict[str, VisualPrimitive]:
        """Return primitives indexed by identifier."""
        return {primitive.id: primitive for primitive in self.primitives}