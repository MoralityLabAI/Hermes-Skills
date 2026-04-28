# Addendum: Local 3B MeTTa Action-Space Rudder Benchmark

Status: draft addendum  
Date: April 28, 2026

## Thesis

The previous local 3B rudder benchmark showed the failure mode: a small LLM can often choose `commit` versus `reject_or_abstain`, but it is weak as an unconstrained repair-action selector. The next skill design moves repair-action selection out of the LLM and into a MeTTa action-space gate, then uses the 3B only where a commit/veto decision remains ambiguous.

The full result is [local_3b_repair_training_rudder.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_3b_metta_action_space_rudder_benchmark\local_3b_repair_training_rudder.results.md>).

## Setup

Model: local `Qwen2.5-3B-Instruct-Q4_K_M` via llama.cpp CUDA.  
Rows: all `88` non-train Pure-TRM rows from the near-miss split.  
Baseline comparison: prior `raw_3b_rudder` and `repair_training_rudder` from April 26.

New arms:

- `metta_action_space_rudder`: MeTTa fixes the repair action; 3B chooses commit/veto.
- `metta_action_space_training_rudder`: same, with retrieved near-miss train examples.
- `metta_static_gate_rudder`: MeTTa fixes repair action and handles obvious exact/no-gain states before falling back to 3B.
- `metta_validator_gate`: post-repair validator ceiling; not a prompt-level 3B result.

## Result

| Arm | Rows | Target-action acc | Repair-action acc | Joint acc |
| --- | ---: | ---: | ---: | ---: |
| `raw_3b_rudder` | `88` | `0.7159` | `0.4091` | `0.3636` |
| `repair_training_rudder` | `88` | `0.7955` | `0.3409` | `0.3182` |
| `metta_action_space_rudder` | `88` | `0.7500` | `1.0000` | `0.7500` |
| `metta_action_space_training_rudder` | `88` | `0.6932` | `1.0000` | `0.6932` |
| `metta_static_gate_rudder` | `88` | `0.9545` | `1.0000` | `0.9545` |
| `metta_validator_gate` | `88` | `1.0000` | `1.0000` | `1.0000` |

## Read

This gives a concrete improvement on a lane where the 3B failed under the naive design. The 3B should not be asked to choose from the global repair-action vocabulary. MeTTa should narrow or select the repair action from env family, failure label, and proposal tier; the LLM can remain as a lightweight commit/veto rudder.

The strongest practical arm is `metta_static_gate_rudder`: it reaches `0.9545` joint accuracy while still using the local 3B for ambiguous commit decisions. The remaining misses are mostly ambiguous `c_signature_fail` no-gain cases where pre-repair state alone is insufficient. The `metta_validator_gate` ceiling shows that a post-repair verifier/commit TRM can close those misses.

## Claim Boundary

The `metta_static_gate_rudder` result is a skill-circuit benchmark, not a trained TRM-weight result. The `metta_validator_gate` arm is an upper bound using post-repair validation. The publishable claim should therefore be: MeTTa action-space narrowing and verifier-visible commit gates can compactify the LLM role and recover a large share of the naive 3B/TRM failure mode; the final step is training the verifier/commit TRM and rerunning at 9B/27B.

## OOM-Safe Reproduction

After an OOM report, the runner was patched with explicit llama.cpp resource controls: `--ctx`, `--batch-size`, `--ubatch-size`, `--max-child-rss-mb`, and `--cooldown-sec`.

OOM-safe command profile:

```powershell
python research\scripts\run_3b_repair_training_rudder_benchmark.py --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_3b_metta_static_gate_oom_safe" --max-cases 0 --ctx 1536 --batch-size 128 --ubatch-size 32 --max-tokens 48 --timeout-sec 120 --max-child-rss-mb 2500 --cooldown-sec 0.5 --arm metta_static_gate_rudder
```

OOM-safe result over the same `88` held-out rows:

