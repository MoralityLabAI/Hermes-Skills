---
name: primehub-hard-reasoning-logic-hermes
description: "Use for PrimeIntellect logic-heavy reasoning envs where the gain comes from explicit state tracking and elimination, especially logic_env, science_env, lisanbench, mmlu_pro, and related exact-answer reasoning tasks."
---

# Primehub Hard Reasoning Logic Hermes

Use this skill for Prime envs where the answer depends on maintaining a crisp latent state table, eliminating wrong branches, and only then formatting the answer.

## Local references

- Contract: `references/contract.md`

## Local scripts

- `scripts/build_skill_prompt.py`

## Skill contract

Follow the `Primehub-Hard-Reasoning-Logic-v1` flow:

1. `TRM_PARSE`: extract entities, constraints, and the requested decision.
2. `TRM_STATE_TABLE`: keep a compact latent table of cases or claims.
3. `TRM_ELIMINATE`: remove impossible branches or unsupported answers.
4. `TRM_VERIFY`: compare the surviving candidate against the exact question wording.
5. `FINAL`: emit only the exact final answer token or string.

## Target envs

- `logic_env`
- `science_env`
- `lisanbench`
- `mmlu_pro`
- `bixbench`

## Operational rules

- Track contradictions before choosing an answer.
- Do not let stylistic confidence substitute for elimination.
- If the env is multiple-choice, emit only the final choice token requested by the task.
- Use `scripts/build_skill_prompt.py --env-name ...` when you need the exact prompt text.
