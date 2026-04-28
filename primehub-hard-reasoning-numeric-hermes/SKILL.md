---
name: primehub-hard-reasoning-numeric-hermes
description: "Use for PrimeIntellect numeric reasoning envs where correctness comes from decomposition and exact arithmetic verification, especially math_env, math500, gauss, and aime2024-2026."
---

# Primehub Hard Reasoning Numeric Hermes

Use this skill for Prime envs where the answer is earned by staged numeric reasoning, not just output repair.

## Local references

- Contract: `references/contract.md`

## Local scripts

- `scripts/build_skill_prompt.py`

## Skill contract

Follow the `Primehub-Hard-Reasoning-Numeric-v1` flow:

1. `TRM_PARSE`: normalize givens, unknowns, and the required final form.
2. `TRM_DECOMPOSE`: split the problem into 1-3 arithmetic or algebraic subgoals.
3. `TRM_SOLVE`: execute the minimal derivation needed for the final value.
4. `TRM_VERIFY`: recompute or sanity-check the result against constraints.
5. `FINAL`: emit only the exact final numeric answer string.

## Target envs

- `math_env`
- `math500`
- `gauss`
- `aime2024`
- `aime2025`
- `aime2026`

## Operational rules

- Prefer short derivations over long prose.
- Reject a candidate if the verification pass disagrees, even slightly.
- Preserve the task's required wrapper if one is explicit; otherwise emit the minimal exact final value.
- Use `scripts/build_skill_prompt.py --env-name ...` when you need the exact prompt text.
