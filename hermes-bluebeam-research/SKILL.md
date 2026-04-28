---
name: hermes-bluebeam-research
description: "Continue the local BlueBeam-Research loop: inspect SAE/autoresearch artifacts, resume budgeted runs, and package handoff state when plan budget is tight."
---

# Hermes Bluebeam Research

## Overview

Use this skill to continue the local BlueBeam-Research loop when context or plan budget is low. It is for checking current SAE/autoresearch state, resuming budgeted runs, and preserving a clean handoff for the next agent.

## Workflow

1. Check current state with `scripts/bluebeam_research_status.py`.
2. Prefer existing artifacts over rerunning corpora or rebuilding completed jobs.
3. If the loop is already running, report the current job and do not launch a duplicate.
4. If the loop stalled or finished, relaunch from the repo root with:

```powershell
python -B scripts/run_snacksack_autoresearch_loop.py --max-jobs 20 --target-hours 12 --resume
```

5. After a run completes, summarize the latest `autoresearch_report.json`, `autoresearch_ranked_jobs.csv`, and any updated bundle outputs.
6. Validate that the batch produced nonzero `layer_count` and `top_feature_count` in the job receipts before treating it as a modeling result.
7. If the researcher needs to hand off again, update the repo-level `handoff.md` with concrete artifact paths and the next resume command.
8. For correlation-improvement work, prefer the focused trajectory seed sweep:

```powershell
python -B scripts/run_snacksack_autoresearch_loop.py --profile trajectory_seed_sweep --max-jobs 16 --target-hours 12
```

## Methodology Notes

- The current comparison signal is stronger in the orchestration lane than the manipulation lane. Use that lane as the reference when judging whether a new batch actually improved tamper indicators.
- Manipulation has broader token-SAE coverage, but the layer alignment is less stable. Treat it as a candidate lane for coverage expansion, not as the primary success metric.
- Shared-procedure drift matters more than raw procedure count. Prioritize procedures that appear in both lanes and show the largest corruption-gap or layer-delta separation.
- The current feature path must point at `data/imports/snacksack_corpus_overnight/acts`, not `.../acts/corpus_overnight`. The trainer expects `train/` and `dev/` directly underneath the acts root.
- The current corpus exposes layers `-4`, `-8`, `-12`, and `-16`. Discover layers from disk and build the SAE sweep from what exists instead of hardcoding `-18/-22`.
- The focused next batch is `multi_step_risk_escalation` and `unauthorized_config_edit` across layers `-16` and `-12` with seeds `13` and `47`.
- A run that finishes with zero feature rows or zero layer rows is a pipeline-validity failure, not a successful experiment. Fix the acts root before expanding the matrix.
- The next batch should optimize for paired comparisons, stable layer coverage, and reproducible seed control rather than just more jobs.

## What To Inspect

- `basharena_latent_control_repo/basharena_latent_control_repo/analysis/snacksack_autoresearch/autoresearch_report.json`
- `basharena_latent_control_repo/basharena_latent_control_repo/analysis/snacksack_autoresearch/autoresearch_jobs.csv`
- `basharena_latent_control_repo/basharena_latent_control_repo/analysis/snacksack_autoresearch/autoresearch_ranked_jobs.csv`
- `basharena_latent_control_repo/basharena_latent_control_repo/analysis/snacksack_autoresearch/autoresearch_time_budget.json`
- `basharena_latent_control_repo/basharena_latent_control_repo/analysis/snacksack_autoresearch/launch_*.out.log`
- `basharena_latent_control_repo/basharena_latent_control_repo/analysis/snacksack_autoresearch/launch_*.err.log`
- `basharena_latent_control_repo/basharena_latent_control_repo/analysis/snacksack_experiment_bundle/*`
- `handoff.md`
- `autoresearch.md`

## Rules

- Stay benchmark-safe and local-only.
- Do not add real-world offensive persistence, exfiltration, privilege escalation, or covert compromise content.
- Keep runs reproducible and resume-friendly.
- Leave concrete artifact paths in every status note or handoff.
- Prefer paired lane comparison and output validation over raw job count.
- When output counts are zero, debug the pipeline before interpreting scores.
- Verify the acts root and discovered layer set with real shard paths before starting a long batch.
- Use the focused seed sweep first; only expand to `-8` and `delayed_policy_violation_setup` if the initial matrix improves.

## Resources

- `scripts/bluebeam_research_status.py` prints a compact live-state summary for the loop.
- `references/research_loop.md` captures the current operating contract and resume path.
