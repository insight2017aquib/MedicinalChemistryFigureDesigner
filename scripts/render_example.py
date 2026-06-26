#!/usr/bin/env python3
"""Render a minimal FSL example through the full pipeline to SVG."""

from __future__ import annotations

from pathlib import Path

from figure_agent import compile_figure, load_yaml, parse
from figure_agent.renderers import SVGRenderer

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT = REPO_ROOT / "examples" / "minimal_figure.yaml"
OUTPUT_DIR = REPO_ROOT / "output"
OUTPUT_FILE = OUTPUT_DIR / "example.svg"


def main() -> None:
    """Load, parse, compile, render, and write an example SVG."""
    figure = parse(load_yaml(INPUT))
    graph = compile_figure(figure)
    result = SVGRenderer().render(graph)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(result.content, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
