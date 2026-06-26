# Examples

Valid FSL examples with reasoning. Each passes schema, semantic, compiler, and ontology validation.

**See also:** [FSL_SPEC.md](./FSL_SPEC.md), [LAYOUT_GUIDE.md](./LAYOUT_GUIDE.md), [VALIDATION_RULES.md](./VALIDATION_RULES.md)

Verify any example:

```python
from figure_agent import validate_fsl, compile

assert validate_fsl(doc).valid
assert compile(doc).success
```

---

## Example 1: Minimal Figure (Single Panel)

**Intent:** Simplest valid figure — one panel, one slot.

**Why valid:**

- `single-panel` with exactly 1 panel
- `object_refs` matches `content_slots[].id`
- No orphan slots
- Known template and supported `fsl_version`

```yaml
fsl_version: "0.3.0"

metadata:
  id: "fig-001"
  title: "Placeholder Figure"
  author: "maintainer"
  provenance: []

template:
  ref: "templates/single-panel.md"
  params:
    aspect_ratio: "4:3"

layout:
  type: "single-panel"
  panels:
    - id: "panel-a"
      zones: ["primary"]
      object_refs: ["slot-1"]

styles:
  refs:
    - ref: "styles/color-system.md"
  overrides: {}

content_slots:
  - id: "slot-1"
    label: "Primary content"
    type: "placeholder"
    value: null

rules:
  refs:
    - "rules/composition.md"

validation:
  refs:
    - "validation/pre-export-checklist.md"
  required_checks: []

knowledge:
  packs: []

integrations: {}

export:
  formats:
    - "svg"
  naming: "fig-{id}"
```

**Compiles to:** 4 entities, 3 relationships (figure→panel, panel→slot, figure→style).

Source: `examples/minimal_figure.yaml`

---

## Example 2: Two Panels (Multi-Panel)

**Intent:** Side-by-side regions with distinct content.

**Why valid:**

- `multi-panel` requires ≥2 panels — provides 2
- Each panel references its own slot — no orphans
- Each slot referenced exactly once
- Distinct panel and slot IDs

```yaml
fsl_version: "0.3.0"

metadata:
  id: "fig-002"
  title: "Two Panel Figure"
  author: "maintainer"

template:
  ref: "templates/multi-panel.md"
  params: {}

layout:
  type: "multi-panel"
  panels:
    - id: "panel-a"
      zones: ["left"]
      object_refs: ["slot-1"]
    - id: "panel-b"
      zones: ["right"]
      object_refs: ["slot-2"]

styles:
  refs:
    - ref: "styles/color-system.md"
  overrides: {}

content_slots:
  - id: "slot-1"
    label: "Primary content"
    type: "placeholder"
    value: null
  - id: "slot-2"
    label: "Secondary content"
    type: "shape"
    value: null

rules:
  refs: []

validation:
  refs: []
  required_checks: []

knowledge:
  packs: []

integrations: {}

export:
  formats: ["svg"]
  naming: "fig-{id}"
```

**Compiles to:** 5 entities (figure, 2 panels, 2 slots, style), 5 `contains` + 1 `references`.

Source pattern: `tests/test_compiler.py` → `multi_panel_document()`

---

## Example 3: Three Panels (Multi-Panel)

**Intent:** Three distinct regions (e.g. top banner + two bottom panels).

**Why valid:**

- `multi-panel` allows unlimited panels above minimum 2
- Three unique panels, three unique slots, bijective references

```yaml
fsl_version: "0.3.0"

metadata:
  id: "fig-003"
  title: "Three Panel Figure"

template:
  ref: "templates/multi-panel.md"
  params: {}

layout:
  type: "multi-panel"
  panels:
    - id: "panel-top"
      zones: ["header"]
      object_refs: ["slot-header"]
    - id: "panel-left"
      zones: ["left"]
      object_refs: ["slot-left"]
    - id: "panel-right"
      zones: ["right"]
      object_refs: ["slot-right"]

styles:
  refs:
    - ref: "styles/color-system.md"
  overrides: {}

content_slots:
  - id: "slot-header"
    label: "Header region"
    type: "label"
  - id: "slot-left"
    label: "Left region"
    type: "placeholder"
  - id: "slot-right"
    label: "Right region"
    type: "placeholder"

rules:
  refs: []

validation:
  refs: []

knowledge:
  packs: []

integrations: {}

export:
  formats: ["svg"]
```

