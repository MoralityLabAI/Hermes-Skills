# C-Signature Commit TRM Training Plan

Status: ready target, not launched

## Purpose

Train a post-repair commit/veto TRM for Intellect-3 C-signature repairs. The target is not repair-action selection. MeTTa already narrows the repair action; the TRM learns whether to commit a repaired candidate after verifier state is available.

## Training Task

- `training_task_id`: `c_signature_commit_trm_v1`
- Train rows: `research/generated/c_signature_commit_trm_pack/c_signature_commit_trm_rows.jsonl`
- Validation split: `val_seen`
- Holdout split: `holdout_seen`
- Primary metric: `false_commit_rate`
- Secondary metrics: `false_reject_rate`, `accuracy`, `expected_delta_if_committed`
- Target policy ceiling: `postrepair_exact_or_gain_gt_0`

## Required Signals

The learner should consume post-repair verifier state:

- `after_exact`
- `reward_delta`
- `after_reward`
- `before_reward`
- `after_t_signature_pass`
- `after_c_signature_pass`
- `repair_action`
- `edit_distance`

The target action is:

```scheme
(= (c-signature-commit-action $state)
   (if (or (after-exact $state) (> (reward-delta $state) 0.0))
       commit
       reject_or_abstain))
```

## Resource Caps

Use the default HRM/TRM safe training caps unless the user explicitly approves larger limits:

- RAM: `2048 MB` hard cap
- CPU: `50%` hard cap
- IO: `50 MB/s` monitored abort cap
- Checkpoint interval: every `100` steps or `60` seconds, whichever comes first
- Chunk strategy: split by `base_case_key`; never mix policy variants from the same base case across chunks

## Wrapper

Use `research/scripts/run_c_signature_commit_trm_jobcap.ps1` to launch the trainer under a Windows Job Object. Abort on cap breach is a valid outcome and should be reported as training data, not hidden.

Example:

```powershell
powershell -ExecutionPolicy Bypass -File research\scripts\run_c_signature_commit_trm_jobcap.ps1 `
  -RunId c_signature_commit_trm_v1 `
  -TrainerScript C:\projects\Pure-TRM-Trainer\train.py `
  -TrainerArgs "--rows research/generated/c_signature_commit_trm_pack/c_signature_commit_trm_rows.jsonl --task commit_veto --checkpoint-interval-steps 100"
```

## Log Schema

Event log: `jobcap.events.jsonl`

```json
{"ts":"2026-04-28T00:00:00Z","event":"start","run_id":"c_signature_commit_trm_v1","caps":{"ram_mb":2048,"cpu_pct":50,"io_mb_s":50}}
{"ts":"2026-04-28T00:01:00Z","event":"checkpoint_due","elapsed_sec":60}
{"ts":"2026-04-28T00:01:03Z","event":"abort","reason":"io_cap_exceeded","peak_ram_mb":1530,"peak_io_mb_s":64.2,"steps_completed":0}
```

Summary: `jobcap.summary.json`

```json
{"run_id":"c_signature_commit_trm_v1","status":"completed_or_aborted","abort_reason":null,"peak_ram_mb":0,"avg_ram_mb":0,"peak_io_mb_s":0,"cpu_pct":0,"steps_completed":0,"checkpoints":[]}
```

## Claim Boundary

The current post-repair verifier sweep is an evaluator-backed ceiling and training-target definition. The paper can claim trained TRM performance only after a capped trainer run learns this decision from train rows and holds it on `val_seen` and `holdout_seen`.
