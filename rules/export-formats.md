# Export Format Rules

## Purpose

Define allowed output formats, format-specific constraints, and conversion rules for figure export.

## Scope

**In scope:**

- Supported export format list (placeholder slots)
- Format-specific resolution and color mode rules
- Vector vs raster selection criteria
- Layer and editability preservation rules
- File size and compression guidelines

**Out of scope:**

- Tool-specific export commands
- Journal file format requirements (user-supplied)
- Validation execution (see `validation/`)

## Sections to be Completed

- [ ] Supported format catalog
- [ ] Vector format rules (SVG, PDF, EPS placeholders)
- [ ] Raster format rules (PNG, TIFF placeholders)
- [ ] Color mode requirements per format
- [ ] Compression and quality settings placeholders
- [ ] Format selection decision tree

## TODO

- [ ] Cross-reference `validation/resolution-dpi.md`
- [ ] Define default export format per use case
- [ ] Document metadata requirements per format
- [ ] Add rule severity assignments