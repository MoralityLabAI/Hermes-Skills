---
name: intellect3-logic-hermes
description: "Use for Campsite / Intellect-3-Logic work, including the Hermes skill contract, TRM-augmented routing, local benchmark receipts, and prompt generation."
---

# Intellect-3 Logic Hermes

Use this skill for Campsite / `Intellect-3-Logic` tasks and for the packaged Hermes contract, prompt helper, and benchmark receipts.

## Local references

- Skill contract: `references/contract.md`
- Generalizability memo: `references/learnings-3-27.md`
- Receipt summary: `references/receipts.md`
- Hybrid receipts: `references/logic_hybrid_200.summary.json`
- Router receipts: `references/logic_router_200.summary.json`

## Local scripts

- `scripts/build_skill_prompt.py`
- `scripts/check_signature_gate.py`
- `scripts/show_receipts.py`

## Skill contract

Follow the current `Hermes/Intellect-3-Logic-v1` contract:

1. Parse the grid and the row / column signatures.
2. Build an initial candidate.
3. Verify tent adjacency, row counts, column counts, and tree pairing.
4. Commit the final grid.

When row and column constraints are available, use `scripts/check_signature_gate.py` to route deterministically. Route to the TRM-augmented workspace only on an exact signature match. Otherwise stay on the plain skill path.

## Operational rules

- Keep the output to the completed `T` / `X` / `C` grid only.
- Treat the exact row/column signature as the current best routing signal.
- Prefer `scripts/check_signature_gate.py` over hand-checking the summary JSON or guessing from puzzle shape.
- If a mixed trajectory file contains non-logic rows, filter to true Campsite rows before benchmarking.
- For visible-rationale experiments, pair this skill with `trm-public-rationale-chain` only when the eval explicitly permits a trace channel.
- Use `scripts/build_skill_prompt.py` when you need the exact skill prompt.
- Use `scripts/check_signature_gate.py --rows ... --cols ...` when you need a route decision.
- Use `scripts/show_receipts.py` when you need the packaged evidence.
- For repo sync, teacher collection, row building, and bench iteration, use `trm-observability-workflow`.
