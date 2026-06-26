# Prompts Module

## Purpose

Provide prompt templates that orchestrate Claude through each stage of the figure design workflow. Prompts reference styles, rules, templates, and validation modules.

## Scope

**In scope:**

- Stage-specific prompt templates
- Variable slots for user-provided inputs
- Module reference instructions within prompts
- Prompt composition and chaining guidelines

**Out of scope:**

- Embedded scientific content or examples
- Hardcoded style values (reference `styles/` instead)
- Validation logic (reference `validation/` instead)

## Sections to be Completed

- [ ] Module overview and prompt pipeline
- [ ] Prompt file index with stage mapping
- [ ] Variable and slot naming conventions
- [ ] Prompt chaining order matching `instructions.md`
- [ ] Extension guidelines for new prompts

## TODO

- [ ] Complete each prompt file in this directory
- [ ] Define prompt variable schema
- [ ] Document how prompts enforce no-fabrication guardrails
- [ ] Specify prompt output format expectations