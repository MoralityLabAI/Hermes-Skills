# MeTTa/TRM Meta-Skills as a Control Plane for Compact Domain Bootstrap

Patrick Dugan, Morality Lab

## Abstract

We study whether a small local model can participate in skill improvement when the exact symbolic burden is moved out of the language model and into a typed MeTTa/TRM control plane. The system routes a task into a broad domain lattice, asks a quantized Qwen2.5-3B model to draft a compact MeTTa/TRM package, then runs deterministic repair, verification, and TRM-row export. In a live local two-domain bootstrap run, raw 3B-authored packages scored `0.5407` on the package verifier, while repaired packages scored `0.9115` and reached `100%` runtime-readiness and training-row readiness. A separate held-out repair study across five domains showed deterministic repair improving package verifier score from `0.8633` to `0.9735`, with a fixed template repair controller reaching `1.0000` exact action rate on 117 held-out repair messages. These results support a bounded compactification claim: small models can draft and route useful control-plane artifacts when symbolic exactness, repair, and commit/veto decisions are delegated to modular MeTTa/TRM scaffolds.

## Thesis

The practical goal is not to make a 3B model behave like a large general reasoner. The goal is to discover which parts of a skill-improvement loop can be made low-bandwidth, typed, and trainable enough that the LLM becomes a proposer while the control plane carries exactness.

This paper frames a MeTTa/TRM meta-skill as a compact skill-authoring loop:

1. Route a task through broad subject and cognition domains.
2. Ask a small model to draft a minimal package under a frozen contract.
3. Repair syntax and unsupported atoms deterministically.
4. Verify manifest, syntax, contract, retrieval, repair, and trainer-export readiness.
5. Export role-specific rows for TRM controllers.
6. Commit, veto, or request more data based on scorecard evidence.

The experiment is a capability-compactification probe. It asks how much of the scaffolding needed for skill growth can be pushed into cheap, typed control systems rather than paid for with larger inference context and larger generative models.

## Architecture

The current implementation lives in `metta-trm-meta-skill`. The skill defines the role set `author_router`, `metta_syntax_repair`, `semantic_contract_verifier`, `retrieval_policy_router`, `skill_patch_controller`, and `commit_veto`.

The domain lattice is deliberately coarser than a final Hermes skill. It includes broad domains such as `formal_reasoning`, `empirical_science`, `systems_engineering`, `creative_narrative`, `safety_security`, `tool_operations`, and `metacognition_learning`. Routing into these domains creates a reusable adapter layer before any final skill specialization.

The small model is used in two places:

1. Domain routing: select a broad domain and cognitive modes from a task prompt.
2. Package drafting: generate six small files under a frozen contract.

The non-LLM control plane handles exactness:

1. File extraction.
2. MeTTa syntax repair.
3. JSON manifest validation.
4. Contract and retrieval-policy coverage scoring.
5. Runtime-readiness scoring.
6. TRM-row export.

## Experiment 1: Broad Domain Routing

The router study first validates that broad routing can be treated separately from package authoring. A heuristic ten-domain study routes one case for each domain and reaches `10/10`; this is a deterministic sanity check, not a live model claim.

A live local 3B routing run then tests three held-out task cards against the same domain lattice. The model routes all three correctly: `formal_reasoning`, `empirical_science`, and `systems_engineering`.

This result only supports a narrow claim: the 3B model can select broad domain labels under a compact JSON routing contract for the tested cases.

## Experiment 2: 3B Package Bootstrap

The live 3B package bootstrap used a CPU-only llama.cpp OpenAI-compatible shim with the GGUF model:

`D:\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf`

The main two-domain run tested:

1. `domain_router_01_formal_reasoning`
2. `domain_router_02_empirical_science`

The process took `680.9` seconds. Each domain produced six package files. Before repair, the average verifier score was `0.5407`. After deterministic repair, the average score was `0.9115`. Both repaired packages were ready for TRM-row export and runtime packet use.

