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

- Per-backend rendering implementation details (BioRender, image generation APIs)
- Scientific content or domain knowledge
- Journal-specific export requirements

---

## System Overview

The platform transforms a user brief into a publication-ready figure through a staged pipeline. Each stage has a dedicated module in this repository or a planned external integration.

```mermaid
flowchart TD
    A[Claude Skill] --> B[Figure Specification Language]
    B --> C[Compiler]
    C --> O[Ontology]
    O --> R[Renderer]
    R --> E[Scientific Validation]
    E --> F[Publication Export]

    subgraph repo [This Repository]
        A
        B
        B2[src/figure_agent/fsl/]
        C2[src/figure_agent/compiler/]
        O2[src/figure_agent/ontology/]
        R2[src/figure_agent/renderers/]
        E
        G[styles/]
        H[rules/]
        I[templates/]
        J[knowledge/]
        K[validation/]
        L[prompts/]
    end

    B --> B2
    B --> C2
    C2 --> O2
    O --> O2
    O --> R2
    R --> R2

    subgraph external [Planned Integrations]
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

**Documentation:** `fsl/` (schema skeleton, validator spec)

**Implementation:** `src/figure_agent/fsl/` (v0.3 engine)

A structured description language for scientific figures. FSL captures layout, style references, content slots, and metadata in a machine-readable format. It bridges human intent and automated rendering.

The v0.3 FSL engine provides:

| Module | Responsibility |
|--------|----------------|
| `models.py` | Pydantic models (`Figure`, `Metadata`, `Panel`, `Layout`, etc.) |
| `parser.py` | Load YAML/JSON, schema validation, full parse pipeline |
| `validator.py` | Semantic checks: duplicate IDs, layout consistency, template refs |
| `serializer.py` | Serialize to YAML/JSON with round-trip consistency |

```mermaid
flowchart LR
    YAML[YAML / JSON file] --> Parser[parser.py]
    Parser --> Models[models.py Figure]
    Models --> Validator[validator.py]
    Validator -->|pass| Serializer[serializer.py]
    Serializer --> Output[YAML / JSON]
```

### 3. Scientific Figure Ontology

**Implementation:** `src/figure_agent/ontology/` (v0.4)

Typed representation of figure components and their relationships. The ontology layer translates FSL content slots into structured entity graphs that future renderers consume.

| Module | Responsibility |
|--------|----------------|
| `entities.py` | Entity hierarchy (`Molecule`, `Protein`, `Label`, `Arrow`, etc.) |
| `relationships.py` | Relationship types (`contains`, `annotates`, etc.) and `OntologyGraph` |
| `registry.py` | Entity type registration, instance lookup, graph serialization |
| `validator.py` | Structural checks: duplicate IDs, missing refs, cycles |
| `enums.py` | `EntityType` and `RelationshipType` identifiers |

```mermaid
flowchart LR
    FSL[FSL Figure] --> Compiler[FigureCompiler]
    Compiler --> Graph[OntologyGraph]
    Graph --> Registry[EntityRegistry]
    Registry --> Val[ontology/validator.py]
    Val -->|pass| Renderer[Renderer implementations]
```

The ontology defines **structure only** — no biological semantics, no rendering, no scientific validation.

### 4. Figure Compilation Engine

**Implementation:** `src/figure_agent/compiler/` (v0.5)

Transforms validated FSL `Figure` documents into `OntologyGraph` instances. Bridges the specification layer and the typed entity layer.

| Module | Responsibility |
|--------|----------------|
| `compiler.py` | `FigureCompiler`, orchestrates compilation pipeline |
| `mapping.py` | Maps panels, content slots, and style refs to ontology entities |
| `context.py` | Tracks compilation state, qualified object registry, ID namespacing |
| `validator.py` | Detects orphan slots, missing references, invalid mappings |

```mermaid
flowchart LR
    FSL[FSL Figure] --> FC[FigureCompiler]
    FC --> Map[mapping.py]
    Map --> Ctx[CompilationContext]
    Ctx --> Graph[OntologyGraph]
    Graph --> OV[ontology/validator.py]
```

### 5. Renderer

**Implementation:** `src/figure_agent/renderers/` (v0.6)

Converts compiled `OntologyGraph` instances into graphical output. All renderer backends share a common abstract interface so the pipeline remains backend-agnostic.

| Module | Responsibility |
|--------|----------------|
| `base.py` | Abstract `Renderer`, `RenderConfig`, `RenderResult` |
| `svg_renderer.py` | `SVGRenderer` — proof-of-concept monochrome SVG output |
| `layout.py` | Simple automatic layout (vertical stacking, panel arrangement) |
| `geometry.py` | Rectangles, arrows, centered label placement |
| `styling.py` | Monochrome palette constants |
| `exceptions.py` | `RenderError`, `LayoutError`, `SVGRenderError` |

**v0.6 rendering scope** (intentionally minimal):

- Rectangle and rounded rectangle
- Text label (centered)
- Straight arrow
- Container box and panel boundary

No gradients, shadows, icons, or scientific illustration assets.

```mermaid
flowchart LR
    Graph[OntologyGraph] --> Layout[layout.py]
    Layout --> Geom[geometry.py]
    Geom --> SVG[svg_renderer.py]
    SVG --> File[SVG document]
```

**Future renderer implementations** (inherit from `Renderer`):

| Renderer | Target | Milestone |
|----------|--------|-----------|
| `BioRenderRenderer` | BioRender MCP assets | v0.8 |
| `GPTImageRenderer` | Image generation API | v0.9+ |
| `PowerPointRenderer` | Slide export | Future |
| `MermaidRenderer` | Diagram syntax | Future |
| `IllustratorRenderer` | Vector authoring tools | Future |

Demo: `python scripts/render_example.py` writes `output/example.svg`.

### 6. Scientific Validation

**Location:** `validation/`, `rules/`

Quality gates applied before export. Validates structural compliance, accessibility, naming, and metadata—not scientific accuracy (user-supplied).

### 7. Publication Export

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
    participant Ont as Ontology
    participant KB as knowledge/
    participant Val as validation/
    participant Render as Renderer
    participant Export as Publication Export

    User->>Skill: Figure brief
    Skill->>KB: Load domain pack (if applicable)
    Skill->>FSL: Generate specification
    FSL->>Ont: Compile via FigureCompiler
    Ont->>Val: Pre-export checks
    Val-->>Skill: Pass / fail report
    Skill->>Render: Validated ontology graph
    Render->>Export: Rendered assets
    Export-->>User: Publication-ready figure
```

---

## Extension Points

| Extension | Location | Version Target |
|-----------|----------|----------------|
| FSL engine | `src/figure_agent/fsl/` | v0.3 |
| Figure ontology | `src/figure_agent/ontology/` | v0.4 |
| Figure compiler | `src/figure_agent/compiler/` | v0.5 |
| SVG renderer | `src/figure_agent/renderers/` | v0.6 |
| Knowledge packs | `knowledge/` | v0.7 |
| FSL schema (complete) | `fsl/schema.yaml` | v0.7 |
| BioRender MCP renderer | External | v0.8 |
| Advanced renderers (image gen, export) | `src/figure_agent/renderers/` | v0.9+ |
| Validation engine | `validation/` + engine | v0.9 |
| Full agent | `CLAUDE.md` + pipeline | v1.0 |

---

## Compatibility Notes

The v0.2 platform layer (`docs/`, `knowledge/`, `fsl/`, `.github/`) extends the v0.1 scaffold without modifying existing module contracts. All original directories (`styles/`, `rules/`, `templates/`, `validation/`, `prompts/`, `examples/`) remain unchanged in purpose and structure.