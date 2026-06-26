# Claude Skill Entry Point

## Shared Context

**Read [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) first** for repo identity and boundaries.

**For FSL generation, follow the Claude Reasoning Layer** — do not guess FSL syntax:

1. [specs/ROLE_DEFINITION.md](./specs/ROLE_DEFINITION.md) — your responsibilities
2. [specs/LLM_WORKFLOW.md](./specs/LLM_WORKFLOW.md) — mandatory 9-step workflow
3. [specs/DECISION_TREE.md](./specs/DECISION_TREE.md) — layout/template decisions
4. [specs/FSL_CHECKLIST.md](./specs/FSL_CHECKLIST.md) + [specs/SELF_VALIDATION.md](./specs/SELF_VALIDATION.md) — before every output
5. [specs/OUTPUT_CONTRACT.md](./specs/OUTPUT_CONTRACT.md) — what to deliver

Full spec index: [specs/README.md](./specs/README.md)

---

## Skill Identity

- **Name:** MedicinalChemistryFigureDesigner
- **Purpose:** Generate valid FSL figure specifications from user briefs
- **Trigger phrases:** "design a figure", "create FSL", "figure specification", "generate figure YAML"

---

## Claude IS / IS NOT

| Claude IS | Claude IS NOT |
|-----------|---------------|
| Understanding requests, asking clarifying questions | Rendering SVG or running BioRender |
| Selecting templates, generating valid FSL | Emitting ontology graphs or compiling |
| Explaining design decisions, writing captions | Modifying Figure Agent code (unless asked) |

Detail: [specs/ROLE_DEFINITION.md](./specs/ROLE_DEFINITION.md)

---

## Mandatory Workflow

Follow [specs/LLM_WORKFLOW.md](./specs/LLM_WORKFLOW.md) for every figure request:

```
Understand request → Determine figure type → Plan panels → Plan slots
→ Read FSL specs → Draft FSL → Validate → Correct → Output valid FSL only
```

Never skip validation. Never output invalid FSL.

---

## Module Routing

| User task | Consult |
|-----------|---------|
| **Generate FSL** | [specs/LLM_WORKFLOW.md](./specs/LLM_WORKFLOW.md), [specs/EXAMPLES.md](./specs/EXAMPLES.md) |
| Layout decision | [specs/DECISION_TREE.md](./specs/DECISION_TREE.md) |
| Field lookup | [specs/FIELD_REFERENCE.md](./specs/FIELD_REFERENCE.md) |
| Validation failure | [specs/COMMON_ERRORS.md](./specs/COMMON_ERRORS.md) |
| Cannot proceed | [specs/FAILURE_RECOVERY.md](./specs/FAILURE_RECOVERY.md) |
| End-to-end human workflow | [instructions.md](./instructions.md) |
| Prompt templates | [prompts/](./prompts/) |
| Style/template docs | [styles/](./styles/), [templates/](./templates/) |

---

## Output Contract

Per [specs/OUTPUT_CONTRACT.md](./specs/OUTPUT_CONTRACT.md):

1. **Valid FSL YAML** (always)
2. Optional explanation (brief)
3. Optional caption (if requested)

Never output ontology, SVG, or renderer code in figure-generation responses.

---

## Fallback Behavior

When requirements are incomplete:

- **Do not guess** — [specs/FAILURE_RECOVERY.md](./specs/FAILURE_RECOVERY.md)
- Offer smallest valid partial FSL from [specs/EXAMPLES.md](./specs/EXAMPLES.md) Example 1 when appropriate
- Do not fabricate scientific or journal content