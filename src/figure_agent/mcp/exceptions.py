"""Exception hierarchy for the Figure Agent MCP server."""

from __future__ import annotations


class MCPError(Exception):
    """Base exception for MCP server errors."""

    def __init__(self, message: str, *, code: str = "mcp_error") -> None:
        super().__init__(message)
        self.code = code


class MCPToolError(MCPError):
    """Raised when a tool invocation fails."""

    def __init__(
        self,
        message: str,
        *,
        tool: str,
        code: str = "tool_error",
        errors: tuple[str, ...] = (),
    ) -> None:
        super().__init__(message, code=code)
        self.tool = tool
        self.errors = errors


class MCPConfigurationError(MCPError):
    """Raised when MCP server configuration is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="configuration_error")