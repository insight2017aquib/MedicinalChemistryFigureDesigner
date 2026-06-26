# Platform Architecture

## Purpose

Describe the end-to-end architecture of the MedicinalChemistryFigureDesigner platform: how modules connect, data flows between stages, and where extension points live.

## Scope

**In scope:**

- High-level system pipeline
- Module boundaries and responsibilities
- Integration points (Claude Skill, FSL, external tools)
- Mermaid diagrams for visual reference

**Out of scope:**

- Implementation code
- Scientific content or domain knowledge
- Journal-specific export requirements

---

## System Overview

The platform transforms a user brief into a publication-ready figure through a staged pipeline. Each stage has a dedicated module in this repository or a planned external integration.

```mermaid
flowchart TD
    A[Claude Skill] --> B[Figure Specification Language]
    B --> C[BioRender MCP]
    C --> D[Image Generation]
    D --> E[Scientific Validation]
    E --> F[Publication Export]

    subgraph repo [This Repository]
        A
        B
        E
        G[styles/]
        H[rules/]
        I[templates/]
        J[knowledge/]
        K[validation/]
        L[prompts/]
    end

    subgraph external [Planned Integrations]
        C
        D
        F
    end

    A --> G
    A --> H
    A --> I
    A --> J
    B --> K
    E --> K
```

---

## Pipeline Stages

### 1. Claude Skill

**Location:** `CLAUDE.md`, `instructions.md`, `prompts/`

The entry point for interactive figure design sessions. The skill routes user requests to the correct modules, enforces guardrails (no fabricated science), and orchestrates the workflow defined in `instructions.md`.

### 2. Figure Specification Language (FSL)

**Location:** `fsl/`

A structured description language for scientific figures. FSL captures layout, style references, content slots, and metadata in a machine-readable format. It bridges human intent and automated rendering.

### 3. BioRender MCP

**Location:** Planned external integration (v0.5)

Model Context Protocol integration with BioRender for molecular and biological illustration assets. FSL specifications will reference BioRender-compatible element slots.

### 4. Image Generation

**Location:** Planned external integration (v0.6)

Rendering pipeline that converts FSL specifications into raster or vector figure assets using styles, templates, and knowledge packs.

### 5. Scientific Validation

**Location:** `validation/`, `rules/`

Quality gates applied before export. Validates structural compliance, accessibility, naming, and metadata—not scientific accuracy (user-supplied).

### 6. Publication Export

**Location:** `validation/`, `rules/export-formats.md`

Final packaging of validated figures with metadata, correct resolution, and format per user-supplied standards.

---

## Module Dependency Diagram

```mermaid
flowchart LR
    subgraph core [Core Modules]
        prompts[prompts/]
        fsl[fsl/]
        styles[styles/]
        rules[rules/]
        templates[templates/]
        validation[validation/]
    end

    subgraph platform [Platform Extensions]
        knowledge[knowledge/]
        docs[docs/]
        examples[examples/]
    end

    prompts --> styles
    prompts --> templates
    prompts --> rules
    prompts --> knowledge
    fsl --> styles
    fsl --> templates
    fsl --> rules
    validation --> rules
    validation --> fsl
    examples --> templates
    examples --> styles
```

---

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Skill as Claude Skill
    participant FSL as FSL
    participant KB as knowledge/
    participant Val as validation/
    participant Render as Image Generation
    participant Export as Publication Export

    User->>Skill: Figure brief
    Skill->>KB: Load domain pack (if applicable)
    Skill->>FSL: Generate specification
    FSL->>Val: Pre-export checks
    Val-->>Skill: Pass / fail report
    Skill->>Render: Validated specification
    Render->>Export: Rendered assets
    Export-->>User: Publication-ready figure
```

---

## Extension Points

| Extension | Location | Version Target |
|-----------|----------|----------------|
| Knowledge packs | `knowledge/` | v0.3 |
| FSL schema | `fsl/schema.yaml` | v0.4 |
| BioRender MCP | External | v0.5 |
| Image generation | External | v0.6 |
| Validation engine | `validation/` | v0.7 |
| Full agent | `CLAUDE.md` + pipeline | v1.0 |

---

## Compatibility Notes

The v0.2 platform layer (`docs/`, `knowledge/`, `fsl/`, `.github/`) extends the v0.1 scaffold without modifying existing module contracts. All original directories (`styles/`, `rules/`, `templates/`, `validation/`, `prompts/`, `examples/`) remain unchanged in purpose and structure.