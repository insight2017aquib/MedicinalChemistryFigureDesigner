"""Core constants and shared type aliases for the figure agent."""

from figure_agent.core.constants import (
    KNOWN_LAYOUT_TYPES,
    KNOWN_TEMPLATES,
    SUPPORTED_FSL_VERSIONS,
)
from figure_agent.core.types import (
    FigureId,
    LayoutType,
    ObjectId,
    PanelId,
    SlotId,
    TemplatePath,
)

__all__ = [
    "FigureId",
    "KNOWN_LAYOUT_TYPES",
    "KNOWN_TEMPLATES",
    "LayoutType",
    "ObjectId",
    "PanelId",
    "SUPPORTED_FSL_VERSIONS",
    "SlotId",
    "TemplatePath",
]
