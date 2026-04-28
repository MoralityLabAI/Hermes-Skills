# Hermes BlueBeam Research Loop

This skill is the local operator layer for the BlueBeam-Research workflow.

## Source Of Truth

- `basharena_latent_control_repo/basharena_latent_control_repo/analysis/snacksack_autoresearch/`
- `basharena_latent_control_repo/basharena_latent_control_repo/analysis/snacksack_experiment_bundle/`
- `handoff.md`
- `autoresearch.md`
- `trajectory_seed_sweep_plan.md`

## Current Resume Command

Run from `basharena_latent_control_repo/basharena_latent_control_repo`:

```powershell
python -B scripts/run_snacksack_autoresearch_loop.py --max-jobs 20 --target-hours 12 --resume
```

For the focused next batch:

```powershell
python -B scripts/run_snacksack_autoresearch_loop.py --profile trajectory_seed_sweep --max-jobs 16 --target-hours 12
```

## Status Checks

Use the helper script in `scripts/` or inspect:

- `launch_*.out.log`
- `launch_*.err.log`
- `autoresearch_report.json`
- `autoresearch_ranked_jobs.csv`
- `autoresearch_time_budget.json`

## Operating Pattern

1. Check whether the loop is still running.
2. If it is, continue from the current artifact set and avoid duplicate launches.
3. If it is not, resume from the latest completed artifact set.
4. Prefer local, reproducible experiments over fresh corpus generation.
5. Keep every handoff grounded in concrete file paths.

## Batch Design Guidance

- Use orchestration as the reference lane for corruption-gap strength.
- Use manipulation as the coverage-expansion lane.
- Favor shared procedures with consistent layer drift across both lanes.
- The correct acts root is `basharena_latent_control_repo/basharena_latent_control_repo/data/imports/snacksack_corpus_overnight/acts`.
- The discovered layer set in the current corpus is `-4`, `-8`, `-12`, `-16`.
- The focused next batch is `multi_step_risk_escalation` and `unauthorized_config_edit` across layers `-16` and `-12` with seeds `13` and `47`.
- Do not scale job count until the batch produces nonzero feature/layer rows.
- Keep the next batch paired by procedure family, not just by mode.
