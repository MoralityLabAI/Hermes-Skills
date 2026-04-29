# Data and Experiment Campaign Plan

Status: provisional paper plan  
Date: 2026-04-29

## Purpose

The full paper should wait for matched `3B`, `9B`, and `27B` benches. The current package preserves the local `3B` result as a provisional control-plane finding and specifies the missing runs needed before making a stronger claim about MeTTa-scaffolded TRM infusion.

## Current Evidence

| Evidence block | Status | Paper role |
| --- | --- | --- |
| Near-miss repair curriculum | Complete locally: `244` rows; `156/34/36/18` train/val/seen-holdout/unseen-holdout split | Methods and data curation section |
| Local 3B repair-training rudder | Complete locally: `88` non-train rows, two arms, `176` completions | Provisional scale-floor result |
| Local 3B MeTTa action-space rudder | Complete locally: same `88` non-train rows; `metta_static_gate_rudder` joint `0.9545` | Strongest current skill-circuit result; separates repair-action narrowing from 3B commit/veto |
| C-signature commit TRM pack | Complete locally: `122` rows, `86/16/20` train/val/holdout | Next trained TRM target for false-commit reduction |
| C-signature post-repair verifier sweep | Complete locally with no model calls: `postrepair_exact_or_gain_gt_0` gets `1.0000` validation and holdout accuracy with `0.0000` false-commit rate | Defines the evaluator-backed multi-signal target for the commit/veto TRM |
| Multi-env methodology lift matrix | Complete locally with no model calls: `148` rows across `9` env families; `post_multi_signal` target gets `1.0000` separability, while symbolic-only still has false-commit `0.6562` | Generalizes the C-signature result into a reusable env-adapter methodology |
| Mixed-contract heldout50 | Complete locally with Qwen2.5-3B Q4: baseline `23/50`, pure TRM `27/50`, MeTTa runtime `32/50`, feedback repair `37/50`; job cap success | Positive compactification evidence for verifier-visible output contracts |
| Hard mixed-contract ablation30 | Complete locally with Qwen2.5-3B Q4: baseline `12/30`, pure TRM `11/30`, MeTTa runtime `9/30`, blind repair `12/30`, feedback repair `13/30`; job cap success | Boundary evidence showing the lift shrinks on math/state/deeper-logic rows |
| Noisy camp-gate task allocation | Complete locally with Qwen2.5-3B Q4 and no-model graph router: baseline extraction `0/12`, MeTTa schema `6/12`, MeTTa graph `9/12`, script graph router `12/12` | Shows that MeTTa's strongest role is exposing a task graph so subtasks can move to scripts, TRM gates, symbolic solvers, or LLM proposal |
| Intellect-3 logic C-signature replay | Complete post-hoc: `0.3028 -> 0.6789` exact under C-only projection | Motivation for repair/verifier gates |
| Symbolic closure threshold suite | Complete deterministic control-plane eval | Defines compactification threshold |
| 9B repair-training rudder | Pending Snacksack or equivalent GPU | Required before full claim |
| 27B repair-training rudder | Pending Snacksack or equivalent GPU | Required for scale trend |
| Trained repair/verifier TRM | Pending Pure-TRM-Trainer run | Required to move beyond prompt-level rudder |

## Required Model-Scale Bench Matrix

| Model | Raw skill | Raw 3B/9B/27B rudder | Repair-training rudder | Trained repair/verifier TRM | Must report |
| --- | ---: | ---: | ---: | ---: | --- |
| `3B` | done for several small envs; rudder done | done | done | pending | Shows scale floor and over-commit failure mode |
| `9B` | pending matched split | pending | pending | pending | Tests whether mid-scale model fixes repair-action routing |
| `27B` | partial post-hoc receipts exist | pending live matched split | pending live matched split | pending | Tests whether high-scale model plus MeTTa/TRM closes the repair selector gap |

## Primary Metrics

- `target_action_accuracy`: correctness of `commit` versus `reject_or_abstain`.
- `repair_action_accuracy`: correctness of the selected repair action.
- `joint_accuracy`: both target and repair action correct.
- `false_commit_rate`: fraction of no-gain rows committed.
- `repair_regression_rate`: fraction of exact positives or safe positives damaged by repair.
- `unseen_family_transfer`: performance on held-out failure labels.

## Minimal Acceptable Paper Evidence

1. Run the same `88` non-train Pure-TRM rows on `9B` and `27B`.
2. Preserve the current `3B` result as the scale-floor reference.
3. Train at least one repair/verifier TRM on `train.pure_trm.jsonl`, tuning only on `val_seen`.
4. Report `holdout_seen` and `holdout_unseen_family` separately.
5. Include a negative-control lane for `signature_pass_cell_fail` and `hard_reasoning_numeric`.
6. Keep all post-hoc Intellect-3 projection claims separated from live benchmark claims.

