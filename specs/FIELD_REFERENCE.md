# Field Reference

Alphabetical reference for every FSL field. Types and defaults match `src/figure_agent/fsl/models.py`.

**See also:** [FSL_SPEC.md](./FSL_SPEC.md), [COMMON_ERRORS.md](./COMMON_ERRORS.md)

---

## content_slots

| Property | Value |
|----------|-------|
| **Description** | Array of labeled content placeholders |
| **Type** | `ContentSlot[]` |
| **Required** | No (default `[]`) |
| **Default** | `[]` |
| **Allowed values** | List of slot objects |
| **Example** | `content_slots: [{ id: "slot-1", label: "Primary", type: "placeholder" }]` |

---

## content_slots[].id

| Property | Value |
|----------|-------|
| **Description** | Unique slot identifier within the figure |
| **Type** | `string` |
| **Required** | Yes |
| **Default** | — |
| **Allowed values** | Non-empty string; referenced by `object_refs` |
| **Example** | `"slot-1"` |

---

## content_slots[].label

| Property | Value |
|----------|-------|
| **Description** | Human-readable slot name |
| **Type** | `string \| null` |
| **Required** | No |
| **Default** | `null` |
| **Allowed values** | Any string |
| **Example** | `"Primary content"` |

---

## content_slots[].type

| Property | Value |
|----------|-------|
| **Description** | Slot kind; compiler maps to ontology entity type |
| **Type** | `string \| null` |
| **Required** | No |
| **Default** | `null` → compiles as `Shape` |
| **Allowed values** | `placeholder`, `text`, `label`, `image`, `asset`, `shape`, `structure`, `arrow`, `annotation`, `molecule`, `protein`, `ligand`, `cell`, etc. |
| **Example** | `"placeholder"` |

---

## content_slots[].value

| Property | Value |
|----------|-------|
| **Description** | User-supplied content payload |
| **Type** | `any` |
| **Required** | No |
| **Default** | `null` |
| **Allowed values** | `null`, string, number, object, array |
| **Example** | `null` or `"path/to/asset.png"` for image slots |

---

## export

| Property | Value |
|----------|-------|
| **Description** | Export targets and naming |
| **Type** | `ExportOptions` |
| **Required** | No |
| **Default** | `formats: []`, `naming: null` |
| **Example** | `export: { formats: ["svg"], naming: "fig-{id}" }` |

---

## export.formats

| Property | Value |
|----------|-------|
| **Description** | Target export format identifiers |
| **Type** | `string[]` |
| **Required** | No |
| **Default** | `[]` |
| **Allowed values** | Convention: `svg`, `png`, `pdf` (not enforced by schema) |
| **Example** | `["svg", "png"]` |

---

## export.naming

| Property | Value |
|----------|-------|
| **Description** | File naming pattern reference |
| **Type** | `string \| null` |
| **Required** | No |
| **Default** | `null` |
| **Allowed values** | Pattern string; `{id}` often replaced with `metadata.id` |
| **Example** | `"fig-{id}"` |

---

## fsl_version

| Property | Value |
|----------|-------|
| **Description** | FSL schema version |
| **Type** | `string` |
| **Required** | Yes |
| **Default** | — |
| **Allowed values** | `0.3.0`, `0.2.0-draft` |
| **Example** | `"0.3.0"` |

---

## integrations

| Property | Value |
|----------|-------|
| **Description** | External tool bindings placeholder |
| **Type** | `object` |
| **Required** | No |
| **Default** | `{}` |
| **Allowed values** | Any object; use `{}` when unused |
| **Example** | `integrations: {}` |

---

## knowledge

| Property | Value |
|----------|-------|
| **Description** | Knowledge pack references |
| **Type** | `KnowledgeConfig` |
| **Required** | No |
| **Default** | `packs: []` |

---

## knowledge.packs

| Property | Value |
|----------|-------|
| **Description** | Paths to `knowledge/` pack directories |
| **Type** | `string[]` |
| **Required** | No |
| **Default** | `[]` |
| **Example** | `[]` |

---

## layout

| Property | Value |
|----------|-------|
| **Description** | Spatial organization of panels |
| **Type** | `Layout` |
| **Required** | Yes |
| **Example** | `layout: { type: "single-panel", panels: [...] }` |

---

## layout.panels

| Property | Value |
|----------|-------|
| **Description** | Panel definitions |
| **Type** | `Panel[]` |
| **Required** | No |
| **Default** | `[]` |
| **Allowed values** | Must satisfy count rules for `layout.type` |

---

## layout.panels[].id

| Property | Value |
|----------|-------|
| **Description** | Unique panel identifier |
| **Type** | `string` |
| **Required** | Yes |
| **Default** | — |
| **Example** | `"panel-a"` |

---

## layout.panels[].object_refs

| Property | Value |
|----------|-------|
| **Description** | Content slot IDs displayed in this panel |
| **Type** | `string[]` |
| **Required** | No |
| **Default** | `[]` |
| **Allowed values** | Each value must match a `content_slots[].id` |
| **Example** | `["slot-1", "slot-2"]` |

---

## layout.panels[].zones

