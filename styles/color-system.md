# Color System

## Purpose

Define the color palette, semantic color roles, and usage constraints for figure elements. Ensures visual consistency across panels and figure types.

## Scope

**In scope:**

- Primary, secondary, and accent color slots
- Semantic roles (e.g., highlight, background, border, annotation)
- Contrast and accessibility considerations (structure only)
- Color application rules by element type

**Out of scope:**

- Specific hex values (to be supplied by maintainers)
- Color choices tied to biological or chemical meaning
- Print vs screen color profiles (detail in `validation/resolution-dpi.md`)

## Sections to be Completed

- [ ] Palette structure (primary, secondary, neutral, accent)
- [ ] Semantic role mapping table
- [ ] Contrast requirements placeholder
- [ ] Color-blind-safe usage guidelines placeholder
- [ ] Do-not-use combinations
- [ ] Extension slot for domain-specific palettes

## TODO

- [ ] Define palette token naming convention
- [ ] Add cross-reference to `rules/accessibility.md`
- [ ] Specify how templates reference color tokens
- [ ] Document grayscale fallback strategy