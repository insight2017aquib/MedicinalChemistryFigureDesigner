"""Tests for GPT Image prompt builder and renderer."""

from __future__ import annotations

from pathlib import Path

import pytest

from figure_agent import compile_figure, load_yaml, parse, render
from figure_agent.renderers import (
    GPTImagePromptBuilder,
    GPTImagePromptRenderer,
    Renderer,
)
from figure_agent.renderers.gpt_image import PROMPT_VERSION, GPTImagePromptBuildError
from figure_agent.renderers.gpt_image.renderer import IMAGE_PROMPT_MIME_TYPE
from helpers import valid_document

REPO_ROOT = Path(__file__).resolve().parents[1]
MINIMAL_FIGURE = REPO_ROOT / "examples" / "minimal_figure.yaml"


def _compiled_graph():
    figure = parse(load_yaml(MINIMAL_FIGURE))
    return compile_figure(figure)


def test_prompt_generation_is_deterministic() -> None:
    """Identical graphs must produce byte-identical prompts."""
    graph = _compiled_graph()
    builder = GPTImagePromptBuilder()

    first = builder.build(graph)
    second = builder.build(graph)

    assert first.prompt == second.prompt
    assert first.version == second.version == PROMPT_VERSION
    assert first.width == second.width
    assert first.height == second.height


def test_minimal_figure_prompt_contains_structural_sections() -> None:
    """Prompt should describe panels, labels, and constraints without biology."""
    graph = _compiled_graph()
    spec = GPTImagePromptBuilder().build(graph)

    assert "PROMPT_VERSION:" in spec.prompt
    assert "TASK: structural_schematic_diagram" in spec.prompt
    assert "PANEL[1]" in spec.prompt
    assert "primitive=text_label" in spec.prompt
    assert "label='Primary content'" in spec.prompt
    assert "do not add biology or chemistry iconography" in spec.prompt
    assert "protein" not in spec.prompt.lower()
    assert "dna" not in spec.prompt.lower()


def test_style_references_included() -> None:
    """Style annotation entities should appear as STYLE_REFERENCES."""
    graph = _compiled_graph()
    spec = GPTImagePromptBuilder().build(graph)

    assert "STYLE_REFERENCES:" in spec.prompt
    assert "styles/color-system.md" in spec.prompt


def test_multi_panel_prompt_lists_multiple_panels() -> None:
    """Multi-panel graphs should emit sorted panel sections."""
    document = valid_document()
    document["layout"]["type"] = "multi-panel"
    document["layout"]["panels"] = [
        {"id": "panel-b", "zones": ["right"], "object_refs": ["slot-2"]},
        {"id": "panel-a", "zones": ["left"], "object_refs": ["slot-1"]},
    ]
    document["content_slots"].append(
        {"id": "slot-2", "label": "Secondary", "type": "shape", "value": None}
    )
    document["template"]["ref"] = "templates/multi-panel.md"

    graph = compile_figure(parse(document))
    spec = GPTImagePromptBuilder().build(graph)

    panel_a_index = spec.prompt.index("id=panel-a")
    panel_b_index = spec.prompt.index("id=panel-b")
    assert panel_a_index < panel_b_index


def test_scientific_entity_types_map_to_generic_primitives() -> None:
    """Protein slots must not produce biological prompt language."""
    document = valid_document()
    document["content_slots"][0]["type"] = "protein"
    document["content_slots"][0]["label"] = "User-supplied structure"

    graph = compile_figure(parse(document))
    spec = GPTImagePromptBuilder().build(graph)

    assert "primitive=rectangle" in spec.prompt
    assert "protein" not in spec.prompt.lower()


def test_arrow_slot_appears_in_prompt() -> None:
    """Arrow entities should use straight_arrow primitive."""
    document = valid_document()
    document["content_slots"][0]["type"] = "arrow"
    document["content_slots"][0]["label"] = "Connection"

    graph = compile_figure(parse(document))
    spec = GPTImagePromptBuilder().build(graph)

    assert "primitive=straight_arrow" in spec.prompt


def test_renderer_implements_renderer_interface() -> None:
    """GPTImagePromptRenderer must satisfy the abstract Renderer contract."""
    renderer = GPTImagePromptRenderer()
    assert isinstance(renderer, Renderer)


def test_renderer_returns_render_result() -> None:
    """Renderer output should use image-prompt mime type and text content."""
    graph = _compiled_graph()
    result = GPTImagePromptRenderer().render(graph)

    assert result.mime_type == IMAGE_PROMPT_MIME_TYPE
    assert "PROMPT_VERSION:" in result.content
    assert result.width > 0
    assert result.height > 0


def test_api_render_gptimage_backend() -> None:
    """Public API should dispatch gptimage renderer."""
    graph = _compiled_graph()
    graph_dict = graph.model_dump(mode="json")
    result = render(graph_dict, renderer="gptimage")

    assert result.success is True
    assert result.renderer == "gptimage"
    assert result.content
    assert "structural_schematic_diagram" in result.content


def test_empty_graph_raises_build_error() -> None:
    """Empty graphs cannot produce prompts."""
    from figure_agent.ontology.relationships import OntologyGraph

    with pytest.raises(GPTImagePromptBuildError):
        GPTImagePromptBuilder().build(OntologyGraph(entities=[], relationships=[]))


def test_prompt_byte_stable_across_builder_instances() -> None:
    """Different builder instances must produce identical output."""
    graph = _compiled_graph()
    prompt_a = GPTImagePromptBuilder().build(graph).prompt
    prompt_b = GPTImagePromptBuilder().build(graph).prompt
    assert prompt_a == prompt_b