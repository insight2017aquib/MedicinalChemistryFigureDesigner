# Claude MCP Integration Guide

## Overview

Claude should use the **Figure Agent MCP server** as the only interface for figure design. The MCP layer orchestrates the existing pipeline — it does not reimplement rendering, compilation, or validation.

**Claude must never call GPT Image (or any image generation API) directly.** Use the `render_gpt_image` tool instead.

## Setup

1. Install the package with MCP support:

   ```bash
   pip install -e ".[mcp]"
   ```

2. Register the server in Claude Desktop or Claude Code (see [MCP_QuickStart.md](MCP_QuickStart.md)).

3. Set `OPENAI_API_KEY` when you need real PNG output. Without it, the server uses a stub backend suitable for pipeline testing.

## Recommended tool sequence

### Full pipeline (natural language → PNG)

1. **`generate_fsl`** — Pass the user's figure brief as natural language.
2. **`validate_fsl`** — Confirm the generated FSL is structurally valid.
3. **`compile`** — Produce the ontology graph.
4. **`build_scene`** — Inspect the renderer-independent Visual Scene (optional but useful for debugging).
5. **`render_gpt_image`** — Produce the PNG through Figure Agent.

### Vector-only workflow

Replace step 5 with **`render_svg`** when the user needs SVG instead of PNG.

### Shortcut

Use **`render`** with `format: "png"` or `format: "svg"` to auto-select the renderer after compilation.

## Tool parameters

### `generate_fsl`

```json
{
  "description": "Mechanism schematic showing receptor binding and downstream signaling"
}
```

Returns `document`, `yaml`, and `json` fields.

### `validate_fsl`

```json
{
  "fsl": { "...": "FSL document object" },
  "semantic": true
}
```

### `compile`

```json
{
  "fsl": { "...": "FSL document object" }
}
```

### `build_scene`

```json
{
  "graph": { "...": "compiled ontology graph" }
}
```

Pass `fsl` instead of `graph` when compilation has not run yet.

### `render_gpt_image`

```json
{
  "graph": { "...": "compiled ontology graph" }
}
```

Returns:

- `image_base64` — PNG bytes (base64-encoded)
- `image_path` — saved file path when `output_dir` is configured
- `metadata` — prompt version, dimensions, backend name

## Guardrails for Claude

1. **Do not call OpenAI image APIs directly** — always use `render_gpt_image`.
2. **Do not invent scientific content** — labels and slots come from the user brief and FSL.
3. **Validate before rendering** — run `validate_fsl` after `generate_fsl` unless the FSL was user-supplied and pre-validated.
4. **Prefer explicit tools** — use `render_svg` or `render_gpt_image` over `render` when the output format is known.
5. **Check `health`** at session start to confirm the server is ready.

## Error handling

All tools return a consistent envelope:

```json
{
  "success": false,
  "tool": "validate_fsl",
  "data": { "valid": false, "errors": ["..."] },
  "errors": ["..."]
}
```

When `success` is `false`, read `errors` and adjust the FSL or inputs before retrying.

## Example session

**User:** "Create a single-panel figure for a placeholder assay readout."

**Claude actions:**

1. Call `generate_fsl` with the user brief.
2. Call `validate_fsl` on the returned `document`.
3. Call `compile` on the validated FSL.
4. Call `render_gpt_image` with the compiled `graph`.
5. Present the PNG to the user using `image_base64` or `image_path`.

## Architecture note

The MCP server (`src/figure_agent/mcp/`) is a thin orchestration layer:

```
Claude → MCP tools → figure_agent.api → FSL / Compiler / Visual Scene / Renderers
```

No renderer-specific logic lives in the MCP layer. GPT Image rendering flows through the existing `GPTImageRenderer` and `GPTImagePromptBuilder`.