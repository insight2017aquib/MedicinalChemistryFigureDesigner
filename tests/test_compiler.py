"""Tests for the FSL-to-ontology figure compiler."""

from __future__ import annotations

from pathlib import Path

import pytest

from figure_agent.compiler import (
    CompilationValidationError,
    FigureCompiler,
    compile_figure,
)
from figure_agent.fsl.parser import load_yaml, parse, validate_schema
from figure_agent.ontology import OntologyValidator, RelationshipType
from helpers import valid_document

REPO_ROOT = Path(__file__).resolve().parents[1]
MINIMAL_FIGURE = REPO_ROOT / "examples" / "minimal_figure.yaml"


def multi_panel_document() -> dict:
    """Return a valid multi-panel FSL document."""
    document = valid_document()
    document["layout"]["type"] = "multi-panel"
    document["layout"]["panels"] = [
        {
            "id": "panel-a",
            "zones": ["left"],
            "object_refs": ["slot-1"],
        },
        {
            "id": "panel-b",
            "zones": ["right"],
            "object_refs": ["slot-2"],
        },
    ]
    document["content_slots"].append(
        {
            "id": "slot-2",
            "label": "Secondary content",
            "type": "shape",
            "value": None,
        }
    )
    return document


def test_compile_simple_figure() -> None:
    """A minimal FSL figure should compile into a valid ontology graph."""
    figure = parse(load_yaml(MINIMAL_FIGURE))
    graph = compile_figure(figure)

    assert len(graph.entities) == 4  # figure, panel, slot, style annotation
    assert len(graph.relationships) == 3  # figure->panel, panel->slot, figure->style

    root = next(entity for entity in graph.entities if ":figure:" in entity.id)
    assert root.metadata["layout_type"] == "single-panel"


def test_compile_multi_panel_figure() -> None:
    """Multi-panel layouts should produce panel entities and contains relationships."""
    figure = parse(multi_panel_document())
    graph = compile_figure(figure)

    panel_entities = [
        entity
        for entity in graph.entities
        if entity.id.endswith(":panel:panel-a") or entity.id.endswith(":panel:panel-b")
    ]
    contains_relationships = [
        rel for rel in graph.relationships if rel.type == RelationshipType.CONTAINS
    ]

    assert len(panel_entities) == 2
    assert len(contains_relationships) == 4  # 2 figure->panel, 2 panel->slot


def test_layout_metadata_mapped_to_root_entity() -> None:
    """Layout and template metadata should be attached to the figure root entity."""
    figure = parse(valid_document())
    graph = compile_figure(figure)

    root = next(entity for entity in graph.entities if ":figure:" in entity.id)

    assert root.metadata["layout_type"] == "single-panel"
    assert root.metadata["template_ref"] == "templates/single-panel.md"
    assert root.metadata["template_params"] == {"aspect_ratio": "4:3"}


def test_missing_panel_reference_raises_validation_error() -> None:
    """Panels referencing unknown slots should fail compilation validation."""
    document = valid_document()
    document["layout"]["panels"][0]["object_refs"] = ["missing-slot"]

    # Schema-only parse isolates compiler validation from FSL semantic checks.
    figure = validate_schema(document)

    with pytest.raises(CompilationValidationError) as exc_info:
        compile_figure(figure)

    assert "unknown content slot 'missing-slot'" in str(exc_info.value)


def test_orphan_slot_raises_validation_error() -> None:
    """Content slots not referenced by any panel should fail compilation."""
    document = valid_document()
    document["content_slots"].append(
        {
            "id": "orphan-slot",
            "label": "Unused",
            "type": "placeholder",
            "value": None,
        }
    )

    figure = parse(document)

    with pytest.raises(CompilationValidationError) as exc_info:
        compile_figure(figure)

    assert "orphaned" in str(exc_info.value)


def test_duplicate_fsl_ids_compile_with_namespacing() -> None:
    """Duplicate FSL IDs across kinds should map to distinct ontology entity IDs."""
    document = valid_document()
    document["layout"]["panels"][0]["id"] = "shared"
    document["content_slots"][0]["id"] = "shared"
    document["layout"]["panels"][0]["object_refs"] = ["shared"]

    figure = parse(document)
    graph = compile_figure(figure)

    ontology_ids = {entity.id for entity in graph.entities}
    assert "fig-001:panel:shared" in ontology_ids
    assert "fig-001:slot:shared" in ontology_ids
    assert "fig-001:panel:shared" != "fig-001:slot:shared"


def test_compiled_graph_passes_ontology_validation() -> None:
    """Compiled graphs should satisfy ontology structural validation."""
    figure = parse(load_yaml(MINIMAL_FIGURE))
    graph = compile_figure(figure)

    OntologyValidator().validate(graph)


def test_style_references_attached_to_graph() -> None:
    """Style references should compile to annotation entities with references."""
    figure = parse(valid_document())
    graph = compile_figure(figure)

    style_entities = [entity for entity in graph.entities if ":style:" in entity.id]
    style_relationships = [
        rel for rel in graph.relationships if rel.type == RelationshipType.REFERENCES
    ]

    assert len(style_entities) == 1
    assert style_entities[0].metadata["style_ref"] == "styles/color-system.md"
    assert len(style_relationships) == 1


def test_figure_compiler_class_matches_helper() -> None:
    """FigureCompiler.compile should match compile_figure helper output."""
    figure = parse(valid_document())

    direct = FigureCompiler().compile(figure)
    helper = compile_figure(figure)

    assert direct.model_dump() == helper.model_dump()
