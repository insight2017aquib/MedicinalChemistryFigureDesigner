# Rules Module

## Purpose

Define compositional, labeling, accessibility, and export rules that govern figure quality. Rules are enforced during design and validated before export.

## Scope

**In scope:**

- Composition and layout rules
- Labeling conventions (structure only)
- Accessibility requirements
- Export format rules
- Journal-agnostic standards placeholder

**Out of scope:**

- Journal-specific submission guidelines
- Scientific content accuracy
- Visual style tokens (see `styles/`)

## Sections to be Completed

- [ ] Module overview and rule categories
- [ ] Rule file index with descriptions
- [ ] Rule precedence and conflict resolution
- [ ] How rules connect to `validation/`
- [ ] Extension guidelines for new rules

## TODO

- [ ] Complete each rule component file in this directory
- [ ] Define rule severity levels (error, warning, suggestion)
- [ ] Document how prompts reference rules during generation
- [ ] Specify mandatory vs optional rules