## Interpretation Target

The April 28 local result sharpens the desired publishable result. The 3B failed as an unconstrained repair-action selector, but a MeTTa action-space gate plus static commit/veto guards raised joint held-out accuracy from `0.3636` raw and `0.3182` retrieval-only to `0.9545`.

The remaining target is now isolated: train a post-repair C-signature commit/veto TRM on `research/generated/c_signature_commit_trm_pack/c_signature_commit_trm_rows.jsonl` and report false-commit rate on `val_seen` and `holdout_seen`.

A visible-feature policy sweep is now available at `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/c_signature_commit_policy_sweep`. It should be the baseline for the trained verifier/commit TRM: validation-selected kNN rules can look perfect on `val_seen` but fail all holdout no-gain rows, while holdout-safe edit-distance rules are lossy. This makes false-commit rate the decisive metric.

A post-repair verifier sweep is now available at `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/c_signature_postrepair_verifier_sweep`. It shows why the verifier TRM should consume multi-signal post-repair state rather than pre-repair hints: signature completion alone still false-commits no-gain repairs, exact-only validation is too conservative, and `after_exact OR reward_delta > 0` cleanly preserves partial improvements while eliminating false commits on the current train/val/holdout split.

A multi-env methodology matrix is now available at `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/metta_trm_methodology_lift_matrix`. It should be the bridge from "C-signature success" to paper methodology: the same before/after verifier-state schema covers tool routing, choice contracts, ASCII trees, camp-gate logic, schema JSON, literal-count IFEval, safety routing, and math as a negative control. The matrix separates score lift from target separability so math does not get overclaimed.

The April 28 mixed-contract compactification results should be used as the environment-dependent bridge. `mixed_contract_heldout50` gives the positive local result: feedback repair improves exact success from `23/50` to `37/50`. `mixed_contract_hard_ablation30` gives the boundary result: feedback repair improves only from `12/30` to `13/30`, while blind repair already reaches `12/30`. The paper-safe wording is that MeTTa/TRM scaffolding helps most when observable contracts expose the failure state; it does not replace missing arithmetic, state-transition, or candidate-generation capability.

The April 29 noisy camp-gate result should be used as the task-allocation bridge. It shows a ladder from prompt extraction to graph extraction to script-owned graph routing: `0/12 -> 6/12 -> 9/12 -> 12/12`. The paper-safe wording is that the MeTTa scaffold identifies which subtasks belong to which executor. Stable parsing gates can be scripts, ambiguous paraphrase gates can become TRM data, symbolic solvers can own closure, and the LLM can remain a proposal or ambiguity-resolution component.

The desired publishable result is not simply "MeTTa improves scores." The stronger claim is:

> MeTTa improves TRM training and deployment by converting semi-failed LLM outputs into typed repair/verifier/commit examples and by exposing a skill-level task graph. Small LLMs can serve as proposal sources or commit rudders once the symbolic scaffold exposes failure state, while stable gates should move to scripts/solvers and uncertain verifier-facing gates should become trained TRM specializations.

## Next Run Commands

Local 3B reproduction:

```powershell
python research\scripts\run_3b_repair_training_rudder_benchmark.py --max-cases 0 --shots 4 --max-tokens 64 --timeout-sec 120
```

OOM-safe local reproduction of the strongest current arm:

```powershell
python research\scripts\run_3b_repair_training_rudder_benchmark.py --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_3b_metta_static_gate_oom_safe" --max-cases 0 --ctx 1536 --batch-size 128 --ubatch-size 32 --max-tokens 48 --timeout-sec 120 --max-child-rss-mb 2500 --cooldown-sec 0.5 --arm metta_static_gate_rudder
```

9B/27B equivalent:

```powershell
python research\scripts\run_3b_repair_training_rudder_benchmark.py --model-path <GGUF_OR_BACKEND_MODEL> --llama-completion-path <LLAMA_COMPLETION> --out-dir <MODEL_SPECIFIC_OUT_DIR> --max-cases 0 --shots 4 --max-tokens 64 --timeout-sec 180
```

If the 9B/27B backend is not llama.cpp, preserve the prompt construction, row selection, and output schema exactly.

No-model verifier target refresh:

```powershell
python research\scripts\build_c_signature_commit_trm_pack.py
python research\scripts\sweep_c_signature_commit_policies.py
python research\scripts\sweep_c_signature_postrepair_verifiers.py
python research\scripts\build_metta_trm_methodology_lift_matrix.py
```
