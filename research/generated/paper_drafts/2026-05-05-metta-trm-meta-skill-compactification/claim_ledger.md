# Claim Ledger

## Allowed Claims

| Claim | Label | Evidence |
| --- | --- | --- |
| A local Qwen2.5-3B Q4 model routed three broad-domain prompts correctly. | `live_model_run` | `D:\metta_trm_meta_small_model_bench\domain_router_3b\domain_router_bootstrap_20260505T201352Z` |
| In a two-domain live 3B package bootstrap, raw verifier score averaged `0.5407` and repaired score averaged `0.9115`. | `live_model_run` plus deterministic repair | `D:\metta_trm_meta_small_model_bench\domain_router_3b\domain_router_bootstrap_20260505T203352Z\bootstrap_runs\small_model_bootstrap_20260505T203446Z\summary.json` |
| The repaired two-domain packages reached `100%` runtime-readiness and training-row readiness. | deterministic verifier result | Same summary JSON |
| A five-domain held-out repair study improved verifier average from `0.8633` to `0.9735`. | `deterministic_replay` | `D:\metta_trm_meta_small_model_bench\heldout_generalization\repair_generalization_20260505T174032Z\summary.json` |
| The fixed repair controller reached exact action rate `1.0` on 117 held-out repair messages. | controller contract eval | `D:\metta_trm_meta_small_model_bench\heldout_generalization\repair_generalization_20260505T174032Z\controller_eval_on_heldout_repairs_v2\summary.json` |
| MeTTa can define a proposed feature-contract layer for tiny LoRA steering of TRM controllers. | `training_corpus_plan` | `tables/vpd_tiny_lora_experiment_matrix.csv` and `figures/vpd_tiny_lora_flow.mmd` |
| A local commit/veto LoRA smoke run executed end-to-end and rank-4 improved held-out exact action accuracy from `0.9085` to `0.9150` on 306 rows. | `control_plane_threshold_eval` | `D:\metta_trm_meta_small_model_bench\commit_veto_feature_steering_v1\trm_lora_smoke\summary.json` |

## Disallowed Claims For Current Evidence

| Claim | Reason |
| --- | --- |
| The 3B model autonomously writes correct Hermes skills. | The result depends on deterministic repair, verification, and row export. |
| The ten-domain lattice has been fully validated with live 3B package authoring. | The full ten-domain run is heuristic-only so far; live package authoring covers two domains. |
| A trained neural TRM has learned the repair policy. | Current repair controller evidence is template/controller-contract evaluation. |
| Repaired package score implies downstream benchmark gain. | Package verification is not the same as live task performance. |
| Goodfire VPD has already been applied to these TRM controllers. | This is a proposed extension; no local VPD run over a TRM controller exists yet. |
| Tiny LoRA feature steering of TRMs has already improved downstream benchmark scores. | The current LoRA result is a commit/veto control-plane smoke benchmark, not a downstream skill benchmark. |
| The commit/veto LoRA smoke is the final 5M-parameter TRM result. | The smoke used a smaller hidden-256 controller to validate the loop. |
| Goodfire Ember feature steering and VPD are the same method. | Ember steering is an activation-feature interface; VPD is parameter decomposition. The paper should distinguish them. |

## Best Short Claim

Small local LLMs can act as broad routers and artifact drafters inside a MeTTa/TRM control plane when syntax, verification, repair, and commit/veto decisions are externalized into typed symbolic and TRM-trainable modules.

## Best Forward-Looking Claim

MeTTa can turn harness I/O, verifier outcomes, and repair traces into explicit feature contracts for tiny LoRA adapters on TRM controllers; VPD-style parameter decomposition can then audit whether those adapters are using sparse, causally meaningful subcomponents rather than broad opaque drift.
