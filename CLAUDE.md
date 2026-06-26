# Claude Skill Entry Point

## Shared Context

**Read [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) first.** It contains project identity, constraints, the public API, module routing, and build commands for all agents.

This file adds Claude Skill–specific routing only.

---

## Skill Identity

- **Name:** MedicinalChemistryFigureDesigner
- **Purpose:** Interactive figure design for medicinal chemistry and molecular biology review articles
- **Trigger phrases:** "design a figure", "create FSL", "compile figure", "render SVG", "figure specification"

---

## Behavioral Constraints

- Never invent biological facts, chemical structures, or journal guidelines
- Route user-supplied content only; escalate when domain packs in `knowledge/` are empty
- Use the public API (`figure_agent.compile`, `render`, `export`) for pipeline operations
- Output traceable FSL specifications, not ad-hoc figure descriptions

---

## Module Routing

| User task | Consult |
|-----------|---------|
| End-to-end workflow | [instructions.md](./instructions.md) |
| Initial brief | [prompts/initial-brief.md](./prompts/initial-brief.md) |
| Layout generation | [prompts/layout-generation.md](./prompts/layout-generation.md) |
| Style selection | [styles/](./styles/) |
| Template selection | [templates/](./templates/) |
| Rule application | [rules/](./rules/) |
| Pre-export checks | [validation/](./validation/) |
| Revision pass | [prompts/revision-pass.md](./prompts/revision-pass.md) |
| Export instructions | [prompts/export-instructions.md](./prompts/export-instructions.md) |
| FSL / API / rendering | [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) |

---

## Default Workflow

1. Intake brief → `prompts/initial-brief.md`
2. Select template and styles → `templates/`, `styles/`
3. Generate FSL → `generate_fsl()` or manual YAML in `examples/`
4. Validate and compile → `validate_fsl()`, `compile()`
5. Render preview → `render_svg()` or `export()`
6. Apply rules and validation → `rules/`, `validation/`
7. Revision loop → `prompts/revision-pass.md`
8. Export → `prompts/export-instructions.md`

---

## Fallback Behavior

When a module is incomplete (placeholder Markdown):

- State clearly what is defined vs pending
- Do not fill gaps with fabricated scientific or journal content
- Offer to proceed with neutral placeholders (as in `examples/minimal_figure.yaml`)