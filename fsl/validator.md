# FSL Validator

## Purpose

Define validation rules and checks for Figure Specification Language (FSL) documents. Ensures structural integrity before a specification proceeds to rendering or export.

## Scope

**In scope:**

- Structural validation rules for `schema.yaml` fields
- Reference integrity checks (templates, styles, rules, knowledge packs)
- Content slot completeness checks (structure only)
- Validator severity levels and reporting format

**Out of scope:**

- Scientific content accuracy
- Rendered output validation (see `validation/`)
- Automated validator implementation (v0.7 milestone)

---

## Validation Categories

| Category | Description | Severity |
|----------|-------------|----------|
| Schema | Required fields present and correctly typed | Error |
| References | Referenced files exist in repository | Error |
| Slots | All required content slots defined | Warning |
| Version | `fsl_version` is supported | Error |
| Metadata | Provenance fields populated | Warning |

---

## Sections to be Completed

- [ ] Required field checklist
- [ ] Type validation rules per `schema.yaml` field
- [ ] Reference resolution procedure
- [ ] Content slot completeness rules
- [ ] Validation report output format
- [ ] Integration with `validation/pre-export-checklist.md`

## TODO

- [ ] Define supported `fsl_version` values
- [ ] Document error vs warning handling
- [ ] Specify validator CLI or API interface (v0.7)
- [ ] Add example validation reports in `fsl/examples/`