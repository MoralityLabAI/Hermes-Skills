# Skill Research Brief

## Metadata

- Skill name: intellect3-math-hermes
- Track: task-skill
- Family: intellect3
- Base contract version: Hermes/Intellect-3-Math-v1
- TRM infusion type: public-trace
- Related overlay or workflow: trm-public-rationale-chain; trm-observability-workflow
- Benchmark or environment family: Intellect-3 Math
- Owner: Hermes Skills research
- Date: 2026-04-22

## Research Question

Can a bounded public rationale improve held arithmetic accuracy or calibration on rationale-allowed slices without hurting the strict final integer answer format?

## Hypothesis

The public trace may help on multi-step arithmetic rows where a short visible critic line catches a mistake, but the benefit is likely narrow because the current packaged receipts do not yet show a net aggregate TRM win.

## Base Contract

Preserve the existing math contract: parse the givens, solve with a short candidate path, verify arithmetic consistency, and return only the final integer answer string.

## TRM Intervention

Add `trm-public-rationale-chain` in tagged format for math-only rationale-allowed evaluations. Keep the visible trace to three short lines before the final integer line.

## Evidence Plan

- teacher trace source: current math receipt summaries plus future rationale-allowed collector runs through `trm-observability-workflow`
- row builder or data path: review `math_hybrid_200.summary.json` and `math_router_100.summary.json`; capture held evaluation traces through the observability harness
- benchmark slice: held Intellect-3 math rows with explicit rationale permission and a preserved final integer answer contract
- primary metric: exact final-answer accuracy
- secondary metrics: non-integer output rate, visible-trace length compliance, support-pattern precision, token cost per solved row
- failure gates: any aggregate drop against plain baseline; non-integer final answers; public trace emitted where the eval does not permit it

## Promotion Rule

State the exact condition for:

- promote: the public-trace path improves held exact accuracy on rationale-allowed math rows without increasing non-integer or malformed outputs
- hold: gains appear only on a narrow support pattern or the held slice is too small to trust
- reject: overall accuracy drops, support-pattern routing remains weak, or the final integer contract is degraded

## Notes

Keep this study opt-in. Math should remain plain-path by default until a larger held slice shows a stable gain.
