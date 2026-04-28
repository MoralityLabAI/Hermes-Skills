---
name: primehub-choice-contract-hermes
description: "Use for PrimeIntellect envs with strict answer wrappers or fixed small answer sets, especially truthfulqa, boolq, simple_bench, arc, hellaswag, winogrande, and instruction-following evals where exact contract repair beats a raw generalized TRM."
---

# Primehub Choice Contract Hermes

Use this skill for Prime envs where the hard part is not only reasoning, but also landing the exact answer contract.

## Local references

- Contract: `references/contract.md`

## Local scripts

- `scripts/build_skill_prompt.py`

## Skill contract

Follow the `Primehub-Choice-Contract-v1` flow:

1. `TRM_PARSE`: identify the semantic answer and the exact output wrapper.
2. `TRM_CRITIC`: decide whether the answer should be emitted or abstained.
3. `TRM_FORMATTER`: rewrite the semantic answer into the required wrapper only.
4. `TRM_VERIFY`: check wrapper legality, allowed symbol set, and one-line exactness.
5. `FINAL`: emit only the repaired answer string.

## Target envs

- `truthfulqa`
- `boolq`
- `simple_bench`
- `arc`
- `hellaswag`
- `winogrande`
- `mmlu_pro`
- `allenai_ifeval`
- `simpleqa`
- `simpleqa_verified`
- `simpleqa_verified_2`

## Operational rules

- Do not change the semantic answer during formatting; only change the wrapper.
- Prefer exact wrapper repair such as `A -> Final Answer: A`, `A -> \boxed{A}`, or `A -> True` only when the task contract supports it.
- If the critic is clearly negative, keep `__ABSTAIN__` behavior rather than forcing a wrapper.
- Use `scripts/build_skill_prompt.py --env-name ...` when you need the exact prompt text.
