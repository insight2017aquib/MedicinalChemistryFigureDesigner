# MedicinalChemistryFigureDesigner

A modular platform for designing publication-quality scientific figures for medicinal chemistry and molecular biology review articles. Built as a Claude Skill with a staged pipeline from user brief to validated, export-ready figures.

**Current status:** v0.2 — Platform architecture (scaffold + platform layer)

**Repository:** [github.com/insight2017aquib/MedicinalChemistryFigureDesigner](https://github.com/insight2017aquib/MedicinalChemistryFigureDesigner)

---

## What This Project Is

MedicinalChemistryFigureDesigner is a **scientific figure platform**, not a content library. It provides:

- A **Claude Skill** entry point for interactive figure design sessions
- **Modular documentation** for styles, rules, templates, validation, and prompts
- A **Figure Specification Language (FSL)** for machine-readable figure descriptions
- **Knowledge packs** for domain-specific conventions (user-supplied content only)
- A **staged pipeline** toward automated rendering, validation, and export

The repository defines architecture, contracts, and extension points. It does not contain scientific facts, biology, or journal guidelines.

---

## Why It Exists

Review-article figures require consistent visual language, structural compliance, and reproducible specifications. This platform:

1. Separates **design system** (styles, rules) from **content** (user-supplied)
2. Produces **traceable specifications** (FSL) instead of ad-hoc descriptions
3. Integrates with **external tools** (BioRender, image generation) through defined interfaces
4. Enforces **validation gates** before publication export

---

## Roadmap

| Version | Milestone | Status |
|---------|-----------|--------|
| v0.1 | Repository scaffold | Complete |
| v0.2 | Platform architecture | In progress |
| v0.3 | Knowledge base | Planned |
| v0.4 | Figure Specification Language | Planned |
| v0.5 | BioRender integration | Planned |
| v0.6 | Image generation | Planned |
| v0.7 | Validation engine | Planned |
| v1.0 | Scientific Figure Agent | Planned |

See [docs/DevelopmentRoadmap.md](docs/DevelopmentRoadmap.md) for milestone details.

---

## Architecture

```mermaid
flowchart TD
    A[Claude Skill] --> B[Figure Specification Language]
    B --> C[BioRender MCP]
    C --> D[Image Generation]
    D --> E[Scientific Validation]
    E --> F[Publication Export]
```

Full architecture with module diagrams: [docs/Architecture.md](docs/Architecture.md)

---

## Repository Structure

```
MedicinalChemistryFigureDesigner/
├── README.md                  # Project overview (this file)
├── CLAUDE.md                  # Claude Skill entry point
├── instructions.md            # End-to-end workflow
│
├── docs/                      # Platform documentation
│   ├── Architecture.md
│   ├── DevelopmentRoadmap.md
│   ├── DesignPrinciples.md
│   ├── Contributing.md
│   └── Changelog.md
│
├── fsl/                       # Figure Specification Language
│   ├── schema.yaml
│   ├── validator.md
│   └── examples/
│
├── knowledge/                 # Domain knowledge packs (placeholders)
│   ├── MedicinalChemistry/
│   ├── StructuralBiology/
│   ├── DNARepair/
│   ├── JournalStyles/
│   └── GeneralDesign/
│
├── styles/                    # Visual design system
├── rules/                     # Composition, labeling, accessibility, export
├── templates/                 # Reusable layout templates
├── validation/                # Pre-export quality gates
├── prompts/                   # Claude prompt templates per workflow stage
├── examples/                  # Worked figure specimens (user-supplied)
│
└── .github/                   # Issue templates, PR template, workflows
```

### Core Modules (v0.1 — preserved)

| Module | Purpose |
|--------|---------|
| `styles/` | Color, typography, grids, molecular rendering, annotations |
| `rules/` | Composition, labeling, accessibility, export formats |
| `templates/` | Single/multi-panel, flow, comparison, legend layouts |
| `validation/` | Pre-export checklist, DPI, naming, metadata |
| `prompts/` | Stage-specific Claude prompt templates |
| `examples/` | Index and specimen notes for future examples |

### Platform Extensions (v0.2 — new)

| Module | Purpose |
|--------|---------|
| `docs/` | Architecture, roadmap, principles, contributing, changelog |
| `fsl/` | Figure Specification Language skeleton |
| `knowledge/` | Placeholder packs for domain conventions |
| `.github/` | Issue templates, PR template, workflows placeholder |

---

## Planned Integrations

| Integration | Milestone | Description |
|-------------|-----------|-------------|
| BioRender MCP | v0.5 | Molecular and biological illustration assets via Model Context Protocol |
| Image generation | v0.6 | FSL-to-render pipeline for raster and vector output |
| Validation engine | v0.7 | Automated FSL and rule compliance checking |
| Publication export | v1.0 | End-to-end packaging with metadata and format compliance |

---

## Getting Started

1. Read [instructions.md](instructions.md) for the figure design workflow
2. Review [CLAUDE.md](CLAUDE.md) for Claude Skill behavior and module routing
3. Consult [docs/DesignPrinciples.md](docs/DesignPrinciples.md) for platform constraints
4. See [docs/Contributing.md](docs/Contributing.md) before making changes

---

## Contributing

Contributions welcome. Follow the standards in [docs/Contributing.md](docs/Contributing.md). Do not submit fabricated scientific content or invented journal guidelines.

Use [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md) when opening pull requests.

---

## Changelog

See [docs/Changelog.md](docs/Changelog.md) for version history.