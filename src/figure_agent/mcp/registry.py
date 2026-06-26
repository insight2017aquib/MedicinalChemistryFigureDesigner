"""MCP tool registry for the Figure Agent server."""

from __future__ import annotations

from figure_agent.mcp.models import ToolDefinition

TOOL_DEFINITIONS: tuple[ToolDefinition, ...] = (
    ToolDefinition(
        name="generate_fsl",
        description=(
            "Generate a valid FSL document from a natural-language figure "
            "description. Returns YAML and JSON representations."
        ),
        handler_name="generate_fsl",
    ),
    ToolDefinition(
        name="validate_fsl",
        description="Validate an FSL document and return a structured report.",
        handler_name="validate_fsl",
    ),
    ToolDefinition(
        name="compile",
        description="Compile an FSL document into an ontology graph.",
        handler_name="compile",
    ),
    ToolDefinition(
        name="build_scene",
        description=(
            "Build a renderer-independent Visual Scene from FSL or an "
            "ontology graph."
        ),
        handler_name="build_scene",
    ),
    ToolDefinition(
        name="render_svg",
        description="Render FSL or an ontology graph to SVG.",
        handler_name="render_svg",
    ),
    ToolDefinition(
        name="render_gpt_image",
        description=(
            "Render FSL or an ontology graph to a PNG image via the Figure "
            "Agent GPT Image pipeline. Claude must use this tool instead of "
            "calling image APIs directly."
        ),
        handler_name="render_gpt_image",
    ),
    ToolDefinition(
        name="render",
        description=(
            "Render FSL or an ontology graph using the appropriate renderer. "
            "Selects SVG or GPT Image based on the requested format."
        ),
        handler_name="render",
    ),
    ToolDefinition(
        name="health",
        description="Return Figure Agent server health and capability status.",
        handler_name="health",
    ),
    ToolDefinition(
        name="version",
        description="Return Figure Agent package and API version metadata.",
        handler_name="version",
    ),
)


def list_tool_names() -> list[str]:
    """Return registered MCP tool names in declaration order."""
    return [tool.name for tool in TOOL_DEFINITIONS]


def get_tool_definition(name: str) -> ToolDefinition | None:
    """Look up a tool definition by name."""
    key = name.strip().lower()
    for tool in TOOL_DEFINITIONS:
        if tool.name == key:
            return tool
    return None