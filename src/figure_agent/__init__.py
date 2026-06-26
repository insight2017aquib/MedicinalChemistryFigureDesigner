"""Figure Agent — scientific figure specification toolkit."""

from figure_agent.api import (
    compile,
    export,
    generate_fsl,
    health,
    render,
    render_svg,
    validate_fsl,
    version,
)
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
from figure_agent.mcp import MCPHandlers, MCPServerConfig, create_mcp_server
from figure_agent.renderers import (
    GPTImagePromptBuilder,
    GPTImagePromptRenderer,
    GPTImageRenderer,
    RenderConfig,
    RenderResult,
    Renderer,
    SVGRenderer,
    create_gpt_image_renderer,
)

__all__ = [
    "Cell",
    "EntityRegistry",
    "Figure",
    "FigureCompiler",
    "FSLValidator",
    "GPTImagePromptBuilder",
    "GPTImagePromptRenderer",
    "GPTImageRenderer",
    "Label",
    "MCPHandlers",
    "MCPServerConfig",
    "OntologyGraph",
    "OntologyValidator",
    "Relationship",
    "RelationshipType",
    "RenderConfig",
    "RenderResult",
    "Renderer",
    "SVGRenderer",
    "compile",
    "compile_figure",
    "create_entity",
    "create_mcp_server",
    "create_gpt_image_renderer",
    "export",
    "generate_fsl",
    "health",
    "graph_from_dict",
    "graph_to_json",
    "graph_to_yaml",
    "load_json",
    "load_yaml",
    "parse",
    "render",
    "render_svg",
    "to_json",
    "to_yaml",
    "validate_fsl",
    "validate_schema",
    "version",
]

from figure_agent.core.constants import __version__
