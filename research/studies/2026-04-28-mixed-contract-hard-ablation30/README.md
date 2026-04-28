# Mixed Contract Hard Ablation30

Generated: `2026-04-28T17:27:39.730877+00:00`

- Route: `paper_main_claim_extension`
- Project: `mixed_contract_hard_ablation`
- Evidence classes: `no_model_validator_smoke`, `live_model_local_3b`
- Source heldout study: `research/studies/2026-04-28-mixed-contract-compactification-heldout50`

## Purpose

This suite probes whether the heldout50 lift survives on harder rows and whether public-validator feedback adds value beyond a blind second repair pass.

## Family Counts

| Family | Rows |
| --- | ---: |
| `computed_json_schema` | 6 |
| `deep_ascii_tree` | 4 |
| `logic_label_contract` | 7 |
| `math_numeric_contract` | 8 |
| `state_sequence_array` | 5 |

## Artifacts

- Rows: `rows/mixed_contract_hard_ablation30_rows.jsonl`
- Validator: `validators/validate_mixed_contracts.py`
- Suite config: `configs/hard_ablation30_suite.json`
- Canonical smoke: `results/canonical_validator_smoke/canonical_validator_smoke.results.md`
- Local 3B run: `results/local_qwen25_3b_mixed_contract_hard_ablation30/local_qwen25_3b_mixed_contract.results.md`
- Job-cap receipt: `results/local_qwen25_3b_mixed_contract_hard_ablation30/jobcap.summary.json`

## Local 3B Result

The full hard-ablation run completed under the Windows job-cap wrapper with a 3,000 MB RAM cap, 50% CPU cap, 50 MB/s IO cap, and 7,200 second timeout. Runner-level child RSS peaked at `2370.91 MB`; the job-cap wrapper reported `success`.

| Arm | Exact | Exact Rate | Contract Valid | Semantic Valid |
| --- | ---: | ---: | ---: | ---: |
| `baseline` | 12/30 | 0.4000 | 20/30 | 15/30 |
| `pure_trm` | 11/30 | 0.3667 | 21/30 | 14/30 |
| `metta_runtime` | 9/30 | 0.3000 | 20/30 | 12/30 |
| `metta_runtime_blind_repair` | 12/30 | 0.4000 | 20/30 | 15/30 |
| `metta_runtime_repair` | 13/30 | 0.4333 | 20/30 | 16/30 |

## Repair Opportunity Result

Rows where `metta_runtime` failed exactly: `21`.

| Repair arm | Opportunity Rows | Exact Repairs | Exact Rate |
| --- | ---: | ---: | ---: |
| `metta_runtime_blind_repair` | 21 | 3 | 0.1429 |
| `metta_runtime_repair` | 21 | 4 | 0.1905 |

## Family Breakdown

| Family | Baseline | Pure TRM | MeTTa Runtime | Blind Repair | Feedback Repair |
| --- | ---: | ---: | ---: | ---: | ---: |
| `computed_json_schema` | 3/6 | 5/6 | 5/6 | 5/6 | 5/6 |
| `deep_ascii_tree` | 0/4 | 0/4 | 1/4 | 1/4 | 1/4 |
| `logic_label_contract` | 4/7 | 5/7 | 3/7 | 5/7 | 5/7 |
| `math_numeric_contract` | 4/8 | 1/8 | 0/8 | 1/8 | 2/8 |
| `state_sequence_array` | 1/5 | 0/5 | 0/5 | 0/5 | 0/5 |
