---
name: primehub-constraint-summarize-hermes
description: "Use for PrimeIntellect constrained summarization envs where the model must infer a structural family from the instruction and satisfy it exactly, especially if_summarize_judge."
---

# Primehub Constraint Summarize Hermes

Use this skill for Prime envs where the answer is still prose-like, but the hard part is a tight structural constraint rather than open summarization quality.

## Local references

- Contract: `references/contract.md`

## Local scripts

- `scripts/build_skill_prompt.py`

## Skill contract

Follow the `Primehub-Constraint-Summarize-v1` flow:

1. `TRM_PARSE`: read the instruction literally and isolate the structural ask.
2. `TRM_CLASSIFY_CONSTRAINT`: map the task to the active family such as exact word count, punctuation count, headline casing, hashtags, question form, or XML wrapping.
3. `TRM_STRUCTURE_PLAN`: decide the minimal text shape that satisfies the family.
4. `TRM_VERIFY_COUNTS`: check counts, delimiters, casing, wrappers, and sentence endings before final output.
5. `FINAL`: emit only the constrained summary text.

## Target envs

- `if_summarize_judge`

## Operational rules

- Treat structural compliance as the first objective and content quality as secondary.
- Do not add prefatory text, rationale, code fences, or extra lines unless the family explicitly demands bullets.
- If the family is unknown, fall back to the smallest valid structure that still matches the literal request.
- Use `scripts/build_skill_prompt.py --env-name ...` when you need the exact prompt text.
