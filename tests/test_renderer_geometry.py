"""Tests for renderer geometry helpers."""

from __future__ import annotations

from figure_agent.renderers.geometry import (
    ArrowSegment,
    Point,
    Rect,
    Size,
    center_text_position,
    stack_rects,
)


def test_stack_rects_vertical_spacing() -> None:
    """Stacked rectangles should use constant vertical spacing."""
    rects = stack_rects(
        Point(10, 10),
        Size(100, 20),
        3,
        spacing=8,
    )

    assert len(rects) == 3
    assert rects[0].y == 10
    assert rects[1].y == 38
    assert rects[2].y == 66


def test_center_text_position_is_inside_rect() -> None:
    """Centered text position should fall within the target rectangle."""
    rect = Rect(0, 0, 100, 40)
    point = center_text_position(rect, "Label", font_size=12)

    assert 0 <= point.x <= rect.width
    assert 0 <= point.y <= rect.height


def test_arrow_segment_head_points() -> None:
    """Arrow segment should provide three head triangle points."""
    segment = ArrowSegment(start=Point(0, 0), end=Point(100, 0))
    left, tip, right = segment.head_points()

    assert tip.x == 100
    assert left.x < tip.x
    assert right.x < tip.x
