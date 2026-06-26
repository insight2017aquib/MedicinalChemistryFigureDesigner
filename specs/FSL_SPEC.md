# FSL Specification

Semantic specification for the Figure Specification Language. Explains what each construct **means**, not just its YAML shape.

**See also:** [FIELD_REFERENCE.md](./FIELD_REFERENCE.md), [FIGURE_GRAMMAR.md](./FIGURE_GRAMMAR.md), [VALIDATION_RULES.md](./VALIDATION_RULES.md)

---

## Figure (Root Document)

### Purpose

The root object representing one figure specification. A single file describes one figure from identity through export intent.

### Required

Yes — the entire document is required to parse.

### Allowed values

A YAML or JSON object matching the `Figure` model. No other root types.

### Relationships

- Owns all other top-level sections
- Compiles to one ontology graph with one figure-root `Cell` entity
- `metadata.id` namespaces all compiled entity IDs

### Example

```yaml
fsl_version: "0.3.0"
metadata:
  id: "fig-001"
  title: "Placeholder Figure"
template:
  ref: "templates/single-panel.md"
layout:
  type: "single-panel"
  panels:
    - id: "panel-a"
      object_refs: ["slot-1"]
content_slots:
  - id: "slot-1"
    label: "Primary content"
    type: "placeholder"
```

### Common mistakes

- Adding unknown top-level keys (`panels:` at root instead of under `layout`)
- Omitting `template` or `layout` (schema failure)
- Treating the figure as rendered output — it is a specification only

### When to use

Always — every figure design session produces one Figure document.

### When NOT to use

Do not split one figure across multiple FSL files unless building separate figures. Do not use FSL for ontology graphs or SVG output.

---

## fsl_version

### Purpose

Declares which FSL schema generation rules apply. Enables backward-compatible parsing.

### Required

Yes.

### Allowed values

`0.3.0` (preferred), `0.2.0-draft` (legacy). Defined in `SUPPORTED_FSL_VERSIONS`.

### Relationships

Stored on figure-root ontology metadata as `fsl_version`.

### Example

```yaml
fsl_version: "0.3.0"
```

### Common mistakes

- Using `0.4.0` or `1.0` — not supported
- Omitting quotes in YAML (unquoted `0.3.0` is usually fine; `0.2.0-draft` needs quotes)

---

## Metadata

### Purpose

Human and machine identity for the specification. Drives figure-root labeling and export naming patterns.

### Required

Yes (`metadata` object with required `id` and `title`).

### Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `id` | Yes | Unique figure identifier; namespaces ontology IDs |
| `title` | Yes | Human-readable name; becomes figure-root label |
| `created` | No | ISO 8601 timestamp |
| `modified` | No | ISO 8601 timestamp |
| `author` | No | Specification author |
| `provenance` | No | Attribution entries (list of objects) |

### Relationships

- `metadata.id` → `{id}:figure:{id}` ontology entity
- `export.naming` may reference `{id}` as placeholder

### Example

```yaml
metadata:
  id: "fig-review-02"
  title: "Mechanism Overview"
  author: "maintainer"
  provenance: []
```

### Common mistakes

- Empty `id` or `title` (schema failure)
- Using ontology namespaced IDs in `metadata.id` (use simple IDs like `fig-001`)
- Inventing journal metadata fields not in the schema

### When to use

Always populate `id` and `title`. Add `author` and timestamps when known.

### When NOT to use

Do not embed scientific claims in `title` unless user-supplied. Do not use `provenance` for fabricated citations.

---

## Template

### Purpose

Links the figure to a layout template document in `templates/`. Templates describe compositional guidance; FSL references them by path.

### Required

Yes (`template.ref`).

### Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `ref` | Yes | Path to `templates/*.md` |
| `params` | No | Key-value bindings passed to template (e.g. `aspect_ratio`) |

### Allowed values for `ref`

Must match `KNOWN_TEMPLATES`:

- `templates/single-panel.md`
- `templates/multi-panel.md`
- `templates/schematic-flow.md`
- `templates/comparison-layout.md`
- `templates/legend-block.md`

### Relationships

- Stored on figure-root ontology metadata as `template_ref`, `template_params`
- Should align with `layout.type` (see [LAYOUT_GUIDE.md](./LAYOUT_GUIDE.md))

### Example

```yaml
template:
  ref: "templates/single-panel.md"
  params:
    aspect_ratio: "4:3"
```

