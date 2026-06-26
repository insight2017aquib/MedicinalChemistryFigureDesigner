"""Geometry helpers for layout and SVG element placement."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Point:
    """A 2D point."""

    x: float
    y: float


@dataclass(frozen=True)
class Size:
    """Width and height dimensions."""

    width: float
    height: float


@dataclass(frozen=True)
class Rect:
    """An axis-aligned rectangle."""

    x: float
    y: float
    width: float
    height: float

    @property
    def center(self) -> Point:
        """Return the rectangle center point."""
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    @property
    def bottom_center(self) -> Point:
        """Return the bottom-center point."""
        return Point(self.x + self.width / 2, self.y + self.height)

    @property
    def top_center(self) -> Point:
        """Return the top-center point."""
        return Point(self.x + self.width / 2, self.y)


@dataclass(frozen=True)
class ArrowSegment:
    """A straight arrow between two points."""

    start: Point
    end: Point
    head_size: float = 8.0

    def line_points(self) -> tuple[Point, Point]:
        """Return line endpoints stopping before the arrowhead."""
        angle = math.atan2(self.end.y - self.start.y, self.end.x - self.start.x)
        stop_x = self.end.x - self.head_size * math.cos(angle)
        stop_y = self.end.y - self.head_size * math.sin(angle)
        return self.start, Point(stop_x, stop_y)

    def head_points(self) -> tuple[Point, Point, Point]:
        """Return the three points of the arrowhead triangle."""
        angle = math.atan2(self.end.y - self.start.y, self.end.x - self.start.x)
        left_angle = angle + math.pi * 0.85
        right_angle = angle - math.pi * 0.85
        left = Point(
            self.end.x + self.head_size * math.cos(left_angle),
            self.end.y + self.head_size * math.sin(left_angle),
        )
        right = Point(
            self.end.x + self.head_size * math.cos(right_angle),
            self.end.y + self.head_size * math.sin(right_angle),
        )
        return left, self.end, right


def center_text_position(rect: Rect, text: str, *, font_size: float) -> Point:
    """Compute centered text anchor position within a rectangle."""
    del text  # Length-based centering is handled by text-anchor in SVG.
    return Point(rect.center.x, rect.center.y + font_size * 0.35)


def stack_rects(
    origin: Point,
    item_size: Size,
    count: int,
    *,
    spacing: float,
) -> list[Rect]:
    """Stack rectangles vertically with constant spacing."""
    rects: list[Rect] = []
    current_y = origin.y
    for _ in range(count):
        rects.append(Rect(origin.x, current_y, item_size.width, item_size.height))
        current_y += item_size.height + spacing
    return rects
