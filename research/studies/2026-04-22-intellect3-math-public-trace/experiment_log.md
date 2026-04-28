# Experiment Log

## Run Metadata

- Study: Intellect3 math public-trace ablation
- Run id: setup-2026-04-22
- Date: 2026-04-22
- Skill: intellect3-math-hermes
- TRM layer: trm-public-rationale-chain
- Model or teacher: pending held-slice run
- Environment family: Intellect-3 Math
- Script or command: planning packet only; first commands are listed in this folder's `README.md`

## Inputs

- input artifact paths: `intellect3-math-hermes/references/math_hybrid_200.summary.json`, `intellect3-math-hermes/references/math_router_100.summary.json`, `trm-public-rationale-chain/references/public_trace_contract.md`
- config path: `trm-public-rationale-chain/scripts/build_skill_prompt.py --task-family math --trace-format tagged --max-step-chars 96`
- prompt or contract version: Hermes/Intellect-3-Math-v1 + TRM-Public-Rationale-Chain-v1

## Outputs

- output artifact paths: `research/studies/2026-04-22-intellect3-math-public-trace/artifacts/`
- summary path: `research/studies/2026-04-22-intellect3-math-public-trace/artifacts/math_public_trace_eval_notes.md`
- ledger or receipts path: `research/studies/2026-04-22-intellect3-math-public-trace/artifacts/math_public_trace_ledger.jsonl`

## Result

- primary metric: pending initial held-slice run
- comparison baseline: plain `intellect3-math-hermes` skill path
- pass or fail: not run yet

## Failure Mode

No benchmark executed yet. Main anticipated failure is that visible trace adds format noise without overcoming the current weak aggregate TRM signal.

## Decision

- rerun

## Next Action

Build a rationale-allowed held math slice and compare plain vs public-trace prompts under the exact same answer-format contract.