### Common mistakes

- Unknown template path — semantic validation error
- Template/layout mismatch (e.g. `comparison-layout` template with `single-panel` layout)
- Inventing template files not in the repository

---

## Layout

### Purpose

Declares the spatial organization category and panel structure. Panels partition the figure; each panel lists which content slots appear there.

### Required

Yes (`layout.type`; `panels` defaults to empty list but must satisfy count rules).

### Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `type` | Yes | Layout category identifier |
| `panels` | No (default `[]`) | Panel definitions |

### Allowed values for `type`

- `single-panel` — exactly 1 panel
- `multi-panel` — 2 or more panels
- `schematic-flow` — 1 or more panels
- `comparison-layout` — 2 or more panels

### Relationships

- Each panel compiles to a `Cell` entity
- Figure root `CONTAINS` each panel
- Each panel `CONTAINS` referenced slots

### Example

See [LAYOUT_GUIDE.md](./LAYOUT_GUIDE.md) and [EXAMPLES.md](./EXAMPLES.md).

### Common mistakes

- Wrong panel count for layout type
- Defining slots inside panels instead of `content_slots`
- Using unsupported layout types (`grid`, `free-layout`)

---

## Panels

### Purpose

A panel is a **region** of the figure that displays one or more content slots. Panels are structural containers, not drawable objects themselves.

### Required

At least one panel for most layouts; count depends on `layout.type`.

### Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `id` | Yes | Unique panel identifier within the figure |
| `zones` | No | Named subregions (semantic labels; renderer uses loosely) |
| `object_refs` | No | List of `content_slots[].id` values to display |

### Relationships

- Panel `id` is **not** used in `object_refs` — only slot IDs are
- `object_refs` must reference existing slot IDs (semantic validation)
- Unreferenced slots cause compilation failure (orphan check)

### Example

```yaml
panels:
  - id: "panel-a"
    zones: ["primary"]
    object_refs: ["slot-1", "slot-2"]
```

### Common mistakes

- Duplicate panel IDs
- `object_refs` pointing to nonexistent slots
- Empty `object_refs` when slots exist — creates orphan slots if slots are defined elsewhere
- Putting ontology entity definitions inside panels

### When to use

One panel per visual region. Multi-panel figures use multiple panel entries.

### When NOT to use

Do not create panels for style references or legend files — those use `styles` and `template`.

---

## Content Slots

### Purpose

A **placeholder** for user-supplied figure content. Slots are the atomic content units FSL defines. The compiler maps each slot to an ontology entity; the renderer draws it.

### Required

No at schema level (defaults to `[]`), but practical figures need slots matching `object_refs`. Compiler requires every slot to be referenced by a panel.

### Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `id` | Yes | Unique slot identifier |
| `label` | No | Human-readable name (used in labels/rendering) |
| `type` | No | Slot kind string → ontology entity type mapping |
| `value` | No | User-supplied payload (string, object, or null) |

### Allowed values for `type`

See slot type mapping in [FIGURE_GRAMMAR.md](./FIGURE_GRAMMAR.md). Neutral types: `placeholder`, `label`, `text`, `shape`, `arrow`, `annotation`, `image`.

### Relationships

- Referenced by `layout.panels[].object_refs`
- Compiles to `Label`, `Shape`, `Arrow`, etc.
- Default type when omitted: maps to `Shape`

### Example

```yaml
content_slots:
  - id: "slot-1"
    label: "Primary content"
    type: "placeholder"
    value: null
  - id: "slot-arrow"
    label: "Step connection"
    type: "arrow"
    value: null
```

### Common mistakes

- Duplicate slot IDs
- Orphan slots (defined but not in any `object_refs`)
- Embedding coordinates or SVG in `value` without user request
- Using ontology type names as slot `id` values with colons (`fig-001:slot:x`)

### When to use

Define one slot per distinct content element the user wants placed in a panel.

### When NOT to use

Do not define slots for style files — use `styles.refs`. Do not define slots for panels themselves.

---

## Style References

### Purpose

Declare which files in `styles/` govern visual appearance. FSL references style documents; it does not embed colors, fonts, or typography values.

### Required

No (`styles` defaults to empty refs).

### Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `styles.refs[].ref` | Per ref | Path to a `styles/` file |
| `styles.overrides` | No | User-supplied key-value overrides |

