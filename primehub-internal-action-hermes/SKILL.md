---
name: primehub-internal-action-hermes
description: "Use for PrimeIntellect envs where the correct move may be an internal or deferred action such as inspect_and_continue rather than immediate visible output, especially antislop-style tasks."
---

# Primehub Internal Action Hermes

Use this skill when the right answer may be to continue internally instead of emitting visible content.

## Local references

- Contract: `references/contract.md`

## Local scripts

- `scripts/build_skill_prompt.py`

## Skill contract

Follow the `Primehub-Internal-Action-v1` flow:

1. `TRM_PARSE`: detect whether the task expects immediate output or internal continuation.
2. `TRM_CRITIC`: reject visible output if the task state says to continue internally.
3. `TRM_INTERNAL_ACT`: prefer `inspect_and_continue` when that is the valid action.
4. `TRM_VERIFY`: confirm the action matches the visibility contract.
5. `FINAL`: emit only the action token.

## Target envs

- `antislop`

## Operational rules

- Distinguish visible text generation from internal continuation explicitly.
- If the valid move is internal, emit only `inspect_and_continue`.
- Do not leak draft content when the contract says to continue internally.
- Use `scripts/build_skill_prompt.py --env-name ...` when you need the exact prompt text.
