# Skill Research Brief

## Metadata

- Skill name: primehub family pack
- Track: task-skill
- Family: primehub
- Base contract version: current `primehub-*` Hermes skill set
- TRM infusion type: observability
- Related overlay or workflow: trm-observability-workflow; run_primehub_trm_rollup.py; build_primehub_skill_trm_matrix.py; primehub_trm_autoresearch_loop.py
- Benchmark or environment family: Primehub clusters `abstain_guard`, `choice_contract`, `hard_reasoning_logic`, `hard_reasoning_numeric`, `internal_action`
- Owner: Hermes Skills research
- Date: 2026-04-22

## Research Question

Can the current Primehub family produce a stable shared observability packet that supports cluster-specific training, benchmarking, and skill imprinting before extra overlays are added?

## Hypothesis

Receipts-first rollups and cluster-specific matrices should produce stronger supervision than generic pooled rows, especially for choice contract, hard reasoning, and internal action clusters.

## Base Contract

Preserve each Primehub skill's exact answer contract. This study is not about visible rationale or retrieval overlays yet; it is about row quality, benchmark coverage, and cluster-specific promotion evidence.

## TRM Intervention

Use `trm-observability-workflow` and the root Primehub rollup scripts to stage replays, merge families, train cluster-specific components, and emit role-based imprints from real benchmark receipts.

## Evidence Plan

- teacher trace source: existing replay roots under `data/primehub_eligible_benchmark_v1`, `data/primehub_eligible_benchmark_v1_retry_27b_tail`, and `data/primehub_eligible_benchmark_v2_47env`
- row builder or data path: `scripts/run_primehub_trm_rollup.py`, `scripts/build_primehub_skill_trm_matrix.py`, `scripts/primehub_trm_autoresearch_loop.py`
- benchmark slice: Primehub clusters `abstain_guard`, `choice_contract`, `hard_reasoning_logic`, `hard_reasoning_numeric`, and `internal_action`
- primary metric: exact-positive rows and target-action coverage by cluster
- secondary metrics: critic bench accuracy, retriever exact-match rate, router abstain quality, replay coverage by model family
- failure gates: sparse clusters that do not clear the family floor; unstable rollups that change materially without new evidence; imprint lines unsupported by the bench summaries

## Promotion Rule

State the exact condition for:

- promote: the rollup and matrix produce stable, reproducible per-cluster summaries with adequate exact-positive and target-action coverage
- hold: some clusters are healthy but others remain sparse or noisy
- reject: the merged corpus remains too weak for promotion or the cluster split does not improve training and benchmark quality

## Notes

`structured_map` is tracked in a separate retrieval study. `core_reasoning` exists in the manifest but is not yet treated as its own packaged skill study here.
