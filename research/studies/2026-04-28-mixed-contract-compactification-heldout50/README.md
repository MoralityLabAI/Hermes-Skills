# Mixed Contract Compactification Heldout50

Generated: `2026-04-28T17:01:15.377680+00:00`

- Route: `paper_main_claim_extension`
- Project: `mixed_contract_compactification`
- Evidence classes: `no_model_validator_smoke`, `live_model_local_3b`
- Source guide: `research/generated/metta_agent_navigation.md`
- Source seed study: `research/studies/2026-04-28-mixed-contract-compactification-seed`

## Purpose

This is the first held-out suite after the 12-row seed smoke. It broadens the same exact validator family to 50 rows across mixed observable contracts.

## Family Counts

| Family | Rows |
| --- | ---: |
| `ascii_tree` | 8 |
| `boolq_choice_contract` | 3 |
| `choice_contract` | 2 |
| `if_summarize_judge` | 10 |
| `ifeval_contract_family` | 14 |
| `pydantic_adherence` | 10 |
| `structured_contract` | 3 |

## Artifacts

- Rows: `rows/mixed_contract_heldout50_rows.jsonl`
- Validator: `validators/validate_mixed_contracts.py`
- Suite config: `configs/heldout50_suite.json`
- Canonical smoke: `results/canonical_validator_smoke/canonical_validator_smoke.results.md`
- Local 3B run: `results/local_qwen25_3b_mixed_contract_heldout50/local_qwen25_3b_mixed_contract.results.md`
- Job-cap receipt: `results/local_qwen25_3b_mixed_contract_heldout50/jobcap.summary.json`

## Local 3B Result

The full 50-row held-out run completed under the Windows job-cap wrapper with a 3,000 MB RAM cap, 50% CPU cap, 50 MB/s IO cap, and 7,200 second timeout. Runner-level child RSS peaked at `2359.30 MB`; the job-cap wrapper reported `success`.

| Arm | Exact | Exact Rate | Contract Valid | Semantic Valid |
| --- | ---: | ---: | ---: | ---: |
| `baseline` | 23/50 | 0.4600 | 24/50 | 30/50 |
| `pure_trm` | 27/50 | 0.5400 | 30/50 | 36/50 |
| `metta_runtime` | 32/50 | 0.6400 | 35/50 | 39/50 |
| `metta_runtime_repair` | 37/50 | 0.7400 | 39/50 | 42/50 |

This supports a held-out prompt/repair-gate methodology claim: MeTTa-scaffolded runtime framing plus public-validator repair improves local 3B exact mixed-contract success on this suite. It does not establish learned TRM lift.
