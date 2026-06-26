# Claude Skill Entry Point

## Purpose

Serve as the primary context file loaded when this project is used as a Claude Skill. Directs Claude to the correct modules, workflows, and constraints without embedding scientific content.

## Scope

**In scope:**

- Skill identity and high-level behavior
- Module routing (which file to consult for which task)
- Hard constraints (no fabricated science, no invented journal rules)
- Workflow summary linking to `instructions.md`

**Out of scope:**

- Detailed style specifications (see `styles/`)
- Prompt text (see `prompts/`)
- Validation criteria (see `validation/`)

## Sections to be Completed

- [ ] Skill name, description, and trigger phrases
- [ ] Module routing table (task → file path)
- [ ] Behavioral constraints and guardrails
- [ ] Default workflow steps
- [ ] Error-handling and fallback behavior when modules are incomplete
- [ ] References to `instructions.md` and subdirectory README files

## TODO

- [ ] Define when to load `styles/` vs `templates/` vs `prompts/`
- [ ] Document prohibition on inventing scientific or journal-specific content
- [ ] Add escalation path when user requests content not yet defined in repo
- [ ] Specify output format expectations (Markdown briefs, SVG specs, etc.)
- [ ] Align with Claude Skill packaging requirements once finalized