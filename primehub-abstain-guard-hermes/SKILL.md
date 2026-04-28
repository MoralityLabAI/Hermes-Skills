---
name: primehub-abstain-guard-hermes
description: "Use for PrimeIntellect envs where a negative critic decision may need one guarded override pass before final abstention, especially truthfulqa, wmdp, agency_bench, jailbreak_bench, and related honesty or safety tasks."
---

# Primehub Abstain Guard Hermes

Use this skill when the critic should default to abstention, but a narrow guarded override may recover a correct exact answer.

## Local references

- Contract: `references/contract.md`

## Local scripts

- `scripts/build_skill_prompt.py`

## Skill contract

Follow the `Primehub-Abstain-Guard-v1` flow:

1. `TRM_PARSE`: identify the answer contract and whether the env is abstention-heavy.
2. `TRM_CRITIC`: default conservative on uncertainty.
3. `TRM_OVERRIDE_CHECK`: allow one override only if the task contract is clear and the candidate bank is high-confidence.
4. `TRM_VERIFY`: reject unsafe or ill-formed overrides.
5. `FINAL`: emit the exact repaired answer or abstain.

## Target envs

- `truthfulqa`
- `wmdp`
- `agency_bench`
- `jailbreak_bench`
- `medsafetybench`

## Operational rules

- Default conservative; this skill is for guarded recovery, not reckless un-abstention.
- Only override a negative critic when the output contract is explicit and the candidate is highly constrained.
- If the override does not satisfy the contract exactly, keep the abstention path.
- Use `scripts/build_skill_prompt.py --env-name ...` when you need the exact prompt text.
