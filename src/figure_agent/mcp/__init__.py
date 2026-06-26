"""Figure Agent MCP server — public interface for Claude and other MCP clients."""

from figure_agent.mcp.config import MCPServerConfig
from figure_agent.mcp.exceptions import MCPConfigurationError, MCPError, MCPToolError
from figure_agent.mcp.handlers import MCPHandlers, parse_natural_language_description
from figure_agent.mcp.models import MCPToolResult, ToolDefinition
from figure_agent.mcp.registry import TOOL_DEFINITIONS, get_tool_definition, list_tool_names
from figure_agent.mcp.server import create_mcp_server, main

__all__ = [
    "MCPConfigurationError",
    "MCPError",
    "MCPHandlers",
    "MCPServerConfig",
    "MCPToolError",
    "MCPToolResult",
    "TOOL_DEFINITIONS",
    "ToolDefinition",
    "create_mcp_server",
    "get_tool_definition",
    "list_tool_names",
    "main",
    "parse_natural_language_description",
]