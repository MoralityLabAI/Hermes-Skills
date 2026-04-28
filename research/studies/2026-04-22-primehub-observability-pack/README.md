# Primehub Observability Pack Study

## Goal

Build the shared TRM observability packet needed before promoting extra overlays across the current Primehub Hermes skills.

## Included Skills

- [primehub-abstain-guard-hermes](C:/projects/Hermes-Skills/Hermes Skills/primehub-abstain-guard-hermes/SKILL.md)
- [primehub-choice-contract-hermes](C:/projects/Hermes-Skills/Hermes Skills/primehub-choice-contract-hermes/SKILL.md)
- [primehub-hard-reasoning-logic-hermes](C:/projects/Hermes-Skills/Hermes Skills/primehub-hard-reasoning-logic-hermes/SKILL.md)
- [primehub-hard-reasoning-numeric-hermes](C:/projects/Hermes-Skills/Hermes Skills/primehub-hard-reasoning-numeric-hermes/SKILL.md)
- [primehub-internal-action-hermes](C:/projects/Hermes-Skills/Hermes Skills/primehub-internal-action-hermes/SKILL.md)

## Workflow Surface

- [trm-observability-workflow](C:/projects/Hermes-Skills/Hermes Skills/trm-observability-workflow/SKILL.md)
- [run_primehub_trm_rollup.py](C:/projects/Hermes-Skills/Hermes Skills/scripts/run_primehub_trm_rollup.py)
- [build_primehub_skill_trm_matrix.py](C:/projects/Hermes-Skills/Hermes Skills/scripts/build_primehub_skill_trm_matrix.py)
- [primehub_trm_autoresearch_loop.py](C:/projects/Hermes-Skills/Hermes Skills/scripts/primehub_trm_autoresearch_loop.py)

## Current Benchmark Roots

- `data/primehub_eligible_benchmark_v1`
- `data/primehub_eligible_benchmark_v1_retry_27b_tail`
- `data/primehub_eligible_benchmark_v2_47env`

## Planned Commands

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\trm-observability-workflow\scripts\show_workflow.py"
python "C:\projects\Hermes-Skills\Hermes Skills\scripts\run_primehub_trm_rollup.py" --run-root "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v1" --run-root "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v1_retry_27b_tail" --run-root "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v2_47env" --work-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-observability-pack\artifacts\rollup"
python "C:\projects\Hermes-Skills\Hermes Skills\scripts\build_primehub_skill_trm_matrix.py" --cluster abstain_guard --cluster choice_contract --cluster hard_reasoning_logic --cluster hard_reasoning_numeric --cluster internal_action --out "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-observability-pack\artifacts\matrix"
python "C:\projects\Hermes-Skills\Hermes Skills\scripts\primehub_trm_autoresearch_loop.py" --cycles 1 --work-base "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-observability-pack\artifacts\autoresearch" --summary "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-observability-pack\artifacts\autoresearch\latest.summary.json" --ledger "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-observability-pack\artifacts\autoresearch\ledger.jsonl"
```

## Artifact Contract

Store new outputs under:

- `research/studies/2026-04-22-primehub-observability-pack/artifacts/`
- expected first artifacts:
  - `rollup/primehub_trm_rollup.manifest.json`
  - `matrix/manifest.json`
  - `matrix/role_based_imprint.md`
  - `autoresearch/latest.summary.json`

## Decision Boundary

Do not stack new overlays on Primehub families until this packet shows stable exact-positive coverage, usable target-action coverage, and reproducible bench summaries by cluster.
