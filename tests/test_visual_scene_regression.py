"""Regression tests for visual-scene-based rendering and prompt generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from figure_agent import compile_figure, load_yaml, parse
from figure_agent.renderers import GPTImagePromptBuilder, SVGRenderer, build_visual_scene
from helpers import valid_document

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "visual_scene_regression"
MINIMAL_FIGURE = REPO_ROOT / "examples" / "minimal_figure.yaml"


def _read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")


def _multi_panel_graph():
    document = valid_document()
    document["layout"]["type"] = "multi-panel"
    document["layout"]["panels"] = [
        {"id": "panel-a", "zones": ["left"], "object_refs": ["slot-1"]},
        {"id": "panel-b", "zones": ["right"], "object_refs": ["slot-2"]},
    ]
    document["content_slots"].append(
        {"id": "slot-2", "label": "Secondary", "type": "shape", "value": None}
    )
    return compile_figure(parse(document))


@pytest.mark.parametrize(
    ("graph_factory", "svg_fixture", "prompt_fixture"),
    [
        (
            lambda: compile_figure(parse(load_yaml(MINIMAL_FIGURE))),
            "minimal.svg",
            "minimal.prompt.txt",
        ),
        (
            lambda: compile_figure(parse(valid_document())),
            "valid.svg",
            "valid.prompt.txt",
        ),
        (_multi_panel_graph, "multi_panel.svg", "multi_panel.prompt.txt"),
    ],
    ids=["minimal", "valid", "multi_panel"],
)
def test_svg_output_matches_golden_fixture(
    graph_factory,
    svg_fixture: str,
    prompt_fixture: str,
) -> None:
    """SVG rendering via visual scene must match pre-refactor golden output."""
    del prompt_fixture
    graph = graph_factory()
    scene = build_visual_scene(graph)
    result = SVGRenderer().render_scene(scene)

    expected = _read_fixture(svg_fixture)
    assert result.content == expected


@pytest.mark.parametrize(
    ("graph_factory", "prompt_fixture"),
    [
        (
            lambda: compile_figure(parse(load_yaml(MINIMAL_FIGURE))),
            "minimal.prompt.txt",
        ),
        (
            lambda: compile_figure(parse(valid_document())),
            "valid.prompt.txt",
        ),
        (_multi_panel_graph, "multi_panel.prompt.txt"),
    ],
    ids=["minimal", "valid", "multi_panel"],
)
def test_prompt_output_matches_golden_fixture(graph_factory, prompt_fixture: str) -> None:
    """Prompt generation via visual scene must match pre-refactor golden output."""
    graph = graph_factory()
    scene = build_visual_scene(graph)
    spec = GPTImagePromptBuilder().build_from_scene(scene)

    expected = _read_fixture(prompt_fixture)
    assert spec.prompt == expected


@pytest.mark.parametrize(
    ("graph_factory", "svg_fixture", "prompt_fixture"),
    [
        (
            lambda: compile_figure(parse(load_yaml(MINIMAL_FIGURE))),
            "minimal.svg",
            "minimal.prompt.txt",
        ),
        (
            lambda: compile_figure(parse(valid_document())),
            "valid.svg",
            "valid.prompt.txt",
        ),
        (_multi_panel_graph, "multi_panel.svg", "multi_panel.prompt.txt"),
    ],
    ids=["minimal", "valid", "multi_panel"],
)
def test_backward_compatible_render_paths_match_golden(
    graph_factory,
    svg_fixture: str,
    prompt_fixture: str,
) -> None:
    """Public graph-based APIs must still produce identical golden output."""
    graph = graph_factory()

    svg_result = SVGRenderer().render(graph)
    prompt_result = GPTImagePromptBuilder().build(graph)

    assert svg_result.content == _read_fixture(svg_fixture)
    assert prompt_result.prompt == _read_fixture(prompt_fixture)