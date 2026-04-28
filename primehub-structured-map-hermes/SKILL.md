---
name: primehub-structured-map-hermes
description: "Use for PrimeIntellect envs that require rigid line-structured or indexed outputs, especially psycho_bench and similar tasks where the model must preserve a schema rather than explain."
---

# Primehub Structured Map Hermes

Use this skill for Prime envs where the answer must follow a rigid line structure.

## Local references

- Contract: `references/contract.md`

## Local scripts

- `scripts/build_skill_prompt.py`

## Skill contract

Follow the `Primehub-Structured-Map-v1` flow:

1. `TRM_PARSE`: detect the required line schema.
2. `TRM_INDEX_PLAN`: decide the required keys or indices.
3. `TRM_FORMATTER`: emit only schema-conforming lines.
4. `TRM_VERIFY`: reject prose, bullets, code fences, and malformed lines.
5. `FINAL`: output only the structured payload.

## Target envs

- `psycho_bench`
- `ascii_tree`
- `pydantic_adherence`

## Operational rules

- Preserve line order and line count when the task implies a fixed template.
- Do not add headings, explanations, or code fences.
- Prefer exact schema compliance over stylistic fluency.
- Use `scripts/build_skill_prompt.py --env-name ...` when you need the exact prompt text.
