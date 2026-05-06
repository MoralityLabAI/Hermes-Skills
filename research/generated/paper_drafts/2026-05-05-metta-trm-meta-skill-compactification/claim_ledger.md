# Claim Ledger

## Allowed Claims

| Claim | Label | Evidence |
| --- | --- | --- |
| A local Qwen2.5-3B Q4 model routed three broad-domain prompts correctly. | `live_model_run` | `D:\metta_trm_meta_small_model_bench\domain_router_3b\domain_router_bootstrap_20260505T201352Z` |
| In a two-domain live 3B package bootstrap, raw verifier score averaged `0.5407` and repaired score averaged `0.9115`. | `live_model_run` plus deterministic repair | `D:\metta_trm_meta_small_model_bench\domain_router_3b\domain_router_bootstrap_20260505T203352Z\bootstrap_runs\small_model_bootstrap_20260505T203446Z\summary.json` |
| The repaired two-domain packages reached `100%` runtime-readiness and training-row readiness. | deterministic verifier result | Same summary JSON |
| In a three-domain live 3B package bootstrap, raw verifier score averaged `0.4936` and repaired score averaged `0.9048`. | `live_model_run` plus deterministic repair | `D:\metta_trm_meta_small_model_bench\domain_router_3b_vdp_20260506_live\domain_router_bootstrap_20260506T211808Z\bootstrap_runs\small_model_bootstrap_20260506T212022Z\summary.json` |
| The repaired three-domain packages reached `100%` runtime-readiness and training-row readiness. | deterministic verifier result | Same summary JSON |
| A five-domain held-out repair study improved verifier average from `0.8633` to `0.9735`. | `deterministic_replay` | `D:\metta_trm_meta_small_model_bench\heldout_generalization\repair_generalization_20260505T174032Z\summary.json` |
| The fixed repair controller reached exact action rate `1.0` on 117 held-out repair messages. | controller contract eval | `D:\metta_trm_meta_small_model_bench\heldout_generalization\repair_generalization_20260505T174032Z\controller_eval_on_heldout_repairs_v2\summary.json` |
| MeTTa can define a proposed feature-contract layer for tiny LoRA steering of TRM controllers. | `training_corpus_plan` | `tables/vpd_tiny_lora_experiment_matrix.csv` and `figures/vpd_tiny_lora_flow.mmd` |
| A 5M-class local commit/veto LoRA run executed end-to-end under a Windows Job Object cap: 4,137 rows, 608 heldout rows, peak RAM `576.5 MB`. | `control_plane_threshold_eval` | `D:\metta_trm_meta_small_model_bench\commit_veto_feature_steering_v4\trm_lora_vpd_cost_sensitive_5m\summary.json` and `D:\metta_trm_meta_small_model_bench\commit_veto_feature_steering_v4\jobcap_vpd_cost_sensitive_5m\jobcap.summary.json` |
| Rank-8 LoRA improved held-out commit/veto accuracy from `0.8931` to `0.9786`, boundary accuracy from `0.8571` to `0.9714`, and false-commit rate from `0.1189` to `0.0093`. | `control_plane_threshold_eval` | Same summary JSON |
| Rank-4 LoRA reached a lower false-commit rate of `0.0070`, with accuracy `0.9704` and false-veto rate `0.0838`. | `control_plane_threshold_eval` | Same summary JSON |
| A 3B-derived commit/veto LoRA run executed under the same cap: 2,051 rows, 289 heldout rows, peak RAM `571.2 MB`, and local VDP Rust component scoring enabled. | `control_plane_threshold_eval` | `D:\metta_trm_meta_small_model_bench\commit_veto_feature_steering_3b_vdp_20260506\trm_lora_vdp_rust_3b\summary.json` and `D:\metta_trm_meta_small_model_bench\commit_veto_feature_steering_3b_vdp_20260506\jobcap_vdp_rust_3b\jobcap.summary.json` |
| In the 3B-derived commit/veto run, rank-2 LoRA reached `0.8720` held-out argmax accuracy, while the conservative rank-4 frontier reached `0.8478` accuracy with zero false commits. | `control_plane_threshold_eval` | Same summary JSON |

## Disallowed Claims For Current Evidence

| Claim | Reason |
| --- | --- |
| The 3B model autonomously writes correct Hermes skills. | The result depends on deterministic repair, verification, and row export. |
| The ten-domain lattice has been fully validated with live 3B package authoring. | The full ten-domain run is heuristic-only so far; live package authoring covers three domains. |
| A trained neural TRM has learned the repair policy. | Current repair controller evidence is template/controller-contract evaluation. |
| Repaired package score implies downstream benchmark gain. | Package verification is not the same as live task performance. |
| Goodfire VPD has already been applied to these TRM controllers. | A local VDP Rust scorer has been applied to LoRA controller components, but this is not a Goodfire VPD reproduction. |
| Tiny LoRA feature steering of TRMs has already improved downstream benchmark scores. | The current LoRA result is a commit/veto control-plane smoke benchmark, not a downstream skill benchmark. |
| The held-out frontier budget-oracle point is deployable as-is. | It uses held-out frontier inspection and should be treated as a calibration target, not validation-selected policy. |
| Goodfire Ember feature steering and VPD are the same method. | Ember steering is an activation-feature interface; VPD is parameter decomposition. The paper should distinguish them. |
| The 5M-class commit/veto LoRA run proves downstream skill improvement. | It is a control-plane heldout benchmark over commit/veto rows, not a downstream benchmark over live skill outcomes. |

## Best Short Claim

Small local LLMs can act as broad routers and artifact drafters inside a MeTTa/TRM control plane when syntax, verification, repair, and commit/veto decisions are externalized into typed symbolic and TRM-trainable modules.

## Best Forward-Looking Claim

MeTTa can turn harness I/O, verifier outcomes, and repair traces into explicit feature contracts for tiny LoRA adapters on TRM controllers; VPD-style parameter decomposition can then audit whether those adapters are using sparse, causally meaningful subcomponents rather than broad opaque drift.
