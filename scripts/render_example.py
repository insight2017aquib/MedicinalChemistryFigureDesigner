#!/usr/bin/env python3
"""Render a minimal FSL example through the Figure Agent public API."""

from __future__ import annotations

from pathlib import Path

from figure_agent import export, health, load_yaml, parse, version

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT = REPO_ROOT / "examples" / "minimal_figure.yaml"
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_FILE = OUTPUT_DIR / "example.svg"


def main() -> None:
    """Load, validate, compile, render, and write an example SVG via the API."""
    print(health())
    print(version())

    figure = parse(load_yaml(INPUT))
    result = export(figure, OUTPUT_FILE)

    if not result.success:
        raise SystemExit(f"Export failed: {', '.join(result.errors)}")

    print(f"Wrote {result.path}")


if __name__ == "__main__":
    main()