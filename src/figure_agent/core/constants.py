"""Repository-aligned constants for FSL validation."""

from __future__ import annotations

SUPPORTED_FSL_VERSIONS: frozenset[str] = frozenset({"0.3.0", "0.2.0-draft"})

KNOWN_TEMPLATES: frozenset[str] = frozenset(
    {
        "templates/single-panel.md",
        "templates/multi-panel.md",
        "templates/schematic-flow.md",
        "templates/comparison-layout.md",
        "templates/legend-block.md",
    }
)

KNOWN_LAYOUT_TYPES: frozenset[str] = frozenset(
    {
        "single-panel",
        "multi-panel",
        "schematic-flow",
        "comparison-layout",
    }
)

LAYOUT_PANEL_RULES: dict[str, tuple[int, int | None]] = {
    # layout type -> (minimum panels, maximum panels or None for unbounded)
    "single-panel": (1, 1),
    "multi-panel": (2, None),
    "schematic-flow": (1, None),
    "comparison-layout": (2, None),
}
