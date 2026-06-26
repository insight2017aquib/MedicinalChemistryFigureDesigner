# LLM Specification Layer

Reasoning specifications for Large Language Models generating valid Figure Specification Language (FSL) documents.

**This is not user documentation, API documentation, or developer documentation.**

It is the semantic layer that teaches Claude and future LLMs how to think about, construct, and validate FSL.

**Synchronized with:** Figure Agent v0.7.0 (`src/figure_agent/fsl/`, `compiler/`, `ontology/`, `renderers/`)

---

## Who Should Read This

- LLMs asked to **generate**, **edit**, or **validate** FSL YAML/JSON
- Agents using `generate_fsl()` or producing figure specifications by hand
- Prompt engineers wiring figure-design workflows

Humans maintaining the platform should use `README.md`, `docs/`, and `fsl/` instead.

---

## Document Map

| Document | Purpose |
|----------|---------|
| [FSL_SPEC.md](./FSL_SPEC.md) | Semantic meaning of every major FSL construct |
| [FIGURE_GRAMMAR.md](./FIGURE_GRAMMAR.md) | Language rules and layer boundaries |
| [FIELD_REFERENCE.md](./FIELD_REFERENCE.md) | Alphabetical field reference |
| [OBJECT_MODEL.md](./OBJECT_MODEL.md) | FSL object → ontology entity → rendered output |
| [LAYOUT_GUIDE.md](./LAYOUT_GUIDE.md) | Layout types and panel composition |
| [STYLING_GUIDE.md](./STYLING_GUIDE.md) | Style references and overrides |
| [VALIDATION_RULES.md](./VALIDATION_RULES.md) | Four validation stages |
| [COMMON_ERRORS.md](./COMMON_ERRORS.md) | Mistakes and corrections |
| [EXAMPLES.md](./EXAMPLES.md) | Valid examples with reasoning |
| [PROMPTING_GUIDE.md](./PROMPTING_GUIDE.md) | How LLMs should produce FSL |

---

## Reading Order for LLMs

**First time generating FSL:**

1. [FIGURE_GRAMMAR.md](./FIGURE_GRAMMAR.md) — understand what FSL is and is not
2. [FSL_SPEC.md](./FSL_SPEC.md) — learn each construct semantically
3. [EXAMPLES.md](./EXAMPLES.md) — copy patterns from valid documents
4. [FIELD_REFERENCE.md](./FIELD_REFERENCE.md) — look up individual fields
5. [VALIDATION_RULES.md](./VALIDATION_RULES.md) — verify before submitting
6. [COMMON_ERRORS.md](./COMMON_ERRORS.md) — fix failures

**When stuck:** [PROMPTING_GUIDE.md](./PROMPTING_GUIDE.md)

---

## Hard Rules for LLMs

1. **FSL describes structure, not rendered graphics.** Panels reference content slots; they do not embed ontology entities, coordinates, or relationships.
2. **Do not invent biology, chemistry, or journal standards.** Use neutral placeholders (`placeholder`, `shape`, `label`) and repository paths that exist.
3. **Do not invent layout types.** Only use values from `KNOWN_LAYOUT_TYPES` in the implementation.
4. **Every panel `object_ref` must match a `content_slots[].id`.** Every slot must be referenced by at least one panel (compiler orphan check).
5. **Relationships exist only in the ontology layer.** The compiler creates `contains` and `references` relationships; FSL has no relationship syntax.
6. **Validate before claiming success.** Run `validate_fsl()` or `parse()` — schema errors and semantic errors are distinct.

---

## Cross-Reference Graph

```mermaid
flowchart TD
    README[README.md] --> Grammar[FIGURE_GRAMMAR.md]
    Grammar --> Spec[FSL_SPEC.md]
    Spec --> Fields[FIELD_REFERENCE.md]
    Spec --> Layout[LAYOUT_GUIDE.md]
    Spec --> Style[STYLING_GUIDE.md]
    Spec --> Object[OBJECT_MODEL.md]
    Fields --> Errors[COMMON_ERRORS.md]
    Layout --> Examples[EXAMPLES.md]
    Style --> Examples
    Spec --> Validation[VALIDATION_RULES.md]
    Validation --> Errors
    Examples --> Prompting[PROMPTING_GUIDE.md]
    Errors --> Prompting
```

---

## Implementation Anchors

When in doubt, derive behavior from these source files — do not guess:

| Behavior | Source |
|----------|--------|
| FSL schema (types, required fields) | `src/figure_agent/fsl/models.py` |
| Semantic validation | `src/figure_agent/fsl/validator.py` |
| Supported versions, layouts, templates | `src/figure_agent/core/constants.py` |
| FSL → ontology mapping | `src/figure_agent/compiler/mapping.py` |
| Compilation validation | `src/figure_agent/compiler/validator.py` |
| Ontology validation | `src/figure_agent/ontology/validator.py` |
| Minimal valid example | `examples/minimal_figure.yaml` |

---

## Related (Outside This Layer)

| Resource | Audience |
|----------|----------|
| `PROJECT_CONTEXT.md` | General agent context for the whole repo |
| `README.md` | Human project overview |
| `src/figure_agent/api/` | Python API for validate/compile/render |
| `fsl/schema.yaml` | Schema skeleton (not a substitute for semantics) |