The important observation is that raw small-model output remains brittle. It is not publishable as a working skill artifact without repair. The control-plane result appears after strict prompting, staged generation, repair, and verification.

## Repair Curriculum

The repair curriculum contains `432` synthetic rows split into `367` train and `65` validation messages. Roles are:

1. `metta_syntax_repair`: `360`
2. `commit_veto`: `36`
3. `semantic_contract_verifier`: `36`

Repair types include unsupported head projection, env-argument reorder, env-argument insertion, env-wrapper projection, and wrapped single-atom repair.

A template controller reaches exact action rate `1.0` and mean key accuracy `1.0` on the validation split. This is not yet a neural TRM benchmark. It is a controller-contract sanity check showing that the repair action space can be made fully typed and low entropy.

## Held-Out Repair Generalization

A held-out generalization study tests five domains not in the original repair curriculum: ALife complexity sculpting, diplomacy coalition forecasting, BlueBeam tamper probing, storyworld balance, and Prime math candidate auditing.

Raw bootstrap verifier score averaged `0.8633`; deterministic repair raised it to `0.9735`. A fixed controller evaluated on `117` held-out repair messages reached exact action rate `1.0` and mean key accuracy `1.0`.

This supports a stronger methodology claim than the two-domain 3B run: many repair decisions are not opaque reasoning problems. They are typed transformations over a narrow action space.

## Interpretation

The central result is not that a 3B model can autonomously design robust skills. The result is that a small model can become useful in a skill-growth loop if the loop is decomposed into:

1. broad routing,
2. constrained artifact drafting,
3. deterministic symbolic repair,
4. typed verification,
5. role-specific controller rows,
6. commit/veto gates.

This changes the scaling question. Instead of asking how large the LLM must be to write a correct skill in one pass, the relevant question becomes how much of the skill-improvement process can be moved into a symbolic and TRM-trainable control plane.

## Feature Steering Extension: MeTTa, VPD, and Tiny LoRA TRMs

The compactification frame naturally extends from training TRM controllers to steering them. The distinction matters: Goodfire's public feature-steering work in Ember is primarily an activation-feature interface, while their VPD line is a parameter-decomposition method that identifies sparse parameter subcomponents used by a model on particular inputs. The useful research direction here is to combine both intuitions without overclaiming either one.

In this paper's setting, a TRM controller is small enough that feature steering can be made concrete. We already have harness I/O rows, verifier labels, repair reports, commit/veto decisions, retrieval choices, and MeTTa contracts. These can define typed behavioral features for TRM controllers:

1. exact JSON/tool contract adherence,
2. near-miss repair recognition,
3. semantic verifier caution,
4. retrieval precision over MCP handles,
5. abstain versus commit thresholding,
6. symbolic-closure recognition,
7. unsafe shortcut rejection.

MeTTa's role is to make those features explicit before training. Instead of asking a small adapter to learn an opaque "better controller" target, each row can carry a symbolic feature contract:

```text
(feature-target "commit_veto" "raise abstain when verifier_disagreement is high")
(feature-target "retrieval_policy_router" "prefer exact handle over broad semantic near-miss")
(feature-forbid "metta_syntax_repair" "invent unsupported atom head")
(feature-success "semantic_contract_verifier" "reject wrong-scope resource")
```

That gives a supervised bridge from harness traces to feature targets. A tiny LoRA on a TRM can then be trained to move controller behavior along those feature axes while preserving the base controller's successful behavior. The adapter does not need broad generative capacity. It needs to alter a small number of typed decisions.

VPD-style analysis becomes the audit layer. If VPD decomposes model parameters into subcomponents that are sparse and causally important on particular datapoints, then a TRM controller can be inspected for parameter subcomponents associated with feature contracts such as "commit-veto caution" or "exact-handle retrieval." The proposed loop is:

1. collect harness I/O and verifier outcomes,
2. convert them to MeTTa feature contracts,
3. train tiny LoRA adapters on TRM controller rows,
4. use VPD-style decomposition to identify which parameter subcomponents the adapter is using,
5. ablate or stress-test those subcomponents against held-out semi-failures,
6. retain adapters only when they improve the target feature without damaging unrelated controller behavior.

The research claim is methodological but now has a first smoke implementation. It says that MeTTa can frame the feature space for steering small TRM controllers, while harness I/O provides dense contrastive supervision and VPD-style decomposition provides a mechanistic audit target. If successful, this would make compactification more surgical: instead of training a larger controller, train a rank-1 to rank-8 adapter that selectively improves one control feature under verifier supervision.

A capped local CPU run tested the `commit_veto_threshold` feature using 4,137 feature-contract rows derived from harvested repair messages plus synthetic boundary cases. The run used a hidden-2048, four-step recursive controller with 4,239,362 base parameters and rank `1,2,4,8` LoRA adapters. The Windows Job Object wrapper reported completion with peak RAM `576.5 MB`, average RAM `540.1 MB`, and no IO-cap abort. This is the first 5M-class local result for the feature-steering lane, though it remains a commit/veto control-plane benchmark rather than a downstream skill benchmark.

On 608 held-out rows, the base TRM reached `0.8931` exact decision accuracy, `0.1189` false-commit rate, `0.0782` false-veto rate, and `0.8571` boundary accuracy. Rank-8 LoRA steering raised held-out accuracy to `0.9786` and boundary accuracy to `0.9714`, while reducing false commits to `0.0093` and false vetoes to `0.0503`. Rank-4 LoRA reached `0.9704` accuracy with an even lower false-commit rate of `0.0070`, at the cost of false vetoes rising to `0.0838`. Validation-tuned thresholds gave a conservative rank-8 operating point with weighted error cost `0.0237`, false-commit rate `0.0070`, false-veto rate `0.0838`, and accuracy `0.9704`.

This is a stronger result than the earlier hidden-256 smoke, but the claim boundary remains important. It does not show that Goodfire VPD has been reproduced locally, and it does not show downstream benchmark lift. It shows that MeTTa feature contracts can generate a trainable commit/veto feature surface, that tiny LoRA adapters on a small TRM can steer that surface sharply, and that VPD-style adapter ablation is an appropriate next audit layer for asking whether the steering is sparse and causal rather than broad controller drift.

## Limitations

The strongest live package-authoring result currently covers two domains, not the full ten-domain lattice. The held-out repair study is broader, but it is not a full live 3B domain-bootstrap study across all domains.

The repair controller result is a template controller evaluation, not a trained neural TRM result. It demonstrates action-space compactness and label determinism, not learned generalization by itself.

Verifier scores measure package readiness under the local compiler and evaluator. They are not direct downstream task-success metrics. A later experiment should connect package quality to live benchmark improvement.

The feature-steering extension now has a 5M-class local commit/veto run, but it is still a control-plane benchmark. Its VPD-style audit is a local adapter-ablation probe rather than a reproduction of Goodfire's VPD method. Those distinctions should remain explicit.

## Next Experiments

The next paper-grade step is a ten-domain live 3B bootstrap with the same frozen prompt and the same deterministic repair pipeline. The primary table should report route accuracy, raw package score, repaired package score, runtime-readiness rate, and TRM-row readiness rate separately.

The second step is to replace the template repair controller with trained TRM controllers and evaluate on held-out repair messages and held-out package tasks.

The third step is downstream transfer: use generated packages to improve actual benchmark arms and measure whether the repaired control-plane artifacts produce task-level gains.

The fourth step is feature-steered TRM compactification: train rank-1 to rank-8 LoRA adapters for individual controller features, compare base TRM versus LoRA-steered TRM on held-out semi-failure rows, and audit the adapters with VPD-style parameter decomposition.
