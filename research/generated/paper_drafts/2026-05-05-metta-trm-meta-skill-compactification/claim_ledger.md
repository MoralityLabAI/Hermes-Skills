# Claim Ledger

## Allowed Claims

| Claim | Label | Evidence |
| --- | --- | --- |
| A local Qwen2.5-3B Q4 model routed three broad-domain prompts correctly. | `live_model_run` | `D:\metta_trm_meta_small_model_bench\domain_router_3b\domain_router_bootstrap_20260505T201352Z` |
| In a two-domain live 3B package bootstrap, raw verifier score averaged `0.5407` and repaired score averaged `0.9115`. | `live_model_run` plus deterministic repair | `D:\metta_trm_meta_small_model_bench\domain_router_3b\domain_router_bootstrap_20260505T203352Z\bootstrap_runs\small_model_bootstrap_20260505T203446Z\summary.json` |
| The repaired two-domain packages reached `100%` runtime-readiness and training-row readiness. | deterministic verifier result | Same summary JSON |
| A five-domain held-out repair study improved verifier average from `0.8633` to `0.9735`. | `deterministic_replay` | `D:\metta_trm_meta_small_model_bench\heldout_generalization\repair_generalization_20260505T174032Z\summary.json` |
| The fixed repair controller reached exact action rate `1.0` on 117 held-out repair messages. | controller contract eval | `D:\metta_trm_meta_small_model_bench\heldout_generalization\repair_generalization_20260505T174032Z\controller_eval_on_heldout_repairs_v2\summary.json` |

## Disallowed Claims For Current Evidence

| Claim | Reason |
| --- | --- |
| The 3B model autonomously writes correct Hermes skills. | The result depends on deterministic repair, verification, and row export. |
| The ten-domain lattice has been fully validated with live 3B package authoring. | The full ten-domain run is heuristic-only so far; live package authoring covers two domains. |
| A trained neural TRM has learned the repair policy. | Current repair controller evidence is template/controller-contract evaluation. |
| Repaired package score implies downstream benchmark gain. | Package verification is not the same as live task performance. |

## Best Short Claim

Small local LLMs can act as broad routers and artifact drafters inside a MeTTa/TRM control plane when syntax, verification, repair, and commit/veto decisions are externalized into typed symbolic and TRM-trainable modules.
