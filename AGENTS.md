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

## Generating FSL (Claude Reasoning Layer)

If asked to create or edit FSL, follow this path — do not guess syntax:

1. [specs/ROLE_DEFINITION.md](./specs/ROLE_DEFINITION.md)
2. [specs/LLM_WORKFLOW.md](./specs/LLM_WORKFLOW.md)
3. [specs/DECISION_TREE.md](./specs/DECISION_TREE.md)
4. [specs/FSL_CHECKLIST.md](./specs/FSL_CHECKLIST.md) + [specs/SELF_VALIDATION.md](./specs/SELF_VALIDATION.md)
5. [specs/OUTPUT_CONTRACT.md](./specs/OUTPUT_CONTRACT.md)

Reference: [specs/FSL_SPEC.md](./specs/FSL_SPEC.md), [specs/EXAMPLES.md](./specs/EXAMPLES.md), [specs/COMMON_ERRORS.md](./specs/COMMON_ERRORS.md)