---
name: trm-public-rationale-chain
description: "Use when you want a bounded public rationale trace layered on top of Hermes/TRM skills, especially for small-model experiments that need observable reasoning without claiming hidden chain-of-thought extraction."
---

# TRM Public Rationale Chain

Use this skill when the experiment explicitly allows a visible rationale channel and you want a small model to emit a short, bounded public trace instead of only a final answer.

## Local references

- Public trace contract: `references/public_trace_contract.md`

## Local scripts

- `scripts/build_skill_prompt.py`

## Skill contract

Follow the current `TRM-Public-Rationale-Chain-v1` contract:

1. `TRM_PARSE`: restate the task and answer contract in one short public line.
2. `TRM_CRITIC`: name the main consistency check or uncertainty in one short public line.
3. `TRM_COMPRESS`: compress the rationale to the minimum public statement that still supports the answer.
4. `FINAL`: emit the answer in the exact requested family format.

This is an observable rationale chain. It does not reveal hidden chain-of-thought, latent scratchpads, or inaccessible internal reasoning.

## Operational rules

- Use this skill only when the benchmark or training task explicitly permits a public trace channel.
- Keep the public trace to at most three rationale lines before the final answer line.
- Keep each public rationale line concrete, task-linked, and short.
- Prefer tagged lines or tiny JSON over freeform prose.
- If the critic cannot justify the answer confidently, surface the uncertainty in `TRM_CRITIC` and keep the final answer conservative.
- Preserve the base task contract. For logic, the final line must still be a completed grid. For math, the final line must still be the final answer string.
- Use `scripts/build_skill_prompt.py --task-family logic|math|generic` when you need the exact prompt text.

## Pairing guidance

- Pair with `intellect3-logic-hermes` when you want a visible trace for Campsite-style work and the eval permits rationale output.
- Pair with `intellect3-math-hermes` when you want a visible trace for arithmetic reasoning and the eval permits rationale output.
- Keep `trm-observability-workflow` as the collection and rollup path for turning these public traces into later TRM rows.
