# MeTTa/TRM Meta-Skill Compactification Paper Seed

Working title: **MeTTa/TRM Meta-Skills as a Control Plane for Compact Domain Bootstrap**

This folder starts a paper package for the local 3B result: a quantized Qwen2.5-3B model can route broad domains and draft MeTTa/TRM package skeletons when exactness is delegated to a symbolic repair, verifier, and TRM-row export control plane.

## Contents

- `paper.md`: first-pass manuscript scaffold.
- `claim_ledger.md`: claim labels and what evidence can support each claim.
- `evidence_manifest.json`: local source artifacts and scripts.
- `tables/domain_router_3b_results.csv`: live 3B routing/bootstrap numbers.
- `tables/repair_controller_results.csv`: repair curriculum and controller evidence.
- `tables/commit_veto_lora_smoke_results.csv`: current 5M-class commit/veto LoRA feature-steering result.
- `figures/architecture.mmd`: Mermaid source for the architecture figure.

## Current Bounded Result

The strongest live-model result is the two-domain 3B bootstrap run at:

`D:\metta_trm_meta_small_model_bench\domain_router_3b\domain_router_bootstrap_20260505T203352Z`

In that run, broad-domain routing was correct for the two tested domains, raw generated packages averaged `0.5407`, deterministic repair raised the average to `0.9115`, and both packages were ready for TRM rows and runtime packet use after repair.

Do not describe this as autonomous skill invention. The measured result is a hybrid control-plane result: small-model drafting plus deterministic MeTTa repair, verification, and row export.

## Current Feature-Steering Result

The current VPD-adjacent feature-steering artifact is:

`D:\metta_trm_meta_small_model_bench\commit_veto_feature_steering_v4\trm_lora_vpd_cost_sensitive_5m`

It trains rank `1,2,4,8` LoRA adapters on a 4.24M-parameter commit/veto TRM over 4,137 MeTTa feature-contract rows. On 608 held-out rows, rank-8 LoRA improves accuracy from `0.8931` to `0.9786` and reduces false commits from `0.1189` to `0.0093`. Treat this as a control-plane feature-steering result, not a Goodfire VPD reproduction or downstream skill benchmark.