**Why NOT `single-panel`:** Would fail — max 1 panel allowed.

---

## Example 4: Workflow (Schematic Flow)

**Intent:** Sequential steps with an arrow connection.

**Why valid:**

- `schematic-flow` allows 1+ panels
- Multiple slots in one panel for vertical stacking
- `type: arrow` compiles to `Arrow` entity

```yaml
fsl_version: "0.3.0"

metadata:
  id: "fig-004"
  title: "Workflow Figure"

template:
  ref: "templates/schematic-flow.md"
  params: {}

layout:
  type: "schematic-flow"
  panels:
    - id: "panel-flow"
      zones: ["flow"]
      object_refs: ["slot-step-1", "slot-arrow-1", "slot-step-2"]

styles:
  refs:
    - ref: "styles/color-system.md"
    - ref: "styles/annotation-styles.md"
  overrides: {}

content_slots:
  - id: "slot-step-1"
    label: "Step one"
    type: "placeholder"
  - id: "slot-arrow-1"
    label: "Connection"
    type: "arrow"
  - id: "slot-step-2"
    label: "Step two"
    type: "placeholder"

rules:
  refs: []

validation:
  refs: []

knowledge:
  packs: []

integrations: {}

export:
  formats: ["svg"]
```

**Note:** Arrow placement is automatic in renderer — FSL does not specify coordinates.

---

## Example 5: Comparison Layout

**Intent:** Two regions for side-by-side comparison.

**Why valid:**

- `comparison-layout` requires ≥2 panels
- Template matches comparison intent
- Neutral labels — no fabricated scientific conditions

```yaml
fsl_version: "0.3.0"

metadata:
  id: "fig-005"
  title: "Comparison Figure"

template:
  ref: "templates/comparison-layout.md"
  params: {}

layout:
  type: "comparison-layout"
  panels:
    - id: "panel-left"
      zones: ["left"]
      object_refs: ["slot-left"]
    - id: "panel-right"
      zones: ["right"]
      object_refs: ["slot-right"]

styles:
  refs:
    - ref: "styles/color-system.md"
    - ref: "styles/typography.md"
  overrides: {}

content_slots:
  - id: "slot-left"
    label: "Condition A (user-supplied)"
    type: "placeholder"
  - id: "slot-right"
    label: "Condition B (user-supplied)"
    type: "placeholder"

rules:
  refs:
    - "rules/composition.md"

validation:
  refs: []

knowledge:
  packs: []

integrations: {}

export:
  formats: ["svg", "png"]
  naming: "fig-{id}"
```

---

## Counterexample: Invalid Two-Panel as Single-Panel

```yaml
layout:
  type: "single-panel"
  panels:
    - id: "panel-a"
      object_refs: ["slot-1"]
    - id: "panel-b"
      object_refs: ["slot-2"]
```

**Fails:** `allows at most 1 panel(s), found 2`

**Fix:** Change `type` to `multi-panel`.

---

## Counterexample: Invalid Orphan Slot

```yaml
content_slots:
  - id: "slot-1"
    type: "placeholder"
  - id: "slot-unused"
    type: "placeholder"
layout:
  type: "single-panel"
  panels:
    - id: "panel-a"
      object_refs: ["slot-1"]
```

**Fails at compile:** `slot-unused` orphaned.

**Fix:** Add `slot-unused` to `object_refs` or remove it.

---

## Complexity Progression

| Example | Panels | Slots | Layout type | New concept |
|---------|--------|-------|-------------|-------------|
| 1 Minimal | 1 | 1 | single-panel | Baseline |
| 2 Two panel | 2 | 2 | multi-panel | Multi-region |
| 3 Three panel | 3 | 3 | multi-panel | Extended multi |
| 4 Workflow | 1 | 3 | schematic-flow | Arrows in flow |
| 5 Comparison | 2 | 2 | comparison-layout | Comparison template |

---

## Related

- [LAYOUT_GUIDE.md](./LAYOUT_GUIDE.md) — layout selection
- [COMMON_ERRORS.md](./COMMON_ERRORS.md) — invalid variants
- [PROMPTING_GUIDE.md](./PROMPTING_GUIDE.md) — generating from user briefs