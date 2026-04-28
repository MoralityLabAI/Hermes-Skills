# Mixed Contract Compactification Seed

Generated: `2026-04-28T16:17:42.680802+00:00`

This study is the first dry run of the MeTTa agent navigation guide.

- Route: `paper_main_claim_extension`
- Project: `mixed_contract_compactification`
- Evidence classes: `no_model_validator_smoke`, `live_model_local_3b`
- Source guide: `research/generated/metta_agent_navigation.md`
- Source menu: `research/generated/metta_project_menu.md`

## Purpose

Create the first artifact required by the agent guide: frozen rows, exact validators, configs, result files, and a claim audit. This is deliberately no-model so future model runs can reuse the same row IDs and validators.

## Artifacts

- Rows: `rows/mixed_contract_seed_rows.jsonl`
- Arms config: `configs/seed_arms.json`
- Validator: `validators/validate_mixed_contracts.py`
- Candidate outputs: `results/seed_candidates.jsonl`
- Smoke results: `results/validator_smoke.results.json`
- Smoke summary: `results/validator_smoke.results.md`
- Claim audit: `claim_audit.md`
- Local 3B seed run: `results/local_qwen25_3b_mixed_contract_seed12/local_qwen25_3b_mixed_contract.results.md`
- Local 3B job cap: `results/local_qwen25_3b_mixed_contract_seed12/jobcap.summary.json`

## Local 3B Seed Run

The first full-seed local Qwen2.5-3B Q4 run used all 12 rows from this seed suite. It ran under a Windows job cap with `3000 MB` per-process memory, `50%` CPU, `50 MB/s` IO, and a runner-level `2600 MB` child RSS cutoff. The runner reported peak child RSS `2371.06 MB`.

| Arm | Exact success | Exact rate | Read |
| --- | ---: | ---: | --- |
| `baseline` | 5/12 | 0.4167 | Plain prompting solves easy label, delimiter, and some schema cases. |
| `pure_trm` | 6/12 | 0.5000 | Typed prompting improves some contracts but still copies schema/header artifacts. |
| `metta_runtime` | 6/12 | 0.5000 | Prompt-only MeTTa matches pure TRM on exact rate, with different failure shape. |
| `metta_runtime_repair` | 8/12 | 0.6667 | Repair-prompt gating gives the current seed lift; this is not trained TRM lift. |

## Next Step

Expand this to the planned 50-row held-out mixed-contract suite. Keep the same validator script and continue separating live model, deterministic repair, and trained TRM evidence.
