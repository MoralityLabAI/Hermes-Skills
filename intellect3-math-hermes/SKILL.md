---
name: intellect3-math-hermes
description: "Use for Intellect-3-Math work, including the Hermes math contract, TRM-augmented routing, local benchmark receipts, and prompt generation."
---

# Intellect-3 Math Hermes

Use this skill for `Intellect-3-Math` tasks and for the packaged Hermes math contract, prompt helper, and benchmark receipts.

## Local references

- Skill contract: `references/contract.md`
- Generalizability memo: `references/learnings-3-27.md`
- Receipt summary: `references/receipts.md`
- Hybrid receipts: `references/math_hybrid_200.summary.json`
- Router receipts: `references/math_router_100.summary.json`

## Local scripts

- `scripts/build_skill_prompt.py`
- `scripts/check_support_pattern.py`
- `scripts/show_receipts.py`

## Skill contract

Follow the current `Hermes/Intellect-3-Math-v1` contract:

1. Parse the givens.
2. Solve with a short candidate path.
3. Verify arithmetic consistency.
4. Commit the final answer.

Treat TRM signals as experimental advisory evidence inside the skill workspace. Default to the plain math skill path. Use the TRM path only when an explicit support pattern from the current benchmark artifacts says it is helpful. When prompt text is available locally, use `scripts/check_support_pattern.py` instead of guessing.

## Current status

- The packaged 200-row receipts do not show a net aggregate win over vanilla yet.
- Until the math collector produces a healthier exact-positive set, keep TRM opt-in rather than default.
- A 27B-drafted MeTTa self-improvement prompt did not beat the current skill on
  the first 10 held-out rows (`2/10` vs current skill `3/10`). Treat MeTTa patch
  generation as propose-and-test; do not adopt a patch unless the held-out
  commit gate passes.
- The active research direction is the skill-patch gym: maintain a patch bank,
  evaluate patches on held-out rows, and train a TRM commit/veto controller over
  patch outcomes.
- A 20-row live 27B patch-bank benchmark kept the incumbent ahead (`4/20`);
  no whole patch cleared the global adoption gate.  There was still row-level
  signal: one Qwen auditor output fixed an incumbent miss, so train/select at
  row level before promoting any whole prompt patch.

## Operational rules

- Return only the final integer answer string.
- Keep the reasoning short and bounded.
- When benchmark state is unknown or no explicit support pattern is present, stay on the plain math path.
- For MeTTa-generated skill revisions, require a held-out exact improvement and
  fixes greater than or equal to regressions before changing the skill contract.
- Prefer patch-bank search over single prompt mutation when trying to improve
  this skill.
- Distinguish global patch adoption from row-level patch selection.  A patch can
  be globally rejected while still providing positive row-level commit examples.
- For visible-rationale experiments, pair this skill with `trm-public-rationale-chain` only when the eval explicitly permits a trace channel.
- Use `scripts/build_skill_prompt.py` when you need the exact skill prompt.
- Use `scripts/check_support_pattern.py --text ...` when you need a route decision.
- Use `scripts/show_receipts.py` when you need the packaged evidence.
- For repo sync, teacher collection, row building, and bench iteration, use `trm-observability-workflow`.