| Property | Value |
|----------|-------|
| **Description** | Named zones within the panel |
| **Type** | `string[]` |
| **Required** | No |
| **Default** | `[]` |
| **Allowed values** | Semantic labels (e.g. `primary`, `left`, `legend`) |
| **Example** | `["primary"]` |

---

## layout.type

| Property | Value |
|----------|-------|
| **Description** | Layout category identifier |
| **Type** | `string` |
| **Required** | Yes |
| **Allowed values** | `single-panel`, `multi-panel`, `schematic-flow`, `comparison-layout` |
| **Panel rules** | See [LAYOUT_GUIDE.md](./LAYOUT_GUIDE.md) |
| **Example** | `"single-panel"` |

---

## metadata

| Property | Value |
|----------|-------|
| **Description** | Figure identity and attribution |
| **Type** | `Metadata` |
| **Required** | Yes |

---

## metadata.author

| Property | Value |
|----------|-------|
| **Description** | Specification author |
| **Type** | `string \| null` |
| **Required** | No |
| **Default** | `null` |
| **Example** | `"maintainer"` |

---

## metadata.created

| Property | Value |
|----------|-------|
| **Description** | ISO 8601 creation timestamp |
| **Type** | `string \| null` |
| **Required** | No |
| **Default** | `null` |
| **Example** | `"2026-06-26T12:00:00Z"` |

---

## metadata.id

| Property | Value |
|----------|-------|
| **Description** | Unique figure specification identifier |
| **Type** | `string` |
| **Required** | Yes |
| **Default** | — |
| **Example** | `"fig-001"` |

---

## metadata.modified

| Property | Value |
|----------|-------|
| **Description** | ISO 8601 modification timestamp |
| **Type** | `string \| null` |
| **Required** | No |
| **Default** | `null` |

---

## metadata.provenance

| Property | Value |
|----------|-------|
| **Description** | Source references and attribution entries |
| **Type** | `object[]` |
| **Required** | No |
| **Default** | `[]` |
| **Example** | `[]` |

---

## metadata.title

| Property | Value |
|----------|-------|
| **Description** | Human-readable figure title |
| **Type** | `string` |
| **Required** | Yes |
| **Example** | `"Placeholder Figure"` |

---

## rules

| Property | Value |
|----------|-------|
| **Description** | Rule file references |
| **Type** | `RulesConfig` |
| **Required** | No |
| **Default** | `refs: []` |

---

## rules.refs

| Property | Value |
|----------|-------|
| **Description** | Paths to `rules/` files |
| **Type** | `string[]` |
| **Required** | No |
| **Default** | `[]` |
| **Example** | `["rules/composition.md"]` |

---

## styles

| Property | Value |
|----------|-------|
| **Description** | Style bindings |
| **Type** | `StylesConfig` |
| **Required** | No |
| **Default** | `refs: []`, `overrides: {}` |

---

## styles.overrides

| Property | Value |
|----------|-------|
| **Description** | User-supplied style overrides |
| **Type** | `object` |
| **Required** | No |
| **Default** | `{}` |
| **Example** | `{}` |

---

## styles.refs

| Property | Value |
|----------|-------|
| **Description** | Style file references |
| **Type** | `StyleReference[]` |
| **Required** | No |
| **Default** | `[]` |

---

## styles.refs[].ref

| Property | Value |
|----------|-------|
| **Description** | Path to a `styles/` file |
| **Type** | `string` |
| **Required** | Yes (per ref entry) |
| **Example** | `"styles/color-system.md"` |

---

## template

| Property | Value |
|----------|-------|
| **Description** | Template reference |
| **Type** | `TemplateReference` |
| **Required** | Yes |

---

## template.params

| Property | Value |
|----------|-------|
| **Description** | Template parameter bindings |
| **Type** | `object` |
| **Required** | No |
| **Default** | `{}` |
| **Example** | `{ aspect_ratio: "4:3" }` |

---

## template.ref

| Property | Value |
|----------|-------|
| **Description** | Path to `templates/` file |
| **Type** | `string` |
| **Required** | Yes |
| **Allowed values** | Known templates only (semantic validation) |
| **Example** | `"templates/single-panel.md"` |

---

## validation

| Property | Value |
|----------|-------|
| **Description** | Validation configuration |
| **Type** | `ValidationOptions` |
| **Required** | No |
| **Default** | `refs: []`, `required_checks: []` |

---

## validation.refs

| Property | Value |
|----------|-------|
| **Description** | Paths to `validation/` files |
| **Type** | `string[]` |
| **Required** | No |
| **Default** | `[]` |
| **Example** | `["validation/pre-export-checklist.md"]` |

---

## validation.required_checks

| Property | Value |
|----------|-------|
| **Description** | Checklist item IDs that must pass |
| **Type** | `string[]` |
| **Required** | No |
| **Default** | `[]` |

---

## Related

- [FSL_SPEC.md](./FSL_SPEC.md) — semantic explanations
- [FIGURE_GRAMMAR.md](./FIGURE_GRAMMAR.md) — language rules
- [VALIDATION_RULES.md](./VALIDATION_RULES.md) — what validators check