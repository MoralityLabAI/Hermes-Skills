# Mixed Contract Compactification Seed

Generated: `2026-04-28T15:06:47.751322+00:00`

This study is the first dry run of the MeTTa agent navigation guide.

- Route: `paper_main_claim_extension`
- Project: `mixed_contract_compactification`
- Evidence class: `no_model_validator_smoke`
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

## Next Step

Replace deterministic candidate outputs with local 3B completions for the same row IDs and score with the same validator script. Do not change the validator between model arms.
