# Changelog

## Purpose

Record notable changes to the MedicinalChemistryFigureDesigner platform by milestone and version.

## Scope

**In scope:**

- Version history with added, changed, and planned items
- Milestone completion markers

**Out of scope:**

- Scientific content changes within knowledge packs
- External integration release notes (tracked separately when live)

Format based on [Keep a Changelog](https://keepachangelog.com/). Versioning aligned with `docs/DevelopmentRoadmap.md`.

---

## [Unreleased]

### Added

- (none yet)

---

## [v0.7.1] — LLM Specification Layer

### Added

- `specs/` — LLM reasoning specifications for FSL generation (11 documents)
- `specs/README.md`, `FSL_SPEC.md`, `FIGURE_GRAMMAR.md`, `FIELD_REFERENCE.md`, `OBJECT_MODEL.md`, `LAYOUT_GUIDE.md`, `STYLING_GUIDE.md`, `VALIDATION_RULES.md`, `COMMON_ERRORS.md`, `EXAMPLES.md`, `PROMPTING_GUIDE.md`

### Changed

- `PROJECT_CONTEXT.md`, `AGENTS.md`, `README.md` — route LLMs to `specs/` for FSL authoring

### Notes

- Documentation derived from `src/figure_agent/fsl/`, `compiler/`, `ontology/`, `renderers/`
- Not user/API/developer docs — semantic layer for Claude and future LLMs

### Changed

- (none yet)

---

## [v0.7] — Figure Agent API

### Added

- `src/figure_agent/api/` — `service`, `requests`, `responses`, `exceptions`
- Public functions: `generate_fsl`, `validate_fsl`, `compile`, `render`, `render_svg`, `export`, `health`, `version`
- Pluggable renderer registry: `register_renderer`, `list_renderers`
- Unit tests: `test_api.py`

### Changed

- Package version `0.7.0`
- `README.md`, `docs/Architecture.md`, `docs/DevelopmentRoadmap.md` — API layer documentation
- Top-level `figure_agent` package exports public API functions

### Notes

- No web framework, MCP, or external integrations — local Python API only
- Future renderers register via `register_renderer()` and are called with `render(renderer="name")`
- Validation and pipeline failures return structured responses by default

---

## [v0.6] — Minimal SVG Renderer

### Added

- `src/figure_agent/renderers/` — abstract `Renderer`, `SVGRenderer`, layout, geometry, styling, exceptions
- `scripts/render_example.py` — FSL → compile → render → `output/example.svg` demo
- Unit tests: `test_svg_renderer.py`, `test_renderer_layout.py`, `test_renderer_geometry.py`

### Changed

- Package version `0.6.0`
- `README.md`, `docs/Architecture.md`, `docs/DevelopmentRoadmap.md` — renderer pipeline documentation

### Notes

- Proof-of-concept renderer only: monochrome palette, no icons, gradients, or scientific assets
- Pipeline validated end-to-end: FSL → Compiler → Ontology → SVGRenderer → SVG file
- Future renderers inherit from `Renderer` without modifying FSL, ontology, or compiler

---

## [v0.5] — Figure Compilation Engine

### Added

- `src/figure_agent/compiler/` — `FigureCompiler`, mapping, context, validator
- Unit tests: `test_compiler.py`, `test_compiler_mapping.py`

### Changed

- Package version `0.5.0`
- `README.md`, `docs/Architecture.md`, `docs/DevelopmentRoadmap.md` — compiler pipeline documentation

### Notes

- Pipeline: FSL → Compiler → Ontology → Renderer (implemented in v0.6)
- No rendering, biology, or external integrations

---

## [v0.4] — Scientific Figure Ontology

### Added

- `src/figure_agent/ontology/` — entity hierarchy, relationships, registry, validator, serialization
- Unit tests: `test_ontology_entities.py`, `test_ontology_relationships.py`, `test_ontology_registry.py`, `test_ontology_validator.py`, `test_ontology_serialization.py`

### Changed

- Package version `0.4.0`
- `README.md`, `docs/Architecture.md`, `docs/DevelopmentRoadmap.md` — ontology layer documentation

### Notes

- Ontology is infrastructure only: no rendering, biology, or scientific validation
- Pipeline position: FSL → Ontology → Renderer (planned)

---

## [v0.3] — FSL Engine

### Added

- `src/figure_agent/` — Python package with FSL parser, validator, serializer, and Pydantic models
- `tests/` — Unit tests for parser, validator, and serialization round-trip
- `examples/minimal_figure.yaml` — Minimal valid FSL document with neutral placeholders
- `pyproject.toml` — Python 3.12+ project configuration (Pydantic v2, PyYAML)

### Changed

- `README.md`, `docs/Architecture.md`, `docs/DevelopmentRoadmap.md` — document FSL engine placement in pipeline
- `.gitignore` — Python tooling artifacts

### Notes

- FSL engine is a structured representation layer, not a rendering engine
- No scientific content, biology validation, or external rendering integrations

---

## [v0.2] — Platform Architecture

### Added

- `docs/` — Architecture, DevelopmentRoadmap, DesignPrinciples, Contributing, Changelog
- `knowledge/` — Placeholder knowledge packs (MedicinalChemistry, StructuralBiology, DNARepair, JournalStyles, GeneralDesign)
- `fsl/` — Figure Specification Language skeleton (`schema.yaml`, `validator.md`, `examples/`)
- `.github/` — Issue templates, pull request template, workflows placeholder
- Root `README.md` rewritten for platform overview and roadmap

### Changed

- Repository positioned as a scientific figure platform (extends v0.1 scaffold)

### Notes

- All v0.1 modules (`styles/`, `rules/`, `templates/`, `validation/`, `prompts/`, `examples/`) preserved without structural changes

---

## [v0.1] — Repository Scaffold

### Added

- Core module directories: `styles/`, `rules/`, `templates/`, `validation/`, `prompts/`, `examples/`
- Entry points: `README.md`, `CLAUDE.md`, `instructions.md`
- Placeholder Markdown documentation for every module component
- `.gitignore` for OS, editor, and export artifacts
- GitHub repository: `insight2017aquib/MedicinalChemistryFigureDesigner`