# Role-Aware TRM Infusion For Hermes Skills: Weekly Draft From April 16, 2026 To April 22, 2026

Status: draft  
Date: April 22, 2026

## Abstract

This draft summarizes one week of Hermes Skills benchmark and training work on Primehub-style environments using `qwen35_9b` and `qwen35_27b`. The strongest result is not a broad reasoning breakthrough but a clearer decomposition of where Task-Representation Memory (TRM) helps. Across the week, TRM became measurably more useful as a control-plane and contract-repair layer than as a general-purpose reasoning substitute. A completed benchmark handoff on April 16, 2026 finished `90/90` tasks and produced `20` new positive replays, while later work on April 20 to April 22 extended environment coverage, introduced role-based routing and trainer policies, and produced two concrete live wins: a narrow `choice_contract` gain on `boolq` for `qwen35_27b`, and a stronger retrieval-assisted `structured_map` result on exact-structure-sensitive tasks such as `ascii_tree` and `pydantic_adherence`. We also resolved a transport-layer failure mode on the `simpleqa` family, showing that these tasks now reach the scorer with visible output, even though answer quality remains weak. The main conclusion is that Hermes should stay anchored in TRM infusion for the paper-facing empirical story, while MeTTa remains best framed as a symbolic packaging layer that has compiled successfully but has not yet earned benchmark-first billing.

## 1. Introduction

The question behind this week of work was not whether TRM can be attached to Hermes skills, but whether a more disciplined version of TRM infusion can produce measurable benchmark gains and cleaner research framing. Earlier runs had already suggested that Hermes benefits from replay-derived critics, format priors, and route guards, but the results were uneven across environment families and model scales.

Three concrete goals shaped the work from April 16, 2026 through April 22, 2026:

1. consolidate benchmark coverage across the current Primehub-style environment set
2. make the TRM layer role-aware rather than treating all retrieved supervision as equivalent
3. determine whether improvements come from better training data, better routing, better retrieval structure, or simply better runtime hygiene

The results point to a narrower but more defensible thesis than a generic "TRM helps reasoning" claim. In this repo, TRM currently helps most when it is used to repair exact answer contracts, preserve structured output validity, and stabilize runtime behavior around brittle interfaces.

## 2. Data Compilation For The Week

A reproducible benchmark spine for this draft now lives in [trm_infused_baseline_summary_table.md](</C:/projects/Hermes-Skills/Hermes Skills/research/generated/trm_infused_baseline_summary_table.md>) and [trm_infused_baseline_crossref.md](</C:/projects/Hermes-Skills/Hermes Skills/research/generated/trm_infused_baseline_crossref.md>). The summary table is the paper-facing view; the cross-ref file is the fuller artifact map with machine-readable JSON alongside it.

The benchmark starting point for this draft is the BlueBeam handoff bundle at [data/handoffs/bluebeam_mechinterp_2026-04-16/README.md](</C:/projects/Hermes-Skills/Hermes Skills/data/handoffs/bluebeam_mechinterp_2026-04-16/README.md>). That bundle records a finished run with:

- `90/90` tasks completed
- `0` failed
- `0` skipped
- `20` new positive replays copied into the benchmark positive replay set
- `14` new positives from `qwen35_9b`
- `6` new positives from `qwen35_27b`

The same handoff also records the TRM state at that moment:

- `195` merged TRM rows
- `24` exact positives
- `5` weak positives
- `166` negatives
- critic bucket accuracy `0.75`
- retriever exact match `0.0625`
- critic-gated router abstain rate `0.9062`

That snapshot is important because it already showed the central tension of the week: the corpus had become useful enough to guide criticism and abstention, but it was still exemplar-starved as an action generator.

Coverage work continued on April 20, 2026. The missing-environment rerun at [primehub-missing-envs-rerun-20260420.summary.json](</C:/projects/Hermes-Skills/Hermes Skills/data/job_limited_runs/primehub-missing-envs-rerun-20260420.summary.json>) completed cleanly, adding `32/32` successful tasks across `16` environments and both Qwen models. A final two-environment gapfill then showed a cleaner boundary condition: `verbatim_copy` succeeded on both models, but `passthrough` failed on both with `bridge_failure` despite replay and summary artifacts being written, as shown in [primehub_final_eligible_gapfill_20260420/overnight_primehub_benchmark.stout.jsonl](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_final_eligible_gapfill_20260420/overnight_primehub_benchmark.stout.jsonl>). This is evidence of a harness or bridge accounting problem, not simply a missing benchmark attempt.

## 3. Role-Based TRM Reframing

The main methodological change during the week was the introduction of role-based TRM imprinting. The current published role cards are in [data/primehub_skill_trm_matrix/latest/role_based_imprint.md](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_skill_trm_matrix/latest/role_based_imprint.md>). They make the repo's implicit structure explicit:

