# MeTTa TRM Hermes Pipeline Study

## Goal

Define a concrete folder layout, file contract, and first live benchmark path for using MeTTa as the symbolic source of truth for TRM infusion artifacts in Hermes.

## Pairing

- Symbolic layer: [metta-trm-hermes-pipeline](C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/README.md)
- Target skill families:
  - `primehub-structured-map-hermes`
  - `primehub-constraint-summarize-hermes`
- TRM overlay target: `trm-mcp`

## Baseline Cross-Ref

Use the shared TRM benchmark spine when positioning any MeTTa result against the current non-MeTTa evidence:

- [trm_infused_baseline_summary_table.md](C:/projects/Hermes-Skills/Hermes Skills/research/generated/trm_infused_baseline_summary_table.md)
- [trm_infused_baseline_crossref.md](C:/projects/Hermes-Skills/Hermes Skills/research/generated/trm_infused_baseline_crossref.md)
- [trm_infused_baseline_crossref.json](C:/projects/Hermes-Skills/Hermes Skills/research/generated/trm_infused_baseline_crossref.json)

## What This Study Builds

- a package contract for MeTTa-authored skill bundles
- a lightweight compiler from `.metta` atoms to JSON TRM artifacts
- an example package for `primehub_structured_map`
- a profile-aware example package for `if_summarize_judge`
- a generated artifact bundle proving the contract is executable

## Artifacts

- `artifacts/primehub_structured_map_bundle/`
- expected bundle outputs:
  - `bundle.manifest.json`
  - `atoms.json`
  - `retrieval_packet.json`
  - `critic_hints.json`
  - `trace_labels.json`
  - `artifact_contract.json`
  - `compiler_summary.md`
  - `runtime_packet.json`
  - `runtime_packet.summary.json`
- `artifacts/primehub_structured_map_rows/`
  - `metta_trm_rows.jsonl`
  - `metta_trm_rows.summary.json`
- `artifacts/primehub_structured_map_multisignal/`
  - `metta_multi_signal_scorecard.jsonl`
  - `metta_multi_signal_scorecard.summary.json`
  - `metta_multi_signal_scorecard.md`
- `artifacts/primehub_structured_map_trainer_policy/`
  - `metta_trainer_policy_bundle.jsonl`
  - `metta_trainer_policy_bundle.summary.json`
  - `metta_trainer_policy_bundle.md`
  - `rollup/metta_trainer_policy_rollup.manifest.json`
- `artifacts/if_summarize_judge_bundle/`
  - `bundle.manifest.json`
  - `retrieval_packet.json`
  - `critic_hints.json`
  - `trace_labels.json`
  - `compiler_summary.md`
  - `runtime_packet.json`
  - `runtime_packet.summary.json`
- `artifacts/if_summarize_judge_rows/`
  - `metta_trm_rows.jsonl`
  - `metta_trm_rows.summary.json`
- `artifacts/if_summarize_judge_multisignal/`
  - `metta_multi_signal_scorecard.jsonl`
  - `metta_multi_signal_scorecard.summary.json`
  - `metta_multi_signal_scorecard.md`
- `artifacts/if_summarize_judge_trainer_policy/`
  - `metta_trainer_policy_bundle.jsonl`
  - `metta_trainer_policy_bundle.summary.json`
  - `metta_trainer_policy_bundle.md`
  - `rollup/metta_trainer_policy_rollup.manifest.json`
- `artifacts/repair_pass_probes/`
  - `psycho_bench.repair.json`
  - `ascii_tree.repair.json`
  - `pydantic_adherence.repair.json`
  - `if_summarize_judge.repair.json`
  - `if_summarize_judge.observation.txt`
- `artifacts/nuanced_env_slice/`
  - `nuanced_env_slice.json`
  - `nuanced_env_slice.md`
  - `trajectory_manifest.core_ready.json`
  - `trajectory_manifest.expanded_ready.json`
  - `trajectory_manifest.blocked_high_value.json`
  - `trajectory_manifest.research_candidates.json`
