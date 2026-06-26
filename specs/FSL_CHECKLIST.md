# FSL Checklist

Pre-output verification checklist for Claude. Every item must pass before delivering FSL.

**See also:** [SELF_VALIDATION.md](./SELF_VALIDATION.md), [VALIDATION_RULES.md](./VALIDATION_RULES.md), [FIELD_REFERENCE.md](./FIELD_REFERENCE.md)

---

## Human Checklist

Before outputting FSL, verify:

- [ ] **Required fields** — `fsl_version`, `metadata`, `template`, `layout` present
- [ ] **Panel IDs** — unique within `layout.panels`
- [ ] **Slot IDs** — unique within `content_slots`
- [ ] **Layout** — `layout.type` known; panel count satisfies rules
- [ ] **Style references** — paths under `styles/` that exist in repo (convention)
- [ ] **Export section** — `export.formats` and `export.naming` present if figure is complete
- [ ] **No ontology entities** — no namespaced IDs, no `EntityType` names, no `relationships` block
- [ ] **No renderer instructions** — no coordinates, SVG, colors, or `render()` calls in FSL
- [ ] **No unsupported fields** — no extra keys (`extra="forbid"` on all models)
- [ ] **object_refs** — every ref matches a `content_slots[].id`
- [ ] **No orphan slots** — every slot in at least one `object_refs`
- [ ] **Template ref** — in `KNOWN_TEMPLATES`
- [ ] **fsl_version** — `0.3.0` (preferred) or `0.2.0-draft`

---

## Machine-Readable Checklist

Use this YAML structure for automated or structured self-checks:

```yaml
fsl_output_checklist:
  version: "0.8"
  checks:
    - id: required_top_level
      description: Top-level keys fsl_version, metadata, template, layout exist
      required: true
      spec: FIELD_REFERENCE.md

    - id: fsl_version_supported
      description: fsl_version in {0.3.0, 0.2.0-draft}
      required: true
      allowed_values: ["0.3.0", "0.2.0-draft"]

    - id: metadata_id
      description: metadata.id non-empty string
      required: true

    - id: metadata_title
      description: metadata.title non-empty string
      required: true

    - id: template_ref_known
      description: template.ref in KNOWN_TEMPLATES
      required: true
      allowed_values:
        - templates/single-panel.md
        - templates/multi-panel.md
        - templates/schematic-flow.md
        - templates/comparison-layout.md
        - templates/legend-block.md

    - id: layout_type_known
      description: layout.type in KNOWN_LAYOUT_TYPES
      required: true
      allowed_values:
        - single-panel
        - multi-panel
        - schematic-flow
        - comparison-layout

    - id: layout_panel_count
      description: Panel count matches LAYOUT_PANEL_RULES for layout.type
      required: true
      rules:
        single-panel: { min: 1, max: 1 }
        multi-panel: { min: 2, max: null }
        schematic-flow: { min: 1, max: null }
        comparison-layout: { min: 2, max: null }

    - id: panel_ids_unique
      description: All layout.panels[].id unique
      required: true

    - id: slot_ids_unique
      description: All content_slots[].id unique
      required: true

    - id: object_refs_resolve
      description: Every panels[].object_refs value exists in content_slots[].id
      required: true

    - id: no_orphan_slots
      description: Every content_slots[].id appears in at least one object_refs
      required: true
      stage: compile

    - id: no_ontology_in_fsl
      description: No relationships block, no namespaced IDs (fig-001:slot:), no EntityType names
      required: true
      spec: FIGURE_GRAMMAR.md

    - id: no_renderer_in_fsl
      description: No x/y/width/height, svg, canvas, or render keys
      required: true

    - id: no_extra_fields
      description: No keys outside Figure model
      required: true

    - id: styles_refs_format
      description: styles.refs[].ref paths use styles/ prefix
      required: false

    - id: export_present
      description: export.formats defined
      required: false
```

---

## Layout Panel Count Quick Table

| layout.type | Min panels | Max panels |
|-------------|------------|------------|
| `single-panel` | 1 | 1 |
| `multi-panel` | 2 | ∞ |
| `schematic-flow` | 1 | ∞ |
| `comparison-layout` | 2 | ∞ |

---

## Validation API Mapping

| Checklist item | API / stage |
|----------------|-------------|
| Schema checks | `validate_fsl()` → `valid: true` |
| Semantic checks | `validate_fsl()` |
| Orphan slots | `compile()` → `success: true` |
| Full pipeline | `compile()` then `render_svg()` if preview requested |

Detail: [VALIDATION_RULES.md](./VALIDATION_RULES.md)

---

## On Failure

Do not output FSL until all **required** checks pass. See [FAILURE_RECOVERY.md](./FAILURE_RECOVERY.md) and [COMMON_ERRORS.md](./COMMON_ERRORS.md).

---

## Related

- [../PROJECT_CONTEXT.md](../PROJECT_CONTEXT.md)
- [../README.md](../README.md)
- [FSL_SPEC.md](./FSL_SPEC.md)
- [SELF_VALIDATION.md](./SELF_VALIDATION.md)
- [LLM_WORKFLOW.md](./LLM_WORKFLOW.md) — step 7