### Allowed values

Paths under `styles/` that exist in the repository, e.g.:

- `styles/color-system.md`
- `styles/typography.md`
- `styles/annotation-styles.md`
- `styles/layout-grids.md`
- `styles/molecular-rendering.md`

**Note:** The FSL semantic validator does not currently verify style paths. Still use real paths — see [STYLING_GUIDE.md](./STYLING_GUIDE.md).

### Relationships

- Each ref compiles to an `Annotation` entity with `kind: style_reference`
- Figure root `REFERENCES` each style annotation
- Renderer may draw style refs as rounded labels at bottom of SVG

### Example

```yaml
styles:
  refs:
    - ref: "styles/color-system.md"
    - ref: "styles/typography.md"
  overrides: {}
```

### Common mistakes

- Embedding hex colors in FSL instead of referencing style files
- Inventing `styles/journal-nature.md` paths that do not exist
- Confusing `styles` with `content_slots` — styles are references, not drawable slots

---

## Rules

### Purpose

Declare which composition/labeling/accessibility rule files from `rules/` apply to this figure.

### Required

No (defaults to empty `refs`).

### Fields

| Field | Purpose |
|-------|---------|
| `rules.refs` | List of paths to `rules/*.md` files |

### Relationships

Not compiled into ontology entities today. Structural declaration for future validation engine.

### Example

```yaml
rules:
  refs:
    - "rules/composition.md"
```

### Common mistakes

- Inventing journal-specific rule files
- Expecting rules refs to affect SVG rendering directly (they do not in v0.7)

---

## Validation

### Purpose

Declare which pre-export validation checklists apply and which checks are mandatory.

### Required

No.

### Fields

| Field | Purpose |
|-------|---------|
| `validation.refs` | Paths to `validation/` checklist files |
| `validation.required_checks` | Checklist item IDs that must pass |

### Relationships

Not executed automatically in v0.7 — declaration for future validation engine.

### Example

```yaml
validation:
  refs:
    - "validation/pre-export-checklist.md"
  required_checks: []
```

### Common mistakes

- Assuming `validation.refs` triggers automatic validation (only FSL/compile/ontology validators run today)
- Inventing check IDs not defined in validation modules

---

## Knowledge

### Purpose

Optional references to domain knowledge packs under `knowledge/`.

### Required

No.

### Fields

| Field | Purpose |
|-------|---------|
| `knowledge.packs` | Paths to knowledge pack directories |

### Relationships

Not compiled. Placeholder for v0.8 knowledge base.

### When NOT to use

Do not populate with fabricated domain content. Use empty `packs: []` unless user supplies pack paths.

---

## Integrations

### Purpose

Placeholder object for external tool bindings (future BioRender, renderers, etc.).

### Required

No (defaults to `{}`).

### Allowed values

Any JSON object. Empty `{}` for current milestones.

### When NOT to use

Do not add BioRender or MCP configuration unless explicitly implementing that milestone.

---

## Export

### Purpose

Declares intended output formats and file naming pattern for publication export.

### Required

No.

### Fields

| Field | Purpose |
|-------|---------|
| `export.formats` | Format identifiers (e.g. `png`, `svg`) |
| `export.naming` | Naming pattern (e.g. `fig-{id}`) |

### Relationships

- `export.formats` copied to figure-root ontology metadata
- `export()` API writes files but does not validate format list

### Example

```yaml
export:
  formats:
    - "svg"
    - "png"
  naming: "fig-{id}"
```

### Common mistakes

- Expecting `export.formats` alone to produce files (must call `export()` or renderer)
- Inventing journal-specific naming schemes as enforced rules

---

## Cross-References

| Topic | Document |
|-------|----------|
| Every field alphabetically | [FIELD_REFERENCE.md](./FIELD_REFERENCE.md) |
| Layout panel counts | [LAYOUT_GUIDE.md](./LAYOUT_GUIDE.md) |
| Style paths | [STYLING_GUIDE.md](./STYLING_GUIDE.md) |
| FSL → ontology mapping | [OBJECT_MODEL.md](./OBJECT_MODEL.md) |
| Validation stages | [VALIDATION_RULES.md](./VALIDATION_RULES.md) |
| Invalid patterns | [COMMON_ERRORS.md](./COMMON_ERRORS.md) |
| Full examples | [EXAMPLES.md](./EXAMPLES.md) |