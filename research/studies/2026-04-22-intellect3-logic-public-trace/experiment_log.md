# Experiment Log

## Run Metadata

- Study: Intellect3 logic public-trace ablation
- Run id: setup-2026-04-22
- Date: 2026-04-22
- Skill: intellect3-logic-hermes
- TRM layer: trm-public-rationale-chain
- Model or teacher: pending held-slice run
- Environment family: Campsite / Intellect-3 Logic
- Script or command: planning packet only; first commands are listed in this folder's `README.md`

## Inputs

- input artifact paths: `intellect3-logic-hermes/references/logic_hybrid_200.summary.json`, `intellect3-logic-hermes/references/logic_router_200.summary.json`, `trm-public-rationale-chain/references/public_trace_contract.md`
- config path: `trm-public-rationale-chain/scripts/build_skill_prompt.py --task-family logic --trace-format tagged --max-step-chars 96`
- prompt or contract version: Hermes/Intellect-3-Logic-v1 + TRM-Public-Rationale-Chain-v1

## Outputs

- output artifact paths: `research/studies/2026-04-22-intellect3-logic-public-trace/artifacts/`
- summary path: `research/studies/2026-04-22-intellect3-logic-public-trace/artifacts/logic_public_trace_eval_notes.md`
- ledger or receipts path: `research/studies/2026-04-22-intellect3-logic-public-trace/artifacts/logic_public_trace_ledger.jsonl`

## Result

- primary metric: pending initial held-slice run
- comparison baseline: plain `intellect3-logic-hermes` skill path
- pass or fail: not run yet

## Failure Mode

No benchmark executed yet. Main anticipated failure is trace leakage that harms exact final-grid formatting.

## Decision

- rerun

## Next Action

Collect a rationale-allowed held logic slice and compare plain vs public-trace prompts under the exact same signature-gated conditions.
