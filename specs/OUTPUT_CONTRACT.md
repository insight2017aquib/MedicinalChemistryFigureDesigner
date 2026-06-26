# Output Contract

Exactly what Claude is allowed to output when generating figures.

**See also:** [ROLE_DEFINITION.md](./ROLE_DEFINITION.md), [LLM_WORKFLOW.md](./LLM_WORKFLOW.md), [SELF_VALIDATION.md](./SELF_VALIDATION.md)

---

## Priority Order

Responses must follow this order:

| Priority | Deliverable | Required |
|----------|-------------|----------|
| **1** | Valid FSL (YAML in fenced code block) | **Always** when user requests a figure spec |
| **2** | Optional explanation (design decisions) | After FSL, brief |
| **3** | Optional caption (plain text for publication) | User-requested only |

**Never** reorder priorities — valid FSL comes first.

---

## Allowed Output

### 1. Valid FSL

- Complete YAML document
- Passes `validate_fsl()` and `compile()` rules
- Conforms to [FSL_SPEC.md](./FSL_SPEC.md) and [FIGURE_GRAMMAR.md](./FIGURE_GRAMMAR.md)

```yaml
# Example format — fenced ```yaml block in response
fsl_version: "0.3.0"
metadata:
  id: "fig-001"
  title: "Placeholder Figure"
# ... complete document
```

### 2. Optional explanation

- Why `layout.type` and `template.ref` were chosen
- Which slots need user content
- Reference to [DECISION_TREE.md](./DECISION_TREE.md) reasoning

Keep under one short paragraph unless user asks for detail.

### 3. Optional caption

- Plain-text figure caption for a paper
- **Not** embedded in FSL unless user supplies caption as slot `label`
- Clearly labeled: "Suggested caption:"

---

## Forbidden Output

| Forbidden | Why |
|-----------|-----|
| **Ontology JSON/YAML** | Compiler output — [OBJECT_MODEL.md](./OBJECT_MODEL.md) |
| **SVG markup** | Renderer output |
| **Renderer-specific instructions** | `render()`, coordinates, canvas size in FSL |
| **Implementation code** | Python, compiler patches, unless user requests engineering |
| **BioRender commands** | Not implemented |
| **Invalid FSL** | Must self-validate first |
| **Fabricated scientific data** | User-supplied only |

---

## Response Template

```markdown
[Suggested caption: only if requested]

```yaml
# complete valid FSL document
```

**Structure:** {N} panel(s), {M} slot(s), layout `{layout.type}`.
**User action needed:** [list slots requiring user content, or "none"]
```

---

## When User Asks for Rendering

Claude does **not** render. Respond:

1. Deliver valid FSL (priority 1)
2. Explain that rendering is downstream: `export(figure, "output/figure.svg")` in Figure Agent
3. Do not include SVG in the response unless user explicitly runs tooling and shares output

Per [ROLE_DEFINITION.md](./ROLE_DEFINITION.md) — rendering is not Claude's responsibility.

---

## When User Asks for Ontology

Decline to output ontology. Explain:

- FSL compiles to ontology via `compile()`
- Claude's contract is FSL only

---

## Cross-References

- [../README.md](../README.md) — project overview
- [../PROJECT_CONTEXT.md](../PROJECT_CONTEXT.md) — API boundaries
- [FSL_SPEC.md](./FSL_SPEC.md)
- [FIELD_REFERENCE.md](./FIELD_REFERENCE.md)
- [EXAMPLES.md](./EXAMPLES.md) — output shape reference
- [FAILURE_RECOVERY.md](./FAILURE_RECOVERY.md) — when valid FSL is not possible