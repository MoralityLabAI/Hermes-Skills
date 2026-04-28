# Experiment Log

## Run Metadata

- Study: Primehub observability pack
- Run id: setup-2026-04-22
- Date: 2026-04-22
- Skill: primehub family pack
- TRM layer: observability
- Model or teacher: current replay roots with `qwen35_9b` and `qwen35_27b` defaults from the autoresearch loop
- Environment family: Primehub clusters `abstain_guard`, `choice_contract`, `hard_reasoning_logic`, `hard_reasoning_numeric`, `internal_action`
- Script or command: planning packet only; first commands are listed in this folder's `README.md`

## Inputs

- input artifact paths: `data/primehub_eligible_benchmark_v1`, `data/primehub_eligible_benchmark_v1_retry_27b_tail`, `data/primehub_eligible_benchmark_v2_47env`, `data/primehub_skill_batch_evolution/latest.manifest.json`
- config path: `scripts/run_primehub_trm_rollup.py` and `scripts/build_primehub_skill_trm_matrix.py`
- prompt or contract version: current `primehub-*` skill contracts plus the latest cluster manifest

## Outputs

- output artifact paths: `research/studies/2026-04-22-primehub-observability-pack/artifacts/`
- summary path: `research/studies/2026-04-22-primehub-observability-pack/artifacts/rollup/primehub_trm_rollup.manifest.json`
- ledger or receipts path: `research/studies/2026-04-22-primehub-observability-pack/artifacts/autoresearch/ledger.jsonl`

## Result

- primary metric: pending initial rollup
- comparison baseline: current unstructured review of Primehub receipts and sidecars
- pass or fail: not run yet

## Failure Mode

No benchmark executed yet. Main anticipated failure is that some clusters remain too sparse to support a trustworthy matrix or role-based imprint.

## Decision

- rerun

## Next Action

Run the shared rollup into this study folder, then build the per-cluster matrix and compare cluster health before adding any new overlay experiments.
