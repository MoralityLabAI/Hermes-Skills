# Skill Research Brief

## Metadata

- Skill name: intellect3-logic-hermes
- Track: task-skill
- Family: intellect3
- Base contract version: Hermes/Intellect-3-Logic-v1
- TRM infusion type: public-trace
- Related overlay or workflow: trm-public-rationale-chain; trm-observability-workflow
- Benchmark or environment family: Campsite / Intellect-3 Logic
- Owner: Hermes Skills research
- Date: 2026-04-22

## Research Question

Does a bounded public rationale improve held Campsite exactness or repairability without violating the final-grid contract?

## Hypothesis

A three-line public trace can improve self-checking on harder logic rows, but only if the trace stays short, task-linked, and separate from the final grid line.

## Base Contract

Preserve the existing logic contract: parse the grid, build a candidate, verify adjacency and counts, and return only the completed Python-style 2D list using `T`, `X`, and `C`.

## TRM Intervention

Add `trm-public-rationale-chain` in tagged format for rationale-allowed evaluations only. The visible trace should be limited to `TRM_PARSE`, `TRM_CRITIC`, and `TRM_COMPRESS`, followed by the final grid.

## Evidence Plan

- teacher trace source: current logic receipt summaries plus future rationale-allowed collector runs routed through `trm-observability-workflow`
- row builder or data path: receipt review from `logic_hybrid_200.summary.json` and `logic_router_200.summary.json`; held-run capture through the observability harness
- benchmark slice: held Intellect-3 logic rows with exact row and column signatures and explicit rationale permission
- primary metric: exact final-grid accuracy
- secondary metrics: contract-break rate, public-trace length compliance, signature-gated win rate, token cost per solved row
- failure gates: lower exact accuracy than plain skill baseline; malformed final grid; visible trace emitted on non-rationale-allowed slices

## Promotion Rule

State the exact condition for:

- promote: the public-trace path beats or matches baseline exact accuracy on the held rationale-allowed slice while keeping contract-break rate at zero
- hold: results are mixed, the held slice is too small, or the trace helps only on a narrow signature class
- reject: exact accuracy drops, formatting breaks rise, or the visible trace weakens the strict final-grid contract

## Notes

Keep signature gating strict. This study is about visible bounded trace quality, not about widening route eligibility.
