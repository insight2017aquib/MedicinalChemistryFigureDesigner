"""Request and response models for MCP tool orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MCPToolResult:
    """Standard tool response envelope."""

    success: bool
    tool: str
    data: dict[str, Any] = field(default_factory=dict)
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "success": self.success,
            "tool": self.tool,
            "data": self.data,
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class ToolDefinition:
    """Metadata for a registered MCP tool."""

    name: str
    description: str
    handler_name: str