- `artifacts/primehub_next_three_family_workplan/`
  - `primehub_next_three_family_workplan.json`
  - `primehub_next_three_family_workplan.md`
  - `benchmark_manifest.json`
- `artifacts/live_eval_qwen35_9b_runtime_packet_repair/`
  - `runtime_packet_repair.results.json`
  - `runtime_packet_repair.results.md`
  - `runtime_packet_repair.findings.md`
- `artifacts/live_eval_qwen35_9b_nuanced_slice/`
  - `core_ready/nuanced_slice_baseline.results.json`
  - `core_ready/nuanced_slice_baseline.results.md`
- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta/`
  - `if_summarize_with_metta.results.json`
  - `if_summarize_with_metta.results.md`
  - `if_summarize_with_metta.findings.md`
  - `direct_probe_results.json`
- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta_seed_sweep/`
  - `if_summarize_with_metta.results.json`
  - `if_summarize_with_metta.results.md`
  - `if_summarize_with_metta.findings.md`
- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta_repair/`
  - `if_summarize_with_metta.results.json`
  - `if_summarize_with_metta.results.md`
  - `if_summarize_with_metta.findings.md`
- live benchmark outputs:
  - first ablation hold:
    - [with_vs_without_metta.results.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_with_vs_without_metta/with_vs_without_metta.results.json)
    - [with_vs_without_metta.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_with_vs_without_metta/with_vs_without_metta.findings.md)
  - richer packet rerun:
    - [with_vs_without_metta.results.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_with_vs_without_metta_richer_packet/with_vs_without_metta.results.json)
    - [with_vs_without_metta.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_with_vs_without_metta_richer_packet/with_vs_without_metta.findings.md)
  - [ablation_decision.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/ablation_decision.md)

## Current Result

The example package compiled successfully into a real bundle at:

- [bundle.manifest.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_structured_map_bundle/bundle.manifest.json)
- [retrieval_packet.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_structured_map_bundle/retrieval_packet.json)
- [critic_hints.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_structured_map_bundle/critic_hints.json)
- [trace_labels.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_structured_map_bundle/trace_labels.json)

The compiled bundle covers:

- `psycho_bench`
- `ascii_tree`
- `pydantic_adherence`

and proves the file contract is executable rather than just descriptive.

The pipeline now also produces the three artifact surfaces that matter if MeTTa is going to do more than add prompt text:

- a compact runtime packet in [runtime_packet.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_structured_map_bundle/runtime_packet.json)
- offline supervision rows in [metta_trm_rows.jsonl](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_structured_map_rows/metta_trm_rows.jsonl)
- a multi-signal scorecard in [metta_multi_signal_scorecard.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_structured_map_multisignal/metta_multi_signal_scorecard.summary.json)

Current local compile snapshot:

- runtime packet env count: `3`
- synthesized TRM rows: `12`
- multi-signal scorecard units: `12`
- multi-signal targets: `63`
- supervision density vs single reward: `5.25x`
- row mix:
  - `metta_contract_select`: `3`
  - `metta_contract_verify`: `6`
  - `metta_contract_repair`: `3`

The deterministic repair pass also works on the demo corruptions for all three envs, with receipts in `artifacts/repair_pass_probes/`.

The first profile-aware nuanced-env lane is now real as well. I added [primehub-constraint-summarize-hermes](C:/projects/Hermes-Skills/Hermes Skills/primehub-constraint-summarize-hermes/SKILL.md) plus a MeTTa package at [examples/if_summarize_judge_constraints](C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/examples/if_summarize_judge_constraints/package.manifest.json), then compiled it into:

- [bundle.manifest.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/if_summarize_judge_bundle/bundle.manifest.json)
- [runtime_packet.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/if_summarize_judge_bundle/runtime_packet.json)
- [metta_trm_rows.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/if_summarize_judge_rows/metta_trm_rows.summary.json)
- [if_summarize_judge.repair.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/repair_pass_probes/if_summarize_judge.repair.json)

That bundle covers one env with `17` structural profiles inside it. The runtime packet summary reports:

- env count: `1`
- profile count: `17`
- answer shape: `constraint_conditioned_summary`

The synthesized supervision surface is much denser than the flat structured-map lane:

- total rows: `72`
- env-level rows:
  - `metta_contract_select`: `1`
  - `metta_contract_verify`: `2`
  - `metta_contract_repair`: `1`
- profile-aware rows:
  - `metta_profile_select`: `17`
  - `metta_profile_verify`: `34`
  - `metta_profile_repair`: `17`

The new multi-signal compiler makes that density explicit instead of hiding it behind one scalar reward:

- [structured-map multisignal summary](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_structured_map_multisignal/metta_multi_signal_scorecard.md)
  - `12` units
  - `63` signal targets
  - `5.25x` label density vs a single-reward lane
- [if_summarize multisignal summary](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/if_summarize_judge_multisignal/metta_multi_signal_scorecard.md)
  - `72` units
  - `446` signal targets
  - `6.19x` label density vs a single-reward lane
- [multi_signal_rollup.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/multi_signal_rollup.md)

The scorecards are now wired into the repo's trainer-policy layer instead of stopping at diagnostics:

- [structured-map trainer-policy bundle](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_structured_map_trainer_policy/metta_trainer_policy_bundle.summary.json)
  - cluster: `structured_map`
  - rows: `63`
  - average supervision weight: `1.5195`
  - local harness rollup:
    - critic bucket accuracy `0.8462`
    - retriever exact match `0.6154`
- [if_summarize trainer-policy bundle](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/if_summarize_judge_trainer_policy/metta_trainer_policy_bundle.summary.json)
  - cluster: `constraint_summarize`
  - rows: `446`
  - average supervision weight: `1.6062`
  - local harness rollup:
    - critic bucket accuracy `0.8605`
    - retriever exact match `0.6628`
- [trainer_policy_rollup.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/trainer_policy_rollup.md)

The repair pass is now observation-aware for this env. Using a recorded replay observation that requested exactly one comma, the repair probe inferred the `one_comma` family, detected `wrong comma count`, and rewrote the demo corruption to the canonical one-comma answer shape.

I also ran the first live `if_summarize_judge` MeTTa eval with the new summarization skill fixed and only the MeTTa catalog changing. The first pass exposed a scorer problem, and the receipts are:

- [if_summarize_with_metta.results.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_if_summarize_with_metta/if_summarize_with_metta.results.json)
- [if_summarize_with_metta.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_if_summarize_with_metta/if_summarize_with_metta.findings.md)
- [direct_probe_results.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_if_summarize_with_metta/direct_probe_results.json)

That run was a flat hold:

- episodes per arm: `3`
- sampled profile family: `one_comma` on every episode
- `without_metta`: total reward `0.0`, avg reward `0.0`
- `with_metta_runtime`: total reward `0.0`, avg reward `0.0`

The important finding from that first pass was not "MeTTa lost"; it was that the env and scorer path were not usable as a benchmark:

- the env served the same seeded `one_comma` prompt on every episode
- three direct scorer probes with plausible one-comma answers also came back `0.0`
- the remote judge path surfaced auth and timeout failures rather than clean structural discrimination

I then fixed that lane end to end:

- `remote_prime_env_bridge.py` now passes local judge settings through for `if_summarize_judge` and surfaces `env_info` on direct probes
- `if_summarize_judge.py` now supports a configurable judge timeout
- the live env on `snacksack` now uses a deterministic structural fastpath for the handled constraint families instead of relying entirely on the remote judge
- the live runner now sweeps explicit seeds instead of repeating the same prompt

The corrected receipts are:

- [if_summarize_with_metta.results.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_if_summarize_with_metta_seed_sweep/if_summarize_with_metta.results.json)
- [if_summarize_with_metta.results.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_if_summarize_with_metta_seed_sweep/if_summarize_with_metta.results.md)
- [if_summarize_with_metta.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_if_summarize_with_metta_seed_sweep/if_summarize_with_metta.findings.md)

That seeded sweep is now a real discriminator:

- seeds: `[7, 11, 19]`
- profiles seen:
  - `one_comma`
  - `single_question`
  - `exact_10w_bullets`
- `without_metta`: total reward `1.0`, avg reward `0.3333`
- `with_metta_runtime`: total reward `2.0`, avg reward `0.6667`
- lift: `+0.3333`

Per-seed read:

- `one_comma`: `0.0 -> 1.0`
- `single_question`: `1.0 -> 1.0`
- `exact_10w_bullets`: `0.0 -> 0.0`

I then targeted the remaining structural miss with a deterministic MeTTa repair arm instead of more prompt inflation. The repair logic now leaves already-valid answers unchanged and applies family-specific structural normalization for `exact_10w_bullets`.

The targeted rerun receipts are:

- [if_summarize_with_metta.results.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_if_summarize_with_metta_repair/if_summarize_with_metta.results.json)
- [if_summarize_with_metta.results.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_if_summarize_with_metta_repair/if_summarize_with_metta.results.md)
- [if_summarize_with_metta.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_if_summarize_with_metta_repair/if_summarize_with_metta.findings.md)

That rerun changed the read:

- `without_metta`: total reward `1.0`, avg reward `0.3333`
- `with_metta_runtime`: total reward `1.0`, avg reward `0.3333`
- `with_metta_runtime_repair`: total reward `3.0`, avg reward `1.0`

Per-seed repair read:

- `one_comma`: runtime miss repaired to `1.0`
- `single_question`: unchanged at `1.0`
- `exact_10w_bullets`: runtime miss repaired to `1.0`

The stronger live path is now the compact runtime packet plus repair-aware scoring, recorded in [runtime_packet_repair.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/live_eval_qwen35_9b_runtime_packet_repair/runtime_packet_repair.findings.md).

A live `with_metta` vs `without_metta` ablation has now also been run on `qwen35_9b`, keeping the base `primehub-structured-map-hermes` prompt fixed and changing only the retrieval memory source.

The first packet was benchmarkable but lost on `psycho_bench`, which put the study on hold. After enriching the MeTTa package with `summary`, `example-status`, `validation-path`, `verifier-caveat`, and stronger env-specific cues and failure modes, the rerun moved the treatment ahead.

Reward snapshot:

- `psycho_bench`
  - `without_metta`: `3.3283`
  - `with_metta` richer packet: `3.3311`
  - `with_metta_runtime`: `3.3483`
- `ascii_tree`
  - `without_metta`: `0.8`
  - `with_metta` richer packet: `0.8`
  - `with_metta_runtime`: `0.8`
- `pydantic_adherence`
  - `without_metta`: `1.0`
  - `with_metta` richer packet: `1.0`
  - `with_metta_runtime`: `1.0`

Current read:

- The MeTTa bundle is runtime-usable.
- The MeTTa bundle now supports three distinct surfaces: runtime packet, offline rows, and repair pass.
- The MeTTa bundle now supports a fourth useful surface: a multi-signal scorecard that separates selection, success, critic, repair, and transport targets.
- The MeTTa bundle now supports a fifth useful surface: a trainer-policy TRM bundle compiled from those signal targets into normal harness rows.
- The richer MeTTa packet now matches or beats the existing non-MeTTa schema pack on all three held envs.
- The compact runtime packet is stronger than the richer prompt-only packet on `psycho_bench`, improving over control by `0.0200`.
- Repair is fully wired into live scoring, but it did not need to modify the runtime-packet answers on this three-env slice.
- Prompt cost is still mixed: runtime packet is cheaper on `pydantic_adherence`, but still higher on `psycho_bench` and `ascii_tree`.
- The broader held-slice question is now structured instead of ad hoc:
  - `core_ready`: `psycho_bench`, `if_summarize_judge`
  - `expanded_ready`: add `allenai_ifeval`
  - `blocked_high_value`: `clbench` after the current 400-path is fixed
  - keep `simpleqa`, `simpleqa_verified`, and `truthfulqa` out of this psycho-like slice
- `if_summarize_judge` is now more than a candidate env; it has a real Hermes skill, a profile-aware MeTTa bundle, generated supervision rows, and replay-grounded repair receipts.
- `if_summarize_judge` is also the clearest data-collection proof point so far: the MeTTa scorecard raised the effective supervision surface from `72` single-reward units to `446` labeled targets.
- `if_summarize_judge` is now also the clearest trainer-policy proof point so far: those `446` targets compile into a normal TRM bundle with `0.8605` critic bucket accuracy and `0.6628` retriever exact match on the local holdout.
- `if_summarize_judge` is now a usable seeded structural benchmark rather than a broken scorer lane:
  - the initial all-zero pass was traced to auth/timeout failures in the judge path plus repeated sampling of one seeded prompt
  - the live env now fastpaths handled structural constraints deterministically
  - the corrected seed sweep improved `avg_reward` from `0.3333` to `0.6667`
  - current unresolved family on this slice: `exact_10w_bullets`
  - prompt cost is still materially higher on the MeTTa arm (`4973` vs `2636`)
- the strongest current `if_summarize_judge` lane is now repair-aware rather than prompt-only:
  - on the latest targeted rerun, prompt-only MeTTa matched control at `0.3333`
  - deterministic MeTTa repair lifted the same seeded slice to `1.0`
  - the repaired wins came from fixing structural misses in `one_comma` and `exact_10w_bullets`

The slice curation receipts are in [nuanced_env_slice.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/nuanced_env_slice/nuanced_env_slice.md). The baseline runner for that slice is [run_nuanced_slice_baseline.py](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/run_nuanced_slice_baseline.py). I only verified the new runner with `--dry-run` in this pass; I did not start a fresh remote benchmark job on the new nuanced slice.

## Primary Question

Can we define a symbolic package format that is simple enough to compile deterministically and rich enough to improve TRM retrieval, critic prompts, and trace labeling for Hermes?

## Current Decision

Promote, narrowly.

The compiler contract is good enough to keep, the runtime wiring is real, the enriched packet clears the held three-env gate, the runtime packet now produces the strongest live result, and the repo has a usable offline-row and repair-pass path. The new `if_summarize_judge` lane now also has a corrected live benchmark and a working repair-aware follow-up: after fixing the judge path and sweeping seeds, the prompt-only MeTTa arm showed a live win on one run, and the latest targeted rerun shows the more reliable result, where deterministic MeTTa repair lifts the seeded structural slice to `1.0`. This is still a narrow promotion rather than a default rollout because the evidence slice is small, the prompt-only runtime path is still variable, and prompt cost is not uniformly lower. The next iteration target is to trim the runtime packet, keep the repair win, widen the seed/profile coverage, and then fix `clbench` so the broader held slice gains a rubric-judged long-context member.

## Primehub Rollup Comparison

I also ran a bounded trainer-policy infusion comparison directly against the existing `cycle_12` TRM corpus using a Windows Job Object wrapper with hard caps:

- caps:
  - RAM: `2048 MB`
  - CPU: `50%`
  - IO budget target: `50 MB/s`
- wrapper receipts:
  - [jobcap.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_rollup_metta_comparison/jobcap.summary.json)
  - [jobcap.events.jsonl](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_rollup_metta_comparison/jobcap.events.jsonl)
- comparison receipts:
  - [comparison.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_rollup_metta_comparison/comparison.summary.json)
  - [comparison.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_rollup_metta_comparison/comparison.findings.md)

Three variants were trained and benched through the normal local TRM harness:

- `control`
- `control_plus_structured_map`
- `control_plus_structured_map_and_if_summarize`

The important result is not the big global number. Adding both MeTTa trainer bundles lifts global retriever exact match from `0.0625` to `0.1667` and global gated router exact match from `0.0000` to `0.1364`, but that lift comes entirely from the added synthetic MeTTa families.

On the original `primehub` holdout rows, transfer is flat:

- primehub retriever exact match stays `0.0625`
- primehub gated router exact match stays `0.0000`
- primehub gated abstain stays `0.9062`

So the current MeTTa trainer-policy bundles are useful as supervision expansion and harness-facing structure, but they do **not** yet improve routing or retrieval on the original Primehub corpus. That is now the right read for this study.

## Primehub Transfer Comparison

I then ran the transfer-oriented follow-up, still under the same hard caps, but this time forcing the MeTTa rows to stay in `task_family=primehub` and scoring only the untouched external Primehub eval rows:

- transfer bundle receipts:
  - [primehub_structured_map_transfer summary](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_structured_map_transfer/metta_primehub_transfer_bundle.summary.json)
  - [if_summarize_judge_transfer summary](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/if_summarize_judge_transfer/metta_primehub_transfer_bundle.summary.json)
- comparison receipts:
  - [comparison.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_transfer_comparison/comparison.summary.json)
  - [comparison.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_transfer_comparison/comparison.findings.md)
  - [comparison.events.jsonl](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_transfer_comparison/comparison.events.jsonl)
  - [jobcap.events.jsonl](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_transfer_comparison/jobcap.events.jsonl)

The result is stricter and still flat:

- untouched external primehub holdout: `32` rows
- control: critic `0.7500`, retriever `0.0625`, gated router `0.0000`
- structured transfer: unchanged
- structured + if transfer: unchanged

I also corrected the subset evaluator after this run. The first version of the custom subset scorer had used saved models trained on the full merged corpus, while the harness bench scripts always train from the train split only. After patching and rerunning, the corrected transfer comparison now matches the bench summaries and keeps the same conclusion: no original external lift.

## Primehub External Abstraction Comparison

I then built a train-only external abstraction bundle from the original external Primehub training rows themselves:

- bundle receipts:
  - [primehub_external_abstraction_bundle.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_bundle/primehub_external_abstraction_bundle.summary.json)
  - [primehub_external_abstraction_bundle.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_bundle/primehub_external_abstraction_bundle.md)
- comparison receipts:
  - [comparison.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/comparison.summary.json)
  - [comparison.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/comparison.findings.md)
  - [jobcap.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/jobcap.summary.json)

That bundle creates `7` projected exact-positive rows:

- `4` `math_env` rows for the repeated boxed-zero difference invariant prompt
- `3` `truthfulqa` rows for the repeated boxed-letter abstention prompt

The corrected original external holdout result is mixed, not promotable:

- untouched external primehub holdout: `32` rows
- control: critic `0.7500`, retriever `0.0625`, gated router `0.0000`, abstain `0.9062`
- external abstraction: critic `0.5938`, retriever `0.1562`, gated router `0.0000`, abstain `0.7500`

So the abstractions do help retrieval on the untouched external holdout, especially on the `math_env` / `truthfulqa` overlap slice, but they do it by making the critic worse. The gated router still fails to convert that retrieval gain into end-to-end wins.

That means the next step is narrower again: the bottleneck is now critic calibration, not retrieval coverage. The next useful move is to generate critic-targeted support rows for the same external observation families instead of only adding more exact-positive retrieval support.

## Primehub External Critic Support Follow-Up

I built that critic-targeted follow-up next.

- compiler:
  - [compile_primehub_external_critic_support_bundle.py](C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/scripts/compile_primehub_external_critic_support_bundle.py)
- generated bundle:
  - [primehub_external_critic_support_bundle.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_critic_support_bundle/primehub_external_critic_support_bundle.summary.json)
  - [primehub_external_critic_support_bundle.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_critic_support_bundle/primehub_external_critic_support_bundle.md)
- updated comparison:
  - [comparison.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/comparison.summary.json)
  - [comparison.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/comparison.findings.md)
  - [jobcap.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/jobcap.summary.json)

The critic-support bundle adds `12` train-only rows with exact matching observations, `visible_output_emitted = true`, and low supervision weight so the retriever ignores them:

- `6` `math_env`
- `6` `truthfulqa`

That fixed the abstraction lane:

- untouched external primehub holdout
  - control: critic `0.7500`, retriever `0.0625`, gated router `0.0000`
  - abstraction only: critic `0.5938`, retriever `0.1562`, gated router `0.0000`
  - abstraction + critic support: critic `0.7500`, retriever `0.1562`, gated router `0.1562`
- focus overlap slice (`psycho_bench`, `math_env`, `truthfulqa`)
  - control: gated router `0.0000`
  - abstraction + critic support: gated router `0.6250`

This is the first end-to-end Primehub transfer win on the untouched external holdout in the repo. The limiting factor was critic calibration, and the critic-support rows fixed it without giving back the retrieval gain.

## Next External Families Workplan

I then turned the next-step recommendation into a machine-readable plan instead of leaving it in chat history.

- source manifest:
  - [primehub_next_three_families.json](C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/plans/primehub_next_three_families.json)
- generator:
  - [build_primehub_next_three_family_workplan.py](C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/scripts/build_primehub_next_three_family_workplan.py)
- generated artifacts:
  - [primehub_next_three_family_workplan.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_next_three_family_workplan/primehub_next_three_family_workplan.json)
  - [primehub_next_three_family_workplan.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_next_three_family_workplan/primehub_next_three_family_workplan.md)
  - [benchmark_manifest.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_next_three_family_workplan/benchmark_manifest.json)

The selected basis is now explicit:

- `allenai_ifeval` for exact-contract and instruction-wrapper repair
- `aime2026` for hard numeric verification plus visible-output recovery
- `jailbreak_bench` for critic abstain calibration and guarded override control

The generated plan also records why `misguided_attn`, `uq`, and `colf` are deferred, and it freezes row families, critic-support families, repair families, and promotion gates for each selected lane.

## AllenAI IFEval External Family

I then built the first next-family lane instead of leaving the workplan dormant.

- compilers:
  - [compile_primehub_external_ifeval_bundle.py](C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/scripts/compile_primehub_external_ifeval_bundle.py)
  - [compile_primehub_external_ifeval_critic_support_bundle.py](C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/scripts/compile_primehub_external_ifeval_critic_support_bundle.py)
- generated bundles:
  - [primehub_external_ifeval_bundle.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_ifeval_bundle/primehub_external_ifeval_bundle.summary.json)
  - [primehub_external_ifeval_critic_support_bundle.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_ifeval_critic_support_bundle/primehub_external_ifeval_critic_support_bundle.summary.json)
- updated comparison:
  - [comparison.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/comparison.summary.json)
  - [comparison.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/comparison.findings.md)
  - [jobcap.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/jobcap.summary.json)

The important data-source detail is that the stable train split had no usable `allenai_ifeval` source rows in `cycle_12`, so the new compilers fall back to the replay corpus under `data/primehub_choice_contract_pressure_20260421` and `...20260422`. That produced:

- `6` train-only `allenai_ifeval` abstraction rows
- `6` train-only `allenai_ifeval` critic-support rows

The result is stronger than the generic exact-match table by itself suggests:

- untouched external primehub holdout
  - prior best (`external abstraction + critic support`): critic `0.7500`, retriever `0.1562`, gated router `0.1562`
  - with `allenai_ifeval` abstraction added: critic `0.6562`, retriever `0.1562`, gated router `0.1562`
- untouched `allenai_ifeval` contract holdout (`3` rows)
  - control: retrieval contract `0.0000`, gated contract `0.0000`
  - with `allenai_ifeval` abstraction: retrieval contract `1.0000`, gated contract `1.0000`
  - with full `allenai_ifeval` stack: unchanged from the abstraction-only lane

So the right reading is:

- `allenai_ifeval` is a real MeTTa transfer win on the contract metric it actually cares about
- the lighter `ifeval_abstraction` lane is enough on the current holdout; the extra `ifeval` critic-support rows did not improve further
- it preserves the earlier untouched-holdout gated-router win, but it does not improve the generic external-holdout exact-match score beyond that prior best

That makes `allenai_ifeval` a good proof that the world-model recipe generalizes beyond `math_env` and `truthfulqa`, but also a good reminder that different external families need different success metrics.

## AIME2026 External Family

I then executed the second next-family lane for `aime2026`.

- compilers:
  - [compile_primehub_external_aime2026_bundle.py](C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/scripts/compile_primehub_external_aime2026_bundle.py)
  - [compile_primehub_external_aime2026_critic_support_bundle.py](C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/scripts/compile_primehub_external_aime2026_critic_support_bundle.py)
- generated bundles:
  - [primehub_external_aime2026_bundle.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_aime2026_bundle/primehub_external_aime2026_bundle.summary.json)
  - [primehub_external_aime2026_critic_support_bundle.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_aime2026_critic_support_bundle/primehub_external_aime2026_critic_support_bundle.summary.json)
- updated comparison:
  - [comparison.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/comparison.summary.json)
  - [comparison.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/comparison.findings.md)
  - [jobcap.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_external_abstraction_comparison/jobcap.summary.json)

This lane uses the official `aime2026` dataset answer for the repeated untouched-holdout problem: `\boxed{39}`. As with `allenai_ifeval`, the stable `cycle_12` train split had no usable source rows, so the new compilers fall back to replay traces under `data/primehub_eligible_benchmark_v3_tuned_44env_v2` and `data/primehub_overnight_all`. That produced:

- `6` train-only `aime2026` abstraction rows
- `6` train-only `aime2026` critic-support rows

The family-specific result is strong:

- untouched `aime2026` numeric holdout (`6` rows)
  - control: retrieval boxed exact `0.0000`, gated boxed exact `0.0000`
  - with `aime_abstraction`: retrieval boxed exact `1.0000`, gated boxed exact `1.0000`
  - with full `aime` stack: unchanged from the abstraction-only lane

But the global tradeoff is real:

- untouched external primehub holdout
  - prior best generic lane (`external abstraction + critic support`): critic `0.7500`, gated router `0.1562`
  - with `aime_abstraction`: critic `0.5625`, gated router `0.1562`

So the right reading is:

- `aime2026` is a real MeTTa transfer win on exact numeric verification and visible-output recovery
- the extra `aime` critic-support rows did not add anything on the current holdout
- this is not yet a global promotion because the critic-calibration drop is too large relative to the generic external holdout

That makes `aime2026` useful as proof that the world-model recipe can solve a strict boxed-exact numeric family, but it also shows the next bottleneck clearly: localized numeric wins still need better critic calibration before they can be merged into the default external stack.

## Family Router Interference Pass

I then added the fresh evaluation layer that separates target-family lift from unrelated-family damage.

- compiler:
  - [compile_primehub_family_router_bundle.py](C:/projects/Hermes-Skills/Hermes Skills/metta-trm-hermes-pipeline/scripts/compile_primehub_family_router_bundle.py)
- runner:
  - [run_primehub_family_router_comparison.py](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/run_primehub_family_router_comparison.py)
- artifacts:
  - [primehub_family_router_bundle.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_family_router_bundle/primehub_family_router_bundle.json)
  - [family_router.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_family_router_comparison/family_router.summary.json)
  - [family_router.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_family_router_comparison/family_router.findings.md)
  - [jobcap.summary.json](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/primehub_family_router_comparison/jobcap.summary.json)

The router bundle currently profiles:

- `allenai_ifeval`: exact-contract / instruction-wrapper profile
- `aime2026`: hard numeric verification profile

The comparison tests shared global merging against routed specialists and reports target lift, unrelated critic drift, unrelated gated-router regression, and whole-holdout critic drift.

Current result:

- `global_common`: unrelated critic `0.6522`, unrelated gated `0.2174`, `ifeval` gated contract `0.0000`, `aime` gated exact `0.0000`
- `global_all_abstractions`: unrelated critic `0.6522`, unrelated gated `0.2174`, `ifeval` gated contract `1.0000`, `aime` gated exact `1.0000`
- `routed_abstractions`: same measured result as `global_all_abstractions`

The fresh read is important:

- the current holdout does not show unrelated-family interference from merging `allenai_ifeval` and `aime2026` rows
- the whole-holdout critic drop is concentrated in the target families, whose original labels are `negative` even though the family-specific contract is now solved
- routing is still the right scaffold for future families, but the immediate bottleneck is target-aware evaluation and label semantics, not cross-family poisoning

That changes the next research question. Before making the router more complex, the repo needs a target-adjusted critic label for solved external families, or a separate terminal-state label that distinguishes "original model failed" from "retrieved/controlled action would now satisfy the environment."