- `choice_contract` is the broadest action-bearing cluster, with `81` rows and `35` exact positives
- `structured_map` is a narrower schema-formatting role
- `internal_action` is tiny but clean, with `2/2` exact positives
- `hard_reasoning_numeric`, `hard_reasoning_logic`, and `abstain_guard` remain critic-first, sparse, and conservatively routed

This role split matters because it prevented us from over-claiming what the TRM bank could do. The high-signal action-support story is mostly in answer wrappers, schema preservation, and narrow latent actions. The hard reasoning clusters are not retrieval-capable in a broad sense yet; they are mainly verifier roles.

Trainer-policy work reinforced that reading. Near-miss mining and easy-negative downsampling changed the published matrix without claiming a false general improvement. The training-side result was not "TRM solved reasoning," but "better supervision shaping can move specific roles that already have action-bearing signal."

## 4. Live Results

### 4.1 Narrow `choice_contract` lift on `boolq`

The clearest training-side gain this week came from the comparison between the baseline rerun and the mining rerun.

In the baseline run, [qwen35_27b_two-model-contract-repair-v1_boolq_q0017.summary.json](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_trainer_policy_baseline_rerun_20260421/qwen35_27b/qwen35_27b_two-model-contract-repair-v1_boolq_q0017.summary.json>) shows:

- reward `0.0`
- `model_client_fallbacks.total = 1`
- `visible_output_emitted.false = 1`

In the post-mining run, [qwen35_27b_two-model-contract-repair-v1_boolq_q0017.summary.json](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_trainer_policy_mining_rerun_20260421/qwen35_27b/qwen35_27b_two-model-contract-repair-v1_boolq_q0017.summary.json>) shows:

- reward `1.0`
- no model-client fallback
- `visible_output_emitted.true = 1`

This is a real improvement, but it is a narrow one. It is best interpreted as a `choice_contract` success on `qwen35_27b`, not a general reasoning lift. The broader pressure slice later in the week did not show broad generalization across all `choice_contract`-aligned environments.

### 4.2 Stronger evidence for retrieval-assisted `structured_map`

The strongest positive empirical story in the repo at the end of the week is the scoped `structured_map + trm-mcp` retrieval study. The study packet and decision memo live at [research/studies/2026-04-22-primehub-structured-map-retrieval/README.md](</C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-primehub-structured-map-retrieval/README.md>) and [promotion_decision.md](</C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-primehub-structured-map-retrieval/artifacts/promotion_decision.md>).

The promoted, scoped result is:

- `ascii_tree`: retrieval-assisted `0.8`, baseline `0.0`, plain structured-map `0.0`
- `psycho_bench`: retrieval-assisted `3.3311`, baseline `3.3283`, plain structured-map `3.3061`
- `pydantic_adherence`: retrieval-assisted `1.0`, baseline `0.0`, plain structured-map `0.0`

This is the only part of the current Hermes work that supports a stronger positive claim than "parity with better control." Even there, the scope should remain tight: the evidence supports promotion for exact-structure-sensitive lanes, not a blanket claim that retrieval is cheaper or universally better.

### 4.3 Runtime repair on the `simpleqa` family

Another meaningful result from April 22, 2026 is the runtime repair of the `simpleqa` family. The problem here was originally not just factual wrongness; it was that the model path often failed to emit visible scored output at all.

After the runtime and post-processing fixes, [primehub-simpleqa-verified-proof-20260422.summary.json](</C:/projects/Hermes-Skills/Hermes Skills/data/job_limited_runs/primehub-simpleqa-verified-proof-20260422.summary.json>) completed cleanly, and [qwen35_27b_two-model-contract-repair-v1_simpleqa_verified_q0004.summary.json](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_simpleqa_verified_proof_20260422/qwen35_27b/qwen35_27b_two-model-contract-repair-v1_simpleqa_verified_q0004.summary.json>) shows:

- reward `0.0`
- no `model_client_fallbacks`
- `visible_output_emitted.true = 1`
- reasoning mode `off`

This is not yet a benchmark win, but it is a meaningful systems result. It moves `simpleqa`-style failures from "transport/harness failure" to "real judged answer quality failure," which is the right failure surface for further TRM or model work.

## 5. What Did Not Improve

Several negative findings are important enough to state directly.

First, the hard reasoning roles remain weak as retrieval actors. The role cards still show `hard_reasoning_numeric` with only `3` exact positives in `35` rows and `hard_reasoning_logic` with `3` exact positives in `20` rows. These are not yet strong enough for an honest retrieval-led reasoning story.

