"""Figure Agent MCP server exposing the full figure pipeline as tools."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from figure_agent.mcp.config import MCPServerConfig
from figure_agent.mcp.exceptions import MCPToolError
from figure_agent.mcp.handlers import MCPHandlers
from figure_agent.mcp.models import MCPToolResult
from figure_agent.mcp.registry import TOOL_DEFINITIONS, list_tool_names

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - optional dependency
    FastMCP = None  # type: ignore[assignment,misc]


def _result_to_payload(result: MCPToolResult) -> dict[str, Any]:
    return result.to_dict()


def _wrap_handler(
    handlers: MCPHandlers,
    method_name: str,
) -> Callable[..., dict[str, Any]]:
    method = getattr(handlers, method_name)

    def _tool(**kwargs: Any) -> dict[str, Any]:
        try:
            result = method(**kwargs)
            return _result_to_payload(result)
        except MCPToolError as exc:
            return MCPToolResult(
                success=False,
                tool=exc.tool,
                errors=exc.errors or (str(exc),),
            ).to_dict()

    return _tool


def create_mcp_server(config: MCPServerConfig | None = None) -> Any:
    """Create a FastMCP server with all Figure Agent tools registered."""
    if FastMCP is None:
        raise ImportError(
            "The 'mcp' package is required to run the Figure Agent MCP server. "
            "Install with: pip install 'figure-agent[mcp]'"
        )

    cfg = config or MCPServerConfig()
    handlers = MCPHandlers(cfg)
    server = FastMCP(
        "Figure Agent",
        instructions=(
            "Publication figure design pipeline. Use these tools to generate FSL, "
            "validate, compile, build visual scenes, and render figures. "
            "Always use render_gpt_image for PNG output — never call GPT Image APIs "
            "directly."
        ),
        json_response=True,
    )

    for tool in TOOL_DEFINITIONS:
        handler = _wrap_handler(handlers, tool.handler_name)
        handler.__name__ = tool.name
        handler.__doc__ = tool.description
        server.tool(name=tool.name)(handler)

    return server


def main() -> None:
    """Run the Figure Agent MCP server over stdio transport."""
    server = create_mcp_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()