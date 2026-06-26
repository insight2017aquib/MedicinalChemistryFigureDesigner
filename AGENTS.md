# Agent Instructions

**Before doing any work in this repository, read and follow [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md).**

That file is the canonical project context for all LLMs and coding agents (Cursor, Grok, Codex, VS Code, Claude Code, etc.).

## Quick commands

```bash
pip install -e ".[dev]"
pytest
python scripts/render_example.py
```

## Key rules (summary)

- Use the public API in `figure_agent` (`compile`, `render`, `export`, etc.)
- Do not fabricate scientific or journal content
- Do not redesign FSL, ontology, compiler, or renderer layers unless asked
- Run `pytest` after code changes

Full details: [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md)