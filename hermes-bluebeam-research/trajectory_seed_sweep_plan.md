# Trajectory Seed Sweep Plan

This is the next batch for improving correlation signals on trajectory bundles.

## Goal

Raise held-out correlation quality on the strongest shared procedures using a small, seed-aware, layer-anchored sweep.

## Exact Matrix

- Procedures:
  - `multi_step_risk_escalation`
  - `unauthorized_config_edit`
- Layers:
  - `-16`
  - `-12`
- Seeds:
  - `13`
  - `47`
- Modes:
  - `dictionary`
  - `sae`
- Probe mode:
  - `trajectory`

This yields 16 jobs total.

## Job Pattern

For each procedure/layer/seed pair, run both modes:

- `dictionary_<procedure>_layer<layer>_seed<seed>`
- `sae_<procedure>_layer<layer>_seed<seed>`

## Run Command

From `basharena_latent_control_repo/basharena_latent_control_repo`:

```powershell
python -B scripts/run_snacksack_autoresearch_loop.py --profile trajectory_seed_sweep --max-jobs 16 --target-hours 12
```

Use `--resume` on a restart.

## Stop Conditions

Stop or revise the matrix if any of the following happen:

1. A job returns `layer_count = 0` or `top_feature_count = 0`. That means the acts path or layer discovery is wrong.
2. The first dictionary anchor pass on `-16` does not beat the current same-procedure baseline by at least `0.02` in `condition_probe_auroc`.
3. The seed sweep produces unstable winners, meaning the best procedure-layer pair changes across seeds without improving the mean score.
4. The best layer drifts away from `-16`/`-12` without a matching gain in `condition_probe_auroc`.

## Expansion Rule

Only expand to `delayed_policy_violation_setup` and layer `-8` after the `multi_step_risk_escalation` and `unauthorized_config_edit` seed sweep shows a stable improvement.