Second, the broader `choice_contract` pressure slice did not turn the narrow `boolq` gain into a broad family-wide improvement. The pressure results in [data/primehub_choice_contract_pressure_20260421/ledger.jsonl](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_choice_contract_pressure_20260421/ledger.jsonl>) show that most evaluated environments remained at `0.0`, with `winogrande` largely staying at parity rather than improving.

Third, `mmlu_pro` remains a serving-path problem. By the end of the week, the evidence supported the claim that the benchmark harness was no longer the central blocker there; the active failure shape was still tied to hidden reasoning and the model server's output behavior.

Finally, `passthrough` remains unresolved because of a bridge-accounting failure mode. It completes an episode and writes artifacts, but the run is still labeled `execution_failure` with `bridge_failure`.

## 6. Positioning Relative To MeTTa

The repo now contains a concrete MeTTa-to-TRM scaffold, documented in [metta-trm-hermes-pipeline/README.md](</C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/README.md>) and the associated study packet at [research/studies/2026-04-22-metta-trm-hermes-pipeline/README.md](</C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/README.md>). That scaffold successfully compiles a symbolic package into:

- retrieval packets
- critic hints
- trace labels
- bundle manifests and artifact contracts

This is promising, but it does not yet outrank the TRM-infusion track as the main paper story. The MeTTa study currently supports a compiler and packaging claim, not a benchmark-first performance claim. The right framing for the present paper draft is therefore:

- TRM infusion is the empirical core
- MeTTa is the symbolic front-end candidate
- a future paper or later section can evaluate MeTTa as an authoring and compilation layer for TRM artifacts

## 7. Discussion

The central lesson from this week is that Hermes benefits most from TRM when TRM is treated as a structured support system instead of a magic reasoning replacement. The empirical gains line up with that interpretation.

`choice_contract` improved only where the corpus already contained enough action-bearing support to repair exact wrappers. `structured_map` improved where retrieval could provide a narrow schema prior. `simpleqa` improved only at the transport layer, which exposed factual weakness rather than hiding it. Hard reasoning remained mostly critic-only because the underlying bank is still too sparse to justify aggressive retrieval or action support.

That is a useful scientific outcome, even though it is less dramatic than a broad benchmark jump. It tells us where to allocate the next unit of research effort:

1. expand exact-positive banks for hard reasoning roles
2. continue targeted near-miss mining for action-bearing contract families
3. preserve the scoped retrieval path for schema-fragile environments
4. keep the paper's claims aligned with these narrower but stronger wins

## 8. Limitations

This draft reflects one week of work and several small or medium evaluation slices rather than a single held-out grand benchmark. It also mixes system repair, corpus shaping, and benchmark reruns in the same development window, which is useful for engineering but less clean than a frozen ablation campaign. The strongest positive result, retrieval-assisted structured mapping, is still scoped to a small family of exact-structure-sensitive tasks. The strongest `choice_contract` gain is still narrow and mostly visible on `qwen35_27b`.

Accordingly, the draft should not yet claim:

- general TRM-driven reasoning improvement
- universal gains across all Primehub families
- token-efficiency improvements from retrieval
- MeTTa-driven benchmark gains

## 9. Provisional Conclusion

As of April 22, 2026, the strongest defensible paper claim is that role-aware TRM infusion improves Hermes most when it is aligned with the true structure of the task: contract repair, schema preservation, criticism, and routing. Broad reasoning gains remain limited. A symbolic MeTTa layer has now been scaffolded and compiled, but it should be presented as a next-stage authoring system rather than as the current empirical core. For the present paper, the evidence-rich story is still the TRM story.

## Artifact Map

- Benchmark handoff: [data/handoffs/bluebeam_mechinterp_2026-04-16/README.md](</C:/projects/Hermes-Skills/Hermes Skills/data/handoffs/bluebeam_mechinterp_2026-04-16/README.md>)
- Published role cards: [data/primehub_skill_trm_matrix/latest/role_based_imprint.md](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_skill_trm_matrix/latest/role_based_imprint.md>)
- Baseline rerun: [data/primehub_trainer_policy_baseline_rerun_20260421](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_trainer_policy_baseline_rerun_20260421>)
- Mining rerun: [data/primehub_trainer_policy_mining_rerun_20260421](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_trainer_policy_mining_rerun_20260421>)
- Choice-contract pressure slice: [data/primehub_choice_contract_pressure_20260421](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_choice_contract_pressure_20260421>)
- Structured-map retrieval study: [research/studies/2026-04-22-primehub-structured-map-retrieval/README.md](</C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-primehub-structured-map-retrieval/README.md>)
- MeTTa pipeline study: [research/studies/2026-04-22-metta-trm-hermes-pipeline/README.md](</C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/README.md>)
- SimpleQA verified proof: [data/primehub_simpleqa_verified_proof_20260422](</C:/projects/Hermes-Skills/Hermes Skills/data/primehub_simpleqa_verified_proof_20260422>)
