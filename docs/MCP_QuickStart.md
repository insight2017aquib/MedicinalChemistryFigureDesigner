# MCP Quick Start

## Purpose

Run the Figure Agent as a [Model Context Protocol](https://modelcontextprotocol.io) server so Claude and other MCP clients can design figures through tools instead of calling internal APIs directly.

## Install

```bash
pip install -e ".[mcp]"
```

## Run the server

**stdio transport (Claude Desktop / Claude Code):**

```bash
figure-agent-mcp
```

Or:

```bash
python -m figure_agent.mcp.server
```

## Exposed tools

| Tool | Input | Output |
|------|-------|--------|
| `generate_fsl` | Natural-language description | Valid FSL (dict, YAML, JSON) |
| `validate_fsl` | FSL document | Validation report |
| `compile` | FSL document | Ontology graph |
| `build_scene` | FSL or graph | Visual Scene |
| `render_svg` | FSL or graph | SVG |
| `render_gpt_image` | FSL or graph | PNG (base64) + metadata |
| `render` | FSL or graph + optional `format` | SVG or PNG (auto-selected) |
| `health` | — | Server status |
| `version` | — | Package version |

## Typical workflow

```
Natural language
    → generate_fsl
    → validate_fsl
    → compile
    → build_scene
    → render_gpt_image
    → PNG
```

## Configuration

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Required for live GPT Image rendering. Without it, `render_gpt_image` uses a deterministic stub backend for development. |

Rendered PNG files and metadata are written to `output/mcp/` by default.

## Claude Desktop configuration

Add to your Claude Desktop MCP config:

```json
{
  "mcpServers": {
    "figure-agent": {
      "command": "figure-agent-mcp",
      "args": []
    }
  }
}
```

Use the full path to `figure-agent-mcp` if it is not on your `PATH`.

## Python usage (without MCP transport)

Handlers can be invoked directly for testing or scripting:

```python
from figure_agent.mcp import MCPHandlers, MCPServerConfig
from figure_agent.renderers.gpt_image import StubImageBackend

handlers = MCPHandlers(
    MCPServerConfig(gpt_image_backend_factory=StubImageBackend)
)
result = handlers.generate_fsl("Assay workflow with primary readout")
print(result.data["yaml"])
```

See [Claude_MCP_Integration.md](Claude_MCP_Integration.md) for Claude-specific guidance.