| Arm | Target-action acc | Repair-action acc | Joint acc | Max child RSS MB |
| --- | ---: | ---: | ---: | ---: |
| `metta_static_gate_rudder` | `0.9432` | `1.0000` | `0.9432` | `2369.8008` |

This is the safer local reproduction profile. It is slightly below the earlier full sweep result (`0.9545`) but stays under the explicit `2500 MB` child-RSS cap and runs only the highest-signal arm.

## Failure Closure And Next TRM Pack

A no-model replay adds a high-precision static rule for the safety-route literal-union miss and recovers the `0.9545` joint result without another 3B call. The remaining four misses are all `c_signature_fail` no-gain rows where the repair action is correct but the commit decision needs post-repair validation.

Failure closure artifact: [static_gate_failure_closure.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_3b_metta_static_gate_failure_closure\static_gate_failure_closure.results.md>).

The resulting next training artifact is [c_signature_commit_trm_pack.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\c_signature_commit_trm_pack\c_signature_commit_trm_pack.md>). It contains `122` C-signature commit rows: `86` train, `16` validation, and `20` holdout. The primary metric should be false-commit rate, because accuracy alone hides the no-gain over-commit failure mode.

## Simple Policy Sweep

A deterministic policy sweep over visible scalar features confirms that this should not be solved with a naive rule. The validation-selected policy, `knn_k3_reject_ge_0p34`, reaches validation accuracy `1.0000` with validation false-commit rate `0.0000`, but fails on holdout with false-commit rate `1.0000`.

The holdout-safe visible-feature rules, such as `edit_2_4_reject`, can reduce holdout false commits to `0.0000`, but they are lossy guards; `edit_2_4_reject` has validation accuracy `0.5000` and false-reject rate `0.5714`.

Policy sweep artifact: [c_signature_commit_policy_sweep.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\c_signature_commit_policy_sweep\c_signature_commit_policy_sweep.results.md>).

Interpretation: pre-repair scalar features are insufficiently stable. The post-repair verifier/commit TRM should consume richer post-repair validation state, and paper metrics should emphasize false-commit rate on holdout.

## Post-Repair Multi-Signal Verifier Sweep

The C-signature pack now preserves post-repair state: `after_reward`, `reward_delta`, `after_exact`, and before/after T/C signature pass flags. A second deterministic sweep tests whether the remaining false commits are solved by exposing this richer verifier state to the commit TRM.

Artifact: [c_signature_postrepair_verifier.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\c_signature_postrepair_verifier_sweep\c_signature_postrepair_verifier.results.md>).

| Policy | Signal class | Val acc | Val false commit | Val false reject | Holdout acc | Holdout false commit | Holdout false reject |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `after_signature_complete_only` | post-symbolic | `0.8750` | `1.0000` | `0.0000` | `0.9000` | `1.0000` | `0.0000` |
| `after_exact_only` | exact evaluator | `0.8750` | `0.0000` | `0.1429` | `0.7000` | `0.0000` | `0.3333` |
| `postrepair_exact_or_gain_gt_0` | multi-signal evaluator | `1.0000` | `0.0000` | `0.0000` | `1.0000` | `0.0000` | `0.0000` |

Read: signature completion is necessary but not sufficient, because all repaired C-signature candidates pass signatures, including no-gain repairs. Exact-only validation is safe but loses partial improvements. The useful target is multi-signal post-repair state: exactness plus positive reward delta.

This gives a cleaner basis for the next trained TRM than the pre-repair policy sweep. The post-repair commit TRM should learn a MeTTa-framed action:

```scheme
(= (c-signature-commit-action $state)
   (if (or (after-exact $state) (> (reward-delta $state) 0.0))
       commit
       reject_or_abstain))
```

Claim boundary: this is still an evaluator-backed verifier ceiling and training-target definition. The paper should not call it trained TRM performance until a capped Pure-TRM-Trainer run learns this decision from train rows and holds it on `val_seen` plus `holdout_seen`.
