# Contributing

## Purpose

Define development standards, conventions, and workflows for contributors to the MedicinalChemistryFigureDesigner platform.

## Scope

**In scope:**

- Coding and documentation standards
- Naming and versioning conventions
- Branch and commit guidelines
- Pull request expectations

**Out of scope:**

- Scientific content authoring guidelines
- Journal submission procedures
- External tool configuration

---

## Getting Started

1. Fork the repository
2. Create a branch following the naming conventions below
3. Make changes within the appropriate module
4. Update `docs/Changelog.md` for notable changes
5. Open a pull request using `.github/PULL_REQUEST_TEMPLATE.md`

---

## Coding Standards

This repository is currently documentation-first. When code is introduced (v0.4+):

- Prefer readable, explicit code over clever abstractions
- One responsibility per file or function
- Include inline comments only for non-obvious logic
- No hardcoded scientific content in source files
- Configuration via files (YAML, JSON), not inline constants

---

## Documentation Standards

Every Markdown file should include:

| Section | Required |
|---------|----------|
| Title (H1) | Yes |
| Purpose | Yes |
| Scope (in / out) | Yes |
| Body content | As needed |
| Sections to be Completed | For placeholders |
| TODO | For placeholders |

Additional rules:

- Use relative links to other repository files
- Mark unfinished content with `[ ]` checkboxes or explicit `TODO` labels
- Do not embed fabricated scientific facts or journal guidelines
- Architecture changes require an update to `docs/Architecture.md`

---

## Markdown Conventions

- **Headings:** ATX style (`#`, `##`, `###`); one H1 per file
- **Lists:** Use `-` for unordered; `1.` for ordered
- **Code:** Fenced blocks with language tags where applicable
- **Links:** `[descriptive text](../path/to/file.md)` — no bare URLs in prose
- **Tables:** Use for structured comparisons; keep columns concise
- **Diagrams:** Mermaid in fenced `mermaid` blocks
- **Line length:** No hard limit; prefer readable paragraph breaks

---

## Naming Conventions

### Files and Directories

| Type | Convention | Example |
|------|------------|---------|
| Module directories | lowercase, plural or descriptive | `styles/`, `knowledge/` |
| Documentation files | PascalCase or kebab-case | `Architecture.md`, `pre-export-checklist.md` |
| Knowledge packs | PascalCase directory names | `knowledge/MedicinalChemistry/` |
| FSL files | lowercase | `schema.yaml`, `validator.md` |
| GitHub templates | SCREAMING_SNAKE or kebab-case | `bug_report.md`, `PULL_REQUEST_TEMPLATE.md` |

### Tokens and Identifiers (FSL, future code)

- Use `snake_case` for schema fields and variables
- Use `kebab-case` for file slugs and export names
- Prefix module-specific tokens with module abbreviation where needed (e.g., `fsl_version`, `val_check_id`)

---

## Versioning Strategy

The project follows milestone-based versioning aligned with `docs/DevelopmentRoadmap.md`:

| Segment | Meaning |
|---------|---------|
| v0.x | Pre-release platform milestones |
| v1.0 | First production-ready Scientific Figure Agent |

- Document changes in `docs/Changelog.md` under the appropriate version heading
- Use `Unreleased` section for in-progress work
- Tag releases on GitHub when a milestone is marked complete

---

## Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<short-description>` | `feature/fsl-schema-v1` |
| Fix | `fix/<short-description>` | `fix/readme-links` |
| Documentation | `docs/<short-description>` | `docs/architecture-diagram` |
| Platform | `platform/<milestone>` | `platform/v0.3-knowledge` |

- Branch from `main`
- Keep branches short-lived
- Rebase or merge `main` before opening a PR

---

## Commit Message Format

```
<type>(<scope>): <short summary>

[optional body]

[optional footer]
```

### Types

| Type | Use for |
|------|---------|
| `feat` | New module, file, or capability |
| `fix` | Corrections to existing content |
| `docs` | Documentation-only changes |
| `chore` | Tooling, `.gitignore`, GitHub templates |
| `refactor` | Restructuring without behavior change |

### Examples

```
docs(platform): add Architecture.md with pipeline diagrams
feat(fsl): add schema.yaml skeleton
chore(github): add issue templates
fix(validation): correct cross-reference to rules module
```

- Summary: imperative mood, ≤ 72 characters
- Body: explain what and why, not how
- Footer: reference issues (`Closes #12`)

---

## Pull Request Expectations

- Fill out the PR template completely
- Link related issues
- Update `docs/Changelog.md` for user-visible changes
- Ensure no fabricated scientific content is introduced
- Confirm all new files follow documentation standards above

---

## What Not to Contribute

- Fabricated biology, chemistry, or pharmacology content
- Invented journal or publisher guidelines
- Copyrighted figure assets without attribution and permission
- Breaking changes to v0.1 module contracts without a migration note in `docs/Changelog.md`