"""Figure Agent — scientific figure specification toolkit."""

from figure_agent.compiler import FigureCompiler, compile_figure
from figure_agent.fsl.models import Figure
from figure_agent.fsl.parser import load_json, load_yaml, parse, validate_schema
from figure_agent.fsl.serializer import to_json, to_yaml
from figure_agent.fsl.validator import FSLValidator
from figure_agent.ontology import (
    Cell,
    EntityRegistry,
    Label,
    OntologyGraph,
    OntologyValidator,
    Relationship,
    RelationshipType,
    create_entity,
    graph_from_dict,
    graph_to_json,
    graph_to_yaml,
)
from figure_agent.renderers import RenderConfig, RenderResult, Renderer, SVGRenderer

__all__ = [
    "Cell",
    "EntityRegistry",
    "Figure",
    "FigureCompiler",
    "FSLValidator",
    "Label",
    "OntologyGraph",
    "OntologyValidator",
    "Relationship",
    "RelationshipType",
    "RenderConfig",
    "RenderResult",
    "Renderer",
    "SVGRenderer",
    "compile_figure",
    "create_entity",
    "graph_from_dict",
    "graph_to_json",
    "graph_to_yaml",
    "load_json",
    "load_yaml",
    "parse",
    "to_json",
    "to_yaml",
    "validate_schema",
]

__version__ = "0.6.0"
