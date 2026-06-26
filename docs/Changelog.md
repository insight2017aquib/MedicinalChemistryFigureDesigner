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

### Changed

- (none yet)

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