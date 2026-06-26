"""Monochrome styling constants for proof-of-concept renderers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MonochromePalette:
    """Simple monochrome palette for SVG output."""

    background: str = "#ffffff"
    stroke: str = "#000000"
    fill: str = "#ffffff"
    fill_container: str = "#f5f5f5"
    text: str = "#000000"
    arrow: str = "#000000"


DEFAULT_PALETTE = MonochromePalette()

DEFAULT_FONT_FAMILY = "Arial, Helvetica, sans-serif"
DEFAULT_FONT_SIZE = 12
DEFAULT_STROKE_WIDTH = 1.5
DEFAULT_CORNER_RADIUS = 8.0
