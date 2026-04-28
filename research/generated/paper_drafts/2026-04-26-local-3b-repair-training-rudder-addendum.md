# Addendum: Local 3B Repair-Training Rudder Benchmark

Status: draft addendum  
Date: April 26, 2026

## Thesis

The near-miss repair curriculum should be benchmarked before training new TRM weights by asking whether a small local model can act as the control-plane rudder over the generated repair rows. This tests the compactification claim directly: can a `3B` model choose repair/commit/veto actions when the MeTTa/TRM scaffold exposes state, failure labels, and retrieved near-miss examples?

The full local result is [local_3b_repair_training_rudder.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_3b_repair_training_rudder_benchmark\local_3b_repair_training_rudder.results.md>).

## Setup

Model: `Qwen2.5-3B-Instruct-Q4_K_M` via llama.cpp CUDA.  
Eval rows: all `88` non-train Pure-TRM rows from the near-miss split: `34` `val_seen`, `36` `holdout_seen`, and `18` `holdout_unseen_family`.  
Arms:

- `raw_3b_rudder`: state-only prompt, no retrieved training examples.
- `repair_training_rudder`: same state plus `4` retrieved train examples from the current near-miss curriculum.

The prompt does not expose the target repair gate or target bucket in eval state.

## Result

| Arm | Rows | Target-action acc | Repair-action acc | Joint acc | JSON parse |
| --- | ---: | ---: | ---: | ---: | ---: |
| `raw_3b_rudder` | `88` | `0.7159` | `0.4091` | `0.3636` | `1.0000` |
| `repair_training_rudder` | `88` | `0.7955` | `0.3409` | `0.3182` | `1.0000` |

The repair-training context improves commit/veto selection by `+0.0796`, with the biggest transfer gain on `holdout_unseen_family` target-action accuracy: `0.5000 -> 0.8889`.

The same context does not improve repair-action selection. Repair-action accuracy falls from `0.4091` to `0.3409`, and joint accuracy falls from `0.3636` to `0.3182`.

## Interpretation

This is good evidence for a two-stage architecture:

- use MeTTa and deterministic skill metadata to narrow the valid repair-action space by env family;
- use the small LLM or a trained commit/veto TRM as a rudder for `commit` versus `reject_or_abstain`;
- use an actual repair/verifier TRM, not prompt-only 3B retrieval, to choose the final repair action in ambiguous or unseen families.

The current 3B over-commits no-gain repairs. On `repair_failure_or_no_gain`, target-action accuracy is `0.0000` raw and only `0.1818` with repair-training retrieval. On `signature_pass_cell_fail`, both arms remain `0.0000` for target-action and repair-action accuracy. This is the main next training target.

## Claim Boundary

This benchmark is a local pre-training control-plane eval. It does not show that repair TRM weights have improved. It shows where the generated repair curriculum is immediately usable as prompt-level control context and where it must be converted into trained verifier/repair/commit TRMs.

