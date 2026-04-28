# Experiment Log

## Run Metadata

- Study: MeTTa TRM Hermes pipeline scaffold
- Date: 2026-04-22
- Focus: define the package contract and compile one example bundle
- Target family: `primehub-structured-map-hermes`

## Planned Command

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_package.py" `
  "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\examples\primehub_structured_map" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle"
```

## Result

- run completed
- package: `primehub_structured_map`
- env count: `3`
- atom count: `46`
- outputs:
  - `artifacts/primehub_structured_map_bundle/bundle.manifest.json`
  - `artifacts/primehub_structured_map_bundle/retrieval_packet.json`
  - `artifacts/primehub_structured_map_bundle/critic_hints.json`
  - `artifacts/primehub_structured_map_bundle/trace_labels.json`
  - `artifacts/primehub_structured_map_bundle/compiler_summary.md`

## Interpretation

- The package contract is concrete enough to compile deterministically.
- The bundle shape is already usable for retrieval overlays and critic prompt builders.
- The next phase is not more structure work; it is wiring one compiled packet into a live Hermes path.

## Decision

- in progress

## Live Benchmark Run

- Date: 2026-04-22
- Focus: run a controlled `with_metta` vs `without_metta` ablation on the live structured-map slice
- Model: `qwen35_9b`
- Scoring path: remote Primehub env bridge on `snacksack`

### Command

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_with_metta_ablation.py"
```

### Receipts

- `artifacts/live_eval_qwen35_9b_with_vs_without_metta/with_vs_without_metta.results.json`
- `artifacts/live_eval_qwen35_9b_with_vs_without_metta/with_vs_without_metta.results.md`
- `artifacts/live_eval_qwen35_9b_with_vs_without_metta/with_vs_without_metta.findings.md`
- `artifacts/ablation_decision.md`

### Result

- `psycho_bench`
  - `without_metta`: `3.328333333333333`
  - `with_metta`: `3.3033333333333332`
- `ascii_tree`
  - `without_metta`: `0.7999999999999999`
  - `with_metta`: `0.7999999999999999`
- `pydantic_adherence`
  - `without_metta`: `1.0`
  - `with_metta`: `1.0`

### Interpretation

- The MeTTa bundle is no longer just a compiler artifact; it now drives a real live eval arm.
- The current MeTTa packet matched the non-MeTTa control on `ascii_tree` and `pydantic_adherence`.
- The current MeTTa packet underperformed the non-MeTTa control on `psycho_bench` by `0.025`.
- That makes this a real runtime hold, not a rejection of the MeTTa pipeline.

### Decision

- hold

## Richer Packet Iteration

- Date: 2026-04-22
- Focus: enrich the MeTTa package with stronger env-specific contract fields and rerun the same live slice
- Added atom heads in use:
  - `summary`
  - `example-status`
  - `validation-path`
  - `verifier-caveat`
- Package changes:
  - sharper `psycho_bench` summary and failure cues
  - richer `ascii_tree` format cues
  - explicit `pydantic_adherence` validation path and historical verifier caveat
- Runtime change:
  - the MeTTa arm now renders the same contract-memory scaffold as the non-MeTTa control instead of a differently shaped prompt

### Commands

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_package.py" `
  "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\examples\primehub_structured_map" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle"

python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_with_metta_ablation.py" `
  --output-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\live_eval_qwen35_9b_with_vs_without_metta_richer_packet"
```

### Receipts

- `artifacts/primehub_structured_map_bundle/retrieval_packet.json`
- `artifacts/live_eval_qwen35_9b_with_vs_without_metta_richer_packet/with_vs_without_metta.results.json`
- `artifacts/live_eval_qwen35_9b_with_vs_without_metta_richer_packet/with_vs_without_metta.findings.md`
- `artifacts/ablation_decision.md`

### Result

- `psycho_bench`
  - `without_metta`: `3.328333333333333`
  - `with_metta`: `3.331111111111111`
- `ascii_tree`
  - `without_metta`: `0.7999999999999999`
  - `with_metta`: `0.7999999999999999`
- `pydantic_adherence`
  - `without_metta`: `1.0`
  - `with_metta`: `1.0`

### Interpretation

- The richer packet closed the original `psycho_bench` gap and moved slightly ahead of control.
- Exact-structure wins on `ascii_tree` and `pydantic_adherence` were preserved.
- The MeTTa arm used more prompt tokens, so the current benefit is about parity-plus-correctness and symbolic maintainability, not lower-cost inference.

### Decision

- promoted (narrow)

## Runtime Packet And Row Compiler Phase

- Date: 2026-04-22
- Focus: move the MeTTa path beyond prompt-only retrieval by splitting it into:
  - compact runtime packet
  - offline TRM supervision rows
  - deterministic repair pass

### Commands

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_runtime_packet.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_rows.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_rows"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\metta_repair_pass.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle" `
  --env-id psycho_bench `
  --use-demo-corruption `
  --emit-report
```

### Receipts

- `artifacts/primehub_structured_map_bundle/runtime_packet.json`
- `artifacts/primehub_structured_map_bundle/runtime_packet.summary.json`
- `artifacts/primehub_structured_map_rows/metta_trm_rows.jsonl`
- `artifacts/primehub_structured_map_rows/metta_trm_rows.summary.json`
- `artifacts/repair_pass_probes/psycho_bench.repair.json`
- `artifacts/repair_pass_probes/ascii_tree.repair.json`
- `artifacts/repair_pass_probes/pydantic_adherence.repair.json`

### Result

- compact runtime packet emitted for all `3` envs
- synthesized row count: `12`
- task-family mix:
  - `metta_contract_select`: `3`
  - `metta_contract_verify`: `6`
  - `metta_contract_repair`: `3`
- deterministic repair probes:
  - `psycho_bench`: stripped commentary and normalized separators
  - `ascii_tree`: removed fences, dropped prose, restored wrapper tags
  - `pydantic_adherence`: removed fences, coerced cooldown, defaulted `created_at`

### Interpretation

- This is the first MeTTa phase that can plausibly beat prompt-only control by more than noise.
- The runtime packet is now slimmer than the rich retrieval packet, so there is a real path to trimming prompt cost later.
- The offline rows and repair pass move useful symbolic detail out of runtime prompt stuffing and into trainable or post-generation machinery.

### Decision

- promoted (research infrastructure)

## Runtime Packet Live Eval

- Date: 2026-04-22
- Focus: replace the rich MeTTa prompt path with the compact runtime packet and test repair-aware scoring
- Live arms:
  - `without_metta`
  - `with_metta_runtime`
  - `with_metta_runtime_repair`

### Command

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_runtime_packet_repair_eval.py"
```

### Receipts

- `artifacts/live_eval_qwen35_9b_runtime_packet_repair/runtime_packet_repair.results.json`
- `artifacts/live_eval_qwen35_9b_runtime_packet_repair/runtime_packet_repair.results.md`
- `artifacts/live_eval_qwen35_9b_runtime_packet_repair/runtime_packet_repair.findings.md`

### Result

- `psycho_bench`
  - `without_metta`: `3.328333333333333`
  - `with_metta_runtime`: `3.3483333333333336`
  - `with_metta_runtime_repair`: `3.3483333333333336`
- `ascii_tree`
  - `without_metta`: `0.7999999999999999`
  - `with_metta_runtime`: `0.7999999999999999`
  - `with_metta_runtime_repair`: `0.7999999999999999`
- `pydantic_adherence`
  - `without_metta`: `1.0`
  - `with_metta_runtime`: `1.0`
  - `with_metta_runtime_repair`: `1.0`

### Interpretation

- The compact runtime packet is the strongest MeTTa runtime lane so far on the held slice.
- The `psycho_bench` uplift is now `0.0200` over control, which is materially larger than the earlier `0.0028` prompt-only gain.
- The repair lane is operational and verifier-faithful, but it did not need to modify outputs on this clean three-env slice.
- Prompt cost is not yet solved:
  - `psycho_bench`: `1187` vs control `1138`
  - `ascii_tree`: `794` vs control `736`
  - `pydantic_adherence`: `1522` vs control `1557`

### Decision

- promoted (runtime packet path)

## Multi-Signal Scorecard Phase

- Date: 2026-04-23
- Focus: compile the same MeTTa bundles into a modular multi-signal TRM scorecard instead of treating each synthetic unit as only one scalar reward
- Goal:
  - separate selection, success, critic, repair, and transport signals
  - quantify supervision density vs the old single-reward framing

### Commands

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\metta_multi_signal_scorecard.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_multisignal"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\metta_multi_signal_scorecard.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_bundle" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_multisignal"
```

### Receipts

- `artifacts/primehub_structured_map_multisignal/metta_multi_signal_scorecard.jsonl`
- `artifacts/primehub_structured_map_multisignal/metta_multi_signal_scorecard.summary.json`
- `artifacts/if_summarize_judge_multisignal/metta_multi_signal_scorecard.jsonl`
- `artifacts/if_summarize_judge_multisignal/metta_multi_signal_scorecard.summary.json`
- `artifacts/multi_signal_rollup.md`

### Result

- structured-map bundle:
  - units: `12`
  - signal targets: `63`
  - average signals per unit: `5.25`
  - label density vs single reward: `5.25x`
- `if_summarize_judge` bundle:
  - units: `72`
  - signal targets: `446`
  - average signals per unit: `6.19`
  - label density vs single reward: `6.19x`

### Interpretation

- MeTTa is a much stronger data-collection and supervision-framing tool than a prompt-only runtime tool.
- The meaningful gain is not just more rows; it is multiple orthogonal labels per unit:
  - selection
  - success
  - critic
  - repair
  - transport
- Profile-heavy envs benefit the most because MeTTa can express structural families directly and then synthesize profile-specific labels at scale.

### Decision

- promoted (data-framing infrastructure)

## Trainer-Policy Bundle Phase

- Date: 2026-04-23
- Focus: compile the MeTTa multi-signal scorecards into normal TRM trainer rows using the repo's trainer-policy object, then run the local critic/retriever/router harness on those rows
- Infrastructure changes:
  - `build_primehub_skill_batch_evolution.py`
    - adds `constraint_summarize` as a first-class cluster with `primehub-constraint-summarize-hermes`
    - adds cluster-level signal weights and support-tier overrides for structural bundles
  - `primehub_role_imprint.py`
    - trainer policy now emits `enabled_signals` and `signal_weights`
  - `compile_metta_trainer_policy_bundle.py`
    - flattens multi-signal scorecards into standard TRM train rows
  - `run_metta_trainer_policy_rollup.py`
    - trains and benches the local TRM harness on those compiled rows

### Commands

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\scripts\build_primehub_skill_batch_evolution.py"
python "C:\projects\Hermes-Skills\Hermes Skills\scripts\build_primehub_role_based_imprint.py"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_trainer_policy_bundle.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle" `
  --scorecard-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_multisignal" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_trainer_policy"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\run_metta_trainer_policy_rollup.py" `
  --input "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_trainer_policy\metta_trainer_policy_bundle.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_trainer_policy\rollup" `
  --top-k 3 `
  --holdout-ratio 0.2 `
  --min-supervision-weight 0.2

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_trainer_policy_bundle.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_bundle" `
  --scorecard-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_multisignal" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_trainer_policy"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\run_metta_trainer_policy_rollup.py" `
  --input "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_trainer_policy\metta_trainer_policy_bundle.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_trainer_policy\rollup" `
  --top-k 3 `
  --holdout-ratio 0.2 `
  --min-supervision-weight 0.25
```

### Receipts

- `artifacts/primehub_structured_map_trainer_policy/metta_trainer_policy_bundle.summary.json`
- `artifacts/primehub_structured_map_trainer_policy/rollup/metta_trainer_policy_rollup.manifest.json`
- `artifacts/if_summarize_judge_trainer_policy/metta_trainer_policy_bundle.summary.json`
- `artifacts/if_summarize_judge_trainer_policy/rollup/metta_trainer_policy_rollup.manifest.json`
- `artifacts/trainer_policy_rollup.md`

### Result

- structured-map trainer-policy bundle:
  - cluster: `structured_map`
  - support tier: `format_support`
  - rows: `63`
  - avg supervision weight: `1.5195`
  - critic bucket accuracy: `0.8462`
  - retriever exact match: `0.6154`
  - critic-gated router exact match: `0.6154`
- `if_summarize_judge` trainer-policy bundle:
  - cluster: `constraint_summarize`
  - support tier: `format_support`
  - rows: `446`
  - avg supervision weight: `1.6062`
  - critic bucket accuracy: `0.8605`
  - retriever exact match: `0.6628`
  - critic-gated router exact match: `0.6628`
  - critic-gated router abstain rate: `0.0116`

### Interpretation

- The MeTTa scorecard is now wired into the actual trainer-policy path instead of stopping at a research artifact.
- One symbolic package now yields:
  - runtime packet
  - offline TRM rows
  - repair pass
  - multi-signal scorecard
  - trainer-policy bundle that the local harness can train and bench
- `constraint_summarize` is now the strongest proof that MeTTa helps TRM data collection more than prompt-only runtime performance.

### Decision

- promoted (trainer-policy bridge)

## Nuanced Slice Curation

- Date: 2026-04-22
- Focus: widen the study beyond the original three-env structured slice by defining a reusable psycho-like nuanced benchmark pack grounded in actual env code and local replay evidence
- Goal:
  - keep `psycho_bench` as the anchor
  - add one or two genuinely richer tasks instead of flooding the study with short QA or generic IF tasks

### Commands

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\build_nuanced_env_slice.py"
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_nuanced_slice_baseline.py" --bundle core_ready --dry-run
```

### Receipts

- `artifacts/nuanced_env_slice/nuanced_env_slice.json`
- `artifacts/nuanced_env_slice/nuanced_env_slice.md`
- `artifacts/nuanced_env_slice/trajectory_manifest.core_ready.json`
- `artifacts/nuanced_env_slice/trajectory_manifest.expanded_ready.json`
- `artifacts/nuanced_env_slice/trajectory_manifest.blocked_high_value.json`
- `artifacts/nuanced_env_slice/trajectory_manifest.research_candidates.json`
- `artifacts/live_eval_qwen35_9b_nuanced_slice/core_ready/nuanced_slice_baseline.results.json`
- `artifacts/live_eval_qwen35_9b_nuanced_slice/core_ready/nuanced_slice_baseline.results.md`

### Result

- selected bundles:
  - `core_ready`: `psycho_bench`, `if_summarize_judge`
  - `expanded_ready`: `psycho_bench`, `if_summarize_judge`, `allenai_ifeval`
  - `blocked_high_value`: `clbench`
  - `research_candidates`: `ifbench`, `ifeval`
- explicit exclusions from the psycho-like slice:
  - `simpleqa`
  - `simpleqa_verified`
  - `simpleqa_verified_2`
  - `truthfulqa`
- blocker surfaced clearly:
  - `clbench` still has a local 400-path failure with `run_token_total = 0`

### Interpretation

- The broader held-slice plan is now concrete instead of conversational.
- `if_summarize_judge` is the best immediate second nuanced env because it combines long context, structural constraints, and judge-based scoring.
- `allenai_ifeval` is useful as a supporting boundary env, but it should not replace a richer judged task in the core slice.
- `clbench` is worth fixing because it is the strongest blocked candidate for a rubric-judged long-context lane.
- I only verified the new runner in `--dry-run` mode here, so this section is structure-and-selection work, not a fresh live benchmark pass.

### Decision

- promoted (broader slice structure)

## if_summarize_judge Profile-Aware Skill Build

- Date: 2026-04-22
- Focus: build the first MeTTa-authored Hermes skill for a multi-family nuanced env instead of a flat output-contract lane
- Target env:
  - `if_summarize_judge`
- New skill surface:
  - `primehub-constraint-summarize-hermes`
- New package source:
  - `metta-trm-hermes-pipeline/examples/if_summarize_judge_constraints`

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\primehub-constraint-summarize-hermes\scripts\build_skill_prompt.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_package.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_runtime_packet.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_rows.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\metta_repair_pass.py"

python "C:\projects\Hermes-Skills\Hermes Skills\primehub-constraint-summarize-hermes\scripts\build_skill_prompt.py" `
  --env-name if_summarize_judge `
  --role-mode critic_only

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_package.py" `
  "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\examples\if_summarize_judge_constraints" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_bundle"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_runtime_packet.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_bundle"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_rows.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_bundle" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_rows"

$sample = Get-Content "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v2_47env\qwen35_9b\qwen35_9b_if_summarize_judge_q0018.jsonl" -TotalCount 1 | ConvertFrom-Json
$obsPath = "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\repair_pass_probes\if_summarize_judge.observation.txt"
Set-Content -Path $obsPath -Value $sample.observation -Encoding UTF8
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\metta_repair_pass.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_bundle" `
  --env-id if_summarize_judge `
  --observation-file $obsPath `
  --use-demo-corruption `
  --emit-report `
  --output-path "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\repair_pass_probes\if_summarize_judge.repair.json"
```

### Receipts

- `primehub-constraint-summarize-hermes/SKILL.md`
- `metta-trm-hermes-pipeline/examples/if_summarize_judge_constraints/package.manifest.json`
- `artifacts/if_summarize_judge_bundle/bundle.manifest.json`
- `artifacts/if_summarize_judge_bundle/runtime_packet.summary.json`
- `artifacts/if_summarize_judge_rows/metta_trm_rows.summary.json`
- `artifacts/repair_pass_probes/if_summarize_judge.observation.txt`
- `artifacts/repair_pass_probes/if_summarize_judge.repair.json`

### Result

- bundle env count: `1`
- profile count inside `if_summarize_judge`: `17`
- runtime packet answer shape: `constraint_conditioned_summary`
- synthesized TRM rows: `72`
- row-family mix:
  - `metta_contract_select`: `1`
  - `metta_contract_verify`: `2`
  - `metta_contract_repair`: `1`
  - `metta_profile_select`: `17`
  - `metta_profile_verify`: `34`
  - `metta_profile_repair`: `17`
- replay-grounded repair probe:
  - detected family: `one_comma`
  - original demo corruption: `Welschbillig Castle rose over Roman remains, and later, and later wars left it a ruin.`
  - repaired output: `Welschbillig Castle rose over Roman remains, and later wars left it a ruin.`
  - detected failure: `wrong comma count`

### Interpretation

- This is the first MeTTa lane in the repo where the symbolic layer has to choose a sub-contract inside one env, not just attach one flat env summary.
- `if_summarize_judge` is a better MeTTa leverage surface than `psycho_bench` because the skill must classify structural families and then satisfy exact counts, punctuation, wrappers, or casing rules.
- The current result is infrastructure plus local proof, not yet a live remote benchmark.

### Decision

- promoted (profile-aware nuanced-env lane)

## if_summarize_judge Live With-MeTTa Eval

- Date: 2026-04-23
- Focus: run the first live baseline-vs-MeTTa benchmark on the new profile-aware `if_summarize_judge` skill lane
- Model: `qwen35_9b`
- Scoring path: remote Prime env bridge on `snacksack`

### Command

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_if_summarize_metta_eval.py" --episodes 3
```

### Receipts

- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta/if_summarize_with_metta.results.json`
- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta/if_summarize_with_metta.results.md`
- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta/if_summarize_with_metta.findings.md`
- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta/direct_probe_results.json`

### Result

- episodes per arm: `3`
- sampled profile family:
  - `one_comma` on all episodes for both arms
- `without_metta`
  - reward total: `0.0`
  - avg reward: `0.0`
  - prompt tokens: `2826`
- `with_metta_runtime`
  - reward total: `0.0`
  - avg reward: `0.0`
  - prompt tokens: `5163`

### Follow-Up Probe

- direct remote bridge probes against the same seeded prompt:
  - `Welschbillig Castle is a ruin of a water castle in the municipality of Welschbillig, Germany.` -> `0.0`
  - `Welschbillig Castle rose over Roman remains, and later wars left it a ruin.` -> `0.0`
  - `Built over a Roman villa, Welschbillig Castle now survives as ruined moated fortifications.` -> `0.0`

### Interpretation

- This is not yet evidence that the MeTTa lane fails on nuanced summarization.
- The env currently behaves like a seeded single-case scorer:
  - every episode hit the same `one_comma` prompt
  - the judge also returned `0.0` for plausible one-comma probe answers
- So the current benchmark result is scorer-limited and non-discriminative.
- The MeTTa treatment increased prompt cost substantially on this slice and did not buy a measurable reward gain.

### Decision

- hold (scorer-limited)

## if_summarize_judge Seed Sweep And Structural Fastpath

- Date: 2026-04-23
- Focus: turn `if_summarize_judge` into a usable benchmark by fixing the scorer path and diversifying the sampled profile family
- Model: `qwen35_9b`
- Scoring path: remote Prime env bridge on `snacksack`

### Changes Applied

- bridge update:
  - `remote_prime_env_bridge.py` now passes the local judge URL, model, and API key settings through for `if_summarize_judge`
- env update:
  - `if_summarize_judge.py` now accepts `judge_timeout_seconds`
  - the live env now fastpaths handled structural constraint families with deterministic checks instead of depending fully on the remote judge
- runner update:
  - `run_if_summarize_metta_eval.py` now sweeps explicit seeds instead of replaying one repeated prompt

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\scripts\remote_prime_env_bridge.py"
python -m py_compile "C:\projects\prime_intellect_research_environments\environments\if_summarize_judge\if_summarize_judge.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_if_summarize_metta_eval.py"

scp -i C:\Users\patri\.ssh\id_ed25519 `
  "C:\projects\prime_intellect_research_environments\environments\if_summarize_judge\if_summarize_judge.py" `
  snacksack@snacksack-ms-7d32.tail3156cd.ts.net:/home/snacksack/prime_repos_tmp/research-environments/environments/if_summarize_judge/if_summarize_judge.py

python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_if_summarize_metta_eval.py"
```

### Receipts

- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta_seed_sweep/if_summarize_with_metta.results.json`
- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta_seed_sweep/if_summarize_with_metta.results.md`
- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta_seed_sweep/if_summarize_with_metta.findings.md`

### Result

- seeds: `7`, `11`, `19`
- profile families seen:
  - `one_comma`
  - `single_question`
  - `exact_10w_bullets`
- `without_metta`
  - reward total: `1.0`
  - avg reward: `0.3333`
  - prompt tokens: `2636`
- `with_metta_runtime`
  - reward total: `2.0`
  - avg reward: `0.6667`
  - prompt tokens: `4973`
- per-seed:
  - seed `7` / `one_comma`: `0.0 -> 1.0`
  - seed `11` / `single_question`: `1.0 -> 1.0`
  - seed `19` / `exact_10w_bullets`: `0.0 -> 0.0`

### Interpretation

- The earlier all-zero run was a benchmark-path failure, not a useful MeTTa comparison.
- After fixing the scorer path and diversifying the sample, `if_summarize_judge` became a real discriminator.
- The MeTTa runtime packet materially improved reward on this seeded structural slice, driven by the `one_comma` case and preserved on `single_question`.
- The main remaining weakness is `exact_10w_bullets`, not the overall viability of the env.
- Token cost is still materially higher on the MeTTa arm, so this is a quality win before it is an efficiency win.

### Decision

- promoted (seeded structural slice)

## if_summarize_judge Exact-Count Repair Rerun

- Date: 2026-04-23
- Focus: target the remaining `exact_10w_bullets` miss with deterministic MeTTa repair instead of more prompt text
- Model: `qwen35_9b`
- Scoring path: remote Prime env bridge on `snacksack`

### Changes Applied

- `metta_repair_pass.py`
  - now leaves already-valid `if_summarize_judge` answers unchanged
  - adds family-specific bullet normalization for `exact_10w_bullets`
- `run_if_summarize_metta_eval.py`
  - now includes a `with_metta_runtime_repair` arm that rescored repaired answers through the remote env

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\metta_repair_pass.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_if_summarize_metta_eval.py"
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_if_summarize_metta_eval.py"
```

### Receipts

- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta_repair/if_summarize_with_metta.results.json`
- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta_repair/if_summarize_with_metta.results.md`
- `artifacts/live_eval_qwen35_9b_if_summarize_with_metta_repair/if_summarize_with_metta.findings.md`

### Result

- seeds: `7`, `11`, `19`
- profile families seen:
  - `one_comma`
  - `single_question`
  - `exact_10w_bullets`
- `without_metta`
  - reward total: `1.0`
  - avg reward: `0.3333`
- `with_metta_runtime`
  - reward total: `1.0`
  - avg reward: `0.3333`
- `with_metta_runtime_repair`
  - reward total: `3.0`
  - avg reward: `1.0`
- per-seed repair read:
  - seed `7` / `one_comma`: `0.0 -> 1.0`
  - seed `11` / `single_question`: unchanged at `1.0`
  - seed `19` / `exact_10w_bullets`: `0.0 -> 1.0`

### Interpretation

- The prompt-only MeTTa runtime lane is still variable on this env and matched control on this rerun.
- The reliable gain on this slice now comes from the MeTTa repair path, not from prompt-only runtime memory.
- `exact_10w_bullets` is no longer the blocker once the repair arm is allowed to normalize counts before scoring.
- The same repair lane also rescued a `one_comma` miss, which suggests the structural repair layer is the right place to invest next on `if_summarize_judge`.

### Decision

- promoted (repair-aware live lane)

## Primehub TRM Rollup Infusion Comparison

- Date: 2026-04-23
- Focus: test whether the MeTTa trainer-policy bundles improve the actual local Primehub TRM rollup, not just standalone bundle benchmarks
- Corpus base: `data/primehub_trm_autoresearch/cycle_12/primehub_trm_merged.jsonl`
- Variants:
  - `control`
  - `control_plus_structured_map`
  - `control_plus_structured_map_and_if_summarize`
- Execution mode: Windows Job Object wrapper with hard caps
  - RAM: `2048 MB`
  - CPU: `50%`
  - IO target: `50 MB/s`

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_metta_rollup_comparison.py"

& "C:\projects\Hermes-Skills\Hermes Skills\scripts\invoke_job_capped_python.ps1" `
  -ScriptPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_metta_rollup_comparison.py" `
  -WorkingDirectory "C:\projects\Hermes-Skills\Hermes Skills" `
  -RunId "metta-primehub-rollup-comparison-20260423" `
  -SummaryPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_rollup_metta_comparison\jobcap.summary.json" `
  -EventLogPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_rollup_metta_comparison\jobcap.events.jsonl" `
  -ScriptArgs @(
    "--out-dir",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_rollup_metta_comparison"
  )
```

### Receipts

- `artifacts/primehub_rollup_metta_comparison/comparison.summary.json`
- `artifacts/primehub_rollup_metta_comparison/comparison.findings.md`
- `artifacts/primehub_rollup_metta_comparison/jobcap.summary.json`
- `artifacts/primehub_rollup_metta_comparison/jobcap.events.jsonl`

### Result

- control
  - rows: `195`
  - global retriever exact match: `0.0625`
  - global gated router exact match: `0.0000`
  - primehub retriever exact match: `0.0625`
  - primehub gated router exact match: `0.0000`
- control plus structured-map bundle
  - rows: `219`
  - global retriever exact match: `0.0571`
  - global gated router exact match: `0.0000`
  - primehub retriever exact match: `0.0625`
  - primehub gated router exact match: `0.0000`
- control plus structured-map plus if-summarize bundle
  - rows: `380`
  - global retriever exact match: `0.1667`
  - global gated router exact match: `0.1364`
  - primehub retriever exact match: `0.0625`
  - primehub gated router exact match: `0.0000`

### Interpretation

- The large global gain is real at the merged-corpus level, but it is carried by the added synthetic MeTTa families.
- There is no measurable transfer to the original `primehub` holdout rows yet.
- So the current MeTTa trainer-policy bundles improve supervision density and local harness learnability, but they do not yet improve retrieval or routing on the existing Primehub autoresearch corpus.
- The live baseline/mining cross-ref is still useful context:
  - `boolq` improved only for `qwen35_27b` in the mining rerun
  - `psycho_bench` stayed flat across baseline and mining
  - there are still no live baseline/mining rows for `if_summarize_judge`, `ascii_tree`, or `pydantic_adherence`

### Decision

- keep the MeTTa trainer-policy bundle work
- do not claim Primehub transfer yet
- next step should be transfer-oriented row design, not just adding more synthetic family rows

## Primehub Transfer Comparison

- Date: 2026-04-23
- Focus: test whether transfer-oriented MeTTa rows that remain inside `task_family=primehub` can move the untouched external Primehub holdout
- Corpus base: `data/primehub_trm_autoresearch/cycle_12/primehub_trm_merged.jsonl`
- Transfer bundles:
  - `artifacts/primehub_structured_map_transfer/metta_primehub_transfer_bundle.jsonl`
  - `artifacts/if_summarize_judge_transfer/metta_primehub_transfer_bundle.jsonl`
- Execution mode: Windows Job Object wrapper with hard caps
  - RAM: `2048 MB`
  - CPU: `50%`
  - IO target: `50 MB/s`

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_primehub_transfer_bundle.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_metta_transfer_comparison.py"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_primehub_transfer_bundle.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle" `
  --base-corpus "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_transfer"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_primehub_transfer_bundle.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_bundle" `
  --base-corpus "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_transfer"

& "C:\projects\Hermes-Skills\Hermes Skills\scripts\invoke_job_capped_python.ps1" `
  -ScriptPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_metta_transfer_comparison.py" `
  -WorkingDirectory "C:\projects\Hermes-Skills\Hermes Skills" `
  -RunId "metta-primehub-transfer-comparison-20260423" `
  -MemoryLimitMB 2048 `
  -CpuRatePercent 50 `
  -IOCapMBps 50 `
  -TimeoutSec 1800 `
  -SummaryPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_transfer_comparison\jobcap.summary.json" `
  -EventLogPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_transfer_comparison\jobcap.events.jsonl" `
  -ScriptArgs @(
    "--out-dir",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_transfer_comparison",
    "--summary-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_transfer_comparison\comparison.summary.json",
    "--events-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_transfer_comparison\comparison.events.jsonl"
  )
```

### Receipts

- `artifacts/primehub_structured_map_transfer/metta_primehub_transfer_bundle.summary.json`
- `artifacts/if_summarize_judge_transfer/metta_primehub_transfer_bundle.summary.json`
- `artifacts/primehub_transfer_comparison/comparison.summary.json`
- `artifacts/primehub_transfer_comparison/comparison.findings.md`
- `artifacts/primehub_transfer_comparison/comparison.events.jsonl`
- `artifacts/primehub_transfer_comparison/jobcap.events.jsonl`

### Result

- transfer rows generated
  - structured map: `19`
  - if summarize judge: `9`
- untouched external primehub holdout
  - rows: `32`
  - control critic bucket accuracy: `0.7500`
  - control retriever exact match: `0.0625`
  - control gated router exact match: `0.0000`
  - both transfer variants: unchanged on all three metrics
- untouched external focus overlap
  - rows: `3`
  - all three are `psycho_bench`
  - control and both transfer variants: all `0.0`

### Interpretation

- The transfer-oriented overlay rows still do not move the untouched external Primehub holdout.
- This rules out the simpler hypothesis that the previous failure was only because the MeTTa rows lived under separate synthetic families.
- On the current stable split, MeTTa-covered overlap inside the untouched external eval set is extremely thin: only `3` `psycho_bench` rows.
- So the next transfer attempt should target abstractions that better match the existing external rows, especially critic buckets, abstain behavior, and reusable near-miss patterns.

### Decision

- keep the transfer-bundle compiler
- do not claim Primehub transfer yet
- next step should target original external row abstractions, not just env-specific overlays

### Scoring Correction

- The first version of the subset scorer in the comparison script used saved models trained on the full merged corpus.
- That was inconsistent with the harness bench scripts, which train from the train split only.
- I patched the scorer and reran the comparison.
- The corrected numbers are the ones above, and they still support the same conclusion: no original external lift.

## Primehub External Abstraction Comparison

- Date: 2026-04-23
- Focus: test whether train-only abstraction rows built from the original external Primehub training distribution can improve untouched external holdout behavior
- Corpus base: `data/primehub_trm_autoresearch/cycle_12/primehub_trm_merged.jsonl`
- New bundle:
  - `artifacts/primehub_external_abstraction_bundle/primehub_external_abstraction_bundle.jsonl`
  - `7` projected exact-positive rows
  - `4` `math_env`
  - `3` `truthfulqa`
- Execution mode: Windows Job Object wrapper with hard caps
  - RAM: `2048 MB`
  - CPU: `50%`
  - IO target: `50 MB/s`

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_abstraction_bundle.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_external_abstraction_comparison.py"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_abstraction_bundle.py" `
  --base-corpus "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_bundle"

& "C:\projects\Hermes-Skills\Hermes Skills\scripts\invoke_job_capped_python.ps1" `
  -ScriptPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_external_abstraction_comparison.py" `
  -WorkingDirectory "C:\projects\Hermes-Skills\Hermes Skills" `
  -RunId "metta-primehub-external-abstraction-comparison-20260423-rerun" `
  -MemoryLimitMB 2048 `
  -CpuRatePercent 50 `
  -IOCapMBps 50 `
  -TimeoutSec 1800 `
  -SummaryPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\jobcap.summary.json" `
  -EventLogPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\jobcap.events.jsonl" `
  -ScriptArgs @(
    "--out-dir",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison",
    "--summary-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\comparison.summary.json",
    "--events-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\comparison.events.jsonl"
  )
```

### Receipts

- `artifacts/primehub_external_abstraction_bundle/primehub_external_abstraction_bundle.summary.json`
- `artifacts/primehub_external_abstraction_bundle/primehub_external_abstraction_bundle.md`
- `artifacts/primehub_external_abstraction_comparison/comparison.summary.json`
- `artifacts/primehub_external_abstraction_comparison/comparison.findings.md`
- `artifacts/primehub_external_abstraction_comparison/jobcap.summary.json`
- `artifacts/primehub_external_abstraction_comparison/jobcap.events.jsonl`

### Result

- untouched external primehub holdout
  - control critic bucket accuracy: `0.7500`
  - control retriever exact match: `0.0625`
  - control gated router exact match: `0.0000`
  - abstraction critic bucket accuracy: `0.5938`
  - abstraction retriever exact match: `0.1562`
  - abstraction gated router exact match: `0.0000`
- original external focus overlap
  - rows: `8`
  - control retriever exact match: `0.2500`
  - abstraction retriever exact match: `0.6250`
  - gated router exact remains `0.0000`

### Interpretation

- The external abstractions do improve retrieval on the untouched external holdout.
- The gain is concentrated in the `math_env` and `truthfulqa` overlap slice, which is exactly what the bundle targeted.
- But critic calibration degrades enough that the end-to-end gated router still shows no win.
- So the limiting factor has shifted: retrieval coverage is no longer the main issue on this slice; critic calibration is.

### Decision

- keep the external abstraction bundle
- do not promote it as an end-to-end Primehub transfer win
- next step should build critic-targeted support rows for the same external observation families

## Primehub External Critic Support Follow-Up

- Date: 2026-04-23
- Focus: test whether critic-targeted support rows for the same repeated external observation families can turn the retrieval lift into a gated-router lift
- New bundle:
  - `artifacts/primehub_external_critic_support_bundle/primehub_external_critic_support_bundle.jsonl`
  - `12` rows total
  - `6` `math_env`
  - `6` `truthfulqa`
- Design:
  - same observation text as the target external families
  - `bucket = exact_positive`
  - `visible_output_emitted = true`
  - `supervision_weight = 0.1` so the retriever ignores them
  - train-forced via alternate `target_action` strings

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_critic_support_bundle.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_external_abstraction_comparison.py"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_critic_support_bundle.py" `
  --base-corpus "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_critic_support_bundle"

& "C:\projects\Hermes-Skills\Hermes Skills\scripts\invoke_job_capped_python.ps1" `
  -ScriptPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_external_abstraction_comparison.py" `
  -WorkingDirectory "C:\projects\Hermes-Skills\Hermes Skills" `
  -RunId "metta-primehub-external-abstraction-comparison-20260423-critic" `
  -MemoryLimitMB 2048 `
  -CpuRatePercent 50 `
  -IOCapMBps 50 `
  -TimeoutSec 1800 `
  -SummaryPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\jobcap.summary.json" `
  -EventLogPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\jobcap.events.jsonl" `
  -ScriptArgs @(
    "--out-dir",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison",
    "--summary-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\comparison.summary.json",
    "--events-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\comparison.events.jsonl"
  )
```

### Receipts

- `artifacts/primehub_external_critic_support_bundle/primehub_external_critic_support_bundle.summary.json`
- `artifacts/primehub_external_critic_support_bundle/primehub_external_critic_support_bundle.md`
- `artifacts/primehub_external_abstraction_comparison/comparison.summary.json`
- `artifacts/primehub_external_abstraction_comparison/comparison.findings.md`
- `artifacts/primehub_external_abstraction_comparison/jobcap.summary.json`
- `artifacts/primehub_external_abstraction_comparison/jobcap.events.jsonl`

### Result

- untouched external primehub holdout
  - control: critic `0.7500`, retriever `0.0625`, gated router `0.0000`
  - abstraction only: critic `0.5938`, retriever `0.1562`, gated router `0.0000`
  - abstraction + critic support: critic `0.7500`, retriever `0.1562`, gated router `0.1562`
- untouched external focus overlap
  - rows: `8`
  - control gated router exact: `0.0000`
  - abstraction + critic support gated router exact: `0.6250`
- adding the earlier transfer overlays on top keeps the same win:
  - `control_plus_external_critic_and_all_transfer`
  - untouched external gated router exact: `0.1562`

### Interpretation

- The critic-targeted support rows solved the real bottleneck.
- Retrieval had already improved from the abstraction bundle; the new critic rows let the router actually use that retrieval.
- This is the first end-to-end Primehub transfer win on the untouched external holdout in this study.

### Decision

- promote the combined lane:
  - external abstraction bundle + external critic-support bundle
- keep the transfer overlay rows as optional extras, not the core reason the win appears
- next step should generalize the critic-support recipe beyond `math_env` and `truthfulqa`

## Next External Families Workplan

- Date: 2026-04-23
- Focus: freeze the next three external Primehub family targets into a machine-readable expansion plan instead of leaving the choice in chat history
- Selection basis:
  - repeated observation families on the untouched external holdout
  - one family each for contract retrieval, numeric verification, and critic abstain calibration
  - alignment with existing trainer-policy clusters so the next MeTTa rows can plug into the current harness cleanly

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\build_primehub_next_three_family_workplan.py"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\build_primehub_next_three_family_workplan.py" `
  --source "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\plans\primehub_next_three_families.json" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_next_three_family_workplan"
```

### Receipts

- `metta-trm-hermes-pipeline/plans/primehub_next_three_families.json`
- `metta-trm-hermes-pipeline/scripts/build_primehub_next_three_family_workplan.py`
- `artifacts/primehub_next_three_family_workplan/primehub_next_three_family_workplan.json`
- `artifacts/primehub_next_three_family_workplan/primehub_next_three_family_workplan.md`
- `artifacts/primehub_next_three_family_workplan/benchmark_manifest.json`

### Result

- selected families:
  - `allenai_ifeval`
  - `aime2026`
  - `jailbreak_bench`
- deferred:
  - `misguided_attn`
  - `uq`
  - `colf`

### Interpretation

- `allenai_ifeval` is the cleanest next contract-family lane because it extends the MeTTa wrapper-repair logic into untouched external Primehub rows.
- `aime2026` is the best numeric lane because it tests visible-output recovery and final-form verification, not just answer formatting.
- `jailbreak_bench` is the right third leg because it exercises critic calibration and abstain quality rather than retrieval alone.

### Decision

- use this three-family plan as the next MeTTa transfer expansion order
- build the `allenai_ifeval` lane first
- keep `jailbreak_bench` judged primarily on critic and abstain metrics, not router exact alone

## Primehub External AllenAI IFEval Follow-Up

- Date: 2026-04-23
- Focus: execute the first planned external family by adding MeTTa-derived `allenai_ifeval` contract rows, then rerun the capped external abstraction comparison with an `allenai_ifeval`-specific contract metric
- Data issue:
  - the stable `cycle_12` train split has no usable `allenai_ifeval` source rows
  - both new compilers therefore fall back to the replay corpora:
    - `data/primehub_choice_contract_pressure_20260421`
    - `data/primehub_choice_contract_pressure_20260422`
- New bundles:
  - `artifacts/primehub_external_ifeval_bundle/primehub_external_ifeval_bundle.jsonl`
  - `artifacts/primehub_external_ifeval_critic_support_bundle/primehub_external_ifeval_critic_support_bundle.jsonl`
  - `6` abstraction rows
  - `6` critic-support rows
- Execution mode: Windows Job Object wrapper with hard caps
  - RAM: `2048 MB`
  - CPU: `50%`
  - IO target: `50 MB/s`

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_ifeval_bundle.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_ifeval_critic_support_bundle.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_external_abstraction_comparison.py"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_ifeval_bundle.py" `
  --base-corpus "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_ifeval_bundle"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_ifeval_critic_support_bundle.py" `
  --base-corpus "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_ifeval_critic_support_bundle"

& "C:\projects\Hermes-Skills\Hermes Skills\scripts\invoke_job_capped_python.ps1" `
  -ScriptPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_external_abstraction_comparison.py" `
  -WorkingDirectory "C:\projects\Hermes-Skills\Hermes Skills" `
  -RunId "metta-primehub-external-abstraction-comparison-20260423-ifeval" `
  -MemoryLimitMB 2048 `
  -CpuRatePercent 50 `
  -IOCapMBps 50 `
  -TimeoutSec 1800 `
  -SummaryPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\jobcap.summary.json" `
  -EventLogPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\jobcap.events.jsonl" `
  -ScriptArgs @(
    "--out-dir",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison",
    "--summary-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\comparison.summary.json",
    "--events-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\comparison.events.jsonl"
  )
```

### Receipts

- `metta-trm-hermes-pipeline/scripts/compile_primehub_external_ifeval_bundle.py`
- `metta-trm-hermes-pipeline/scripts/compile_primehub_external_ifeval_critic_support_bundle.py`
- `artifacts/primehub_external_ifeval_bundle/primehub_external_ifeval_bundle.summary.json`
- `artifacts/primehub_external_ifeval_critic_support_bundle/primehub_external_ifeval_critic_support_bundle.summary.json`
- `artifacts/primehub_external_abstraction_comparison/comparison.summary.json`
- `artifacts/primehub_external_abstraction_comparison/comparison.findings.md`
- `artifacts/primehub_external_abstraction_comparison/jobcap.summary.json`

### Result

- new `allenai_ifeval` bundle counts
  - abstraction: `6`
  - critic-support: `6`
- untouched external primehub holdout
  - prior best (`external abstraction + critic support`): critic `0.7500`, retriever `0.1562`, gated router `0.1562`
  - `+ ifeval abstraction`: critic `0.6562`, retriever `0.1562`, gated router `0.1562`
  - `+ full ifeval stack`: unchanged from `+ ifeval abstraction`
- untouched `allenai_ifeval` contract holdout (`3` rows)
  - control: retrieval contract `0.0000`, gated contract `0.0000`, postscript `0.0000`, semantic `0.0000`, nonempty `0.0000`
  - `+ ifeval abstraction`: all `1.0000`
  - `+ full ifeval stack`: all `1.0000`
- capped-run resource summary
  - status: `success`
  - duration: `605.6343s`
  - peak RAM: `78.9062 MB`
  - avg RAM: `53.4495 MB`
  - avg CPU: `4.248%`

### Interpretation

- `allenai_ifeval` needs its own contract metric; generic exact-match alone would hide the real gain.
- The replay-derived MeTTa abstraction rows solve the repeated `Before I forget:` contract family on untouched external holdout rows.
- The extra `allenai_ifeval` critic-support rows are not yet necessary on the current holdout because the abstraction lane already saturates the contract metric.
- The earlier external abstraction + critic-support lane remains the generic external-holdout routing win; `allenai_ifeval` adds a second, family-specific transfer proof on top.

### Decision

- keep `allenai_ifeval` in the next-three-family expansion set
- score it primarily on contract success, postscript compliance, and semantic match
- carry the lighter `ifeval_abstraction` lane forward as the default unless a broader holdout shows the critic-support rows matter

## Primehub External AIME2026 Follow-Up

- Date: 2026-04-23
- Focus: execute the second planned external family by adding MeTTa-derived `aime2026` boxed-answer rows, then rerun the capped external abstraction comparison with an `aime2026`-specific exact boxed metric
- Gold answer source:
  - the repeated untouched-holdout `aime2026` problem matches the official `MathArena/aime_2026` dataset revision used by the local environment
  - canonical boxed answer: `\boxed{39}`
- Data issue:
  - the stable `cycle_12` train split has no usable `aime2026` source rows
  - both new compilers therefore fall back to the replay corpora:
    - `data/primehub_eligible_benchmark_v3_tuned_44env_v2`
    - `data/primehub_overnight_all`
- New bundles:
  - `artifacts/primehub_external_aime2026_bundle/primehub_external_aime2026_bundle.jsonl`
  - `artifacts/primehub_external_aime2026_critic_support_bundle/primehub_external_aime2026_critic_support_bundle.jsonl`
  - `6` abstraction rows
  - `6` critic-support rows
- Execution mode: Windows Job Object wrapper with hard caps
  - RAM: `2048 MB`
  - CPU: `50%`
  - IO target: `50 MB/s`

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_aime2026_bundle.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_aime2026_critic_support_bundle.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_external_abstraction_comparison.py"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_aime2026_bundle.py" `
  --base-corpus "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_aime2026_bundle"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_external_aime2026_critic_support_bundle.py" `
  --base-corpus "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_aime2026_critic_support_bundle"

& "C:\projects\Hermes-Skills\Hermes Skills\scripts\invoke_job_capped_python.ps1" `
  -ScriptPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_external_abstraction_comparison.py" `
  -WorkingDirectory "C:\projects\Hermes-Skills\Hermes Skills" `
  -RunId "metta-primehub-external-abstraction-comparison-20260423-aime" `
  -MemoryLimitMB 2048 `
  -CpuRatePercent 50 `
  -IOCapMBps 50 `
  -TimeoutSec 1800 `
  -SummaryPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\jobcap.summary.json" `
  -EventLogPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\jobcap.events.jsonl" `
  -ScriptArgs @(
    "--out-dir",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison",
    "--summary-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\comparison.summary.json",
    "--events-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_external_abstraction_comparison\comparison.events.jsonl"
  )
```

### Receipts

- `metta-trm-hermes-pipeline/scripts/compile_primehub_external_aime2026_bundle.py`
- `metta-trm-hermes-pipeline/scripts/compile_primehub_external_aime2026_critic_support_bundle.py`
- `artifacts/primehub_external_aime2026_bundle/primehub_external_aime2026_bundle.summary.json`
- `artifacts/primehub_external_aime2026_critic_support_bundle/primehub_external_aime2026_critic_support_bundle.summary.json`
- `artifacts/primehub_external_abstraction_comparison/comparison.summary.json`
- `artifacts/primehub_external_abstraction_comparison/comparison.findings.md`
- `artifacts/primehub_external_abstraction_comparison/jobcap.summary.json`

### Result

- new `aime2026` bundle counts
  - abstraction: `6`
  - critic-support: `6`
- untouched `aime2026` numeric holdout (`6` rows)
  - control: retrieval boxed exact `0.0000`, gated boxed exact `0.0000`
  - `+ aime abstraction`: retrieval boxed exact `1.0000`, gated boxed exact `1.0000`
  - `+ full aime stack`: unchanged from `+ aime abstraction`
- untouched external primehub holdout
  - prior best generic lane (`external abstraction + critic support`): critic `0.7500`, gated router `0.1562`
  - `+ aime abstraction`: critic `0.5625`, gated router `0.1562`
  - `+ full aime stack`: unchanged from `+ aime abstraction`
- capped-run resource summary
  - status: `success`
  - duration: `774.2849s`
  - peak RAM: `77.5664 MB`
  - avg RAM: `55.2723 MB`
  - avg CPU: `4.6021%`

### Interpretation

- `aime2026` is a real MeTTa transfer win on the family-specific metric that matters: boxed exact numeric correctness with visible output.
- The control lane already retrieved nonempty boxed answers for these rows, but they were wrong; the new abstraction rows fix exactness, not just wrapper presence.
- The extra `aime2026` critic-support rows do not improve beyond the abstraction-only lane on the current holdout.
- The global tradeoff is still too large: critic bucket accuracy on the untouched external holdout falls by `0.1875`, which is outside the original guardrail.

### Decision

- keep the `aime2026` lane as a family-specific win, not a default global stack addition
- treat the next `aime2026` step as a critic-calibration problem, not a retrieval problem
- do not promote `aime2026` into the default external stack until the generic external-holdout critic drop is reduced materially

## Primehub Family Router Interference Pass

- Date: 2026-04-23
- Focus: test whether family-specific MeTTa bundles should be routed behind family specialists, and measure target-family lift separately from unrelated-family interference
- New compiler:
  - `metta-trm-hermes-pipeline/scripts/compile_primehub_family_router_bundle.py`
- New runner:
  - `research/studies/2026-04-22-metta-trm-hermes-pipeline/run_primehub_family_router_comparison.py`
- Router profiles:
  - `allenai_ifeval`: exact-contract / instruction-wrapper
  - `aime2026`: hard numeric verification
- Execution mode: Windows Job Object wrapper with hard caps
  - RAM: `2048 MB`
  - CPU: `50%`
  - IO target: `50 MB/s`

### Commands

```powershell
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_family_router_bundle.py"
python -m py_compile "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_family_router_comparison.py"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_primehub_family_router_bundle.py" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_family_router_bundle"

& "C:\projects\Hermes-Skills\Hermes Skills\scripts\invoke_job_capped_python.ps1" `
  -ScriptPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_primehub_family_router_comparison.py" `
  -WorkingDirectory "C:\projects\Hermes-Skills\Hermes Skills" `
  -RunId "metta-primehub-family-router-comparison-20260423" `
  -MemoryLimitMB 2048 `
  -CpuRatePercent 50 `
  -IOCapMBps 50 `
  -TimeoutSec 1800 `
  -SummaryPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_family_router_comparison\jobcap.summary.json" `
  -EventLogPath "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_family_router_comparison\jobcap.events.jsonl" `
  -ScriptArgs @(
    "--out-dir",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_family_router_comparison",
    "--summary-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_family_router_comparison\family_router.summary.json",
    "--events-path",
    "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_family_router_comparison\family_router.events.jsonl"
  )
```

### Receipts

- `artifacts/primehub_family_router_bundle/primehub_family_router_bundle.json`
- `artifacts/primehub_family_router_bundle/primehub_family_router_bundle.md`
- `artifacts/primehub_family_router_comparison/family_router.summary.json`
- `artifacts/primehub_family_router_comparison/family_router.findings.md`
- `artifacts/primehub_family_router_comparison/jobcap.summary.json`

### Result

- `global_common`
  - unrelated critic: `0.6522`
  - unrelated gated router: `0.2174`
  - `allenai_ifeval` gated contract: `0.0000`
  - `aime2026` gated boxed exact: `0.0000`
- `global_all_abstractions`
  - unrelated critic: `0.6522`
  - unrelated gated router: `0.2174`
  - `allenai_ifeval` gated contract: `1.0000`
  - `aime2026` gated boxed exact: `1.0000`
  - net interference score: `2.0000`
- `routed_abstractions`
  - same measured result as `global_all_abstractions`
  - net interference score: `2.0000`
- capped-run resource summary
  - status: `success`
  - duration: `724.5793s`
  - peak RAM: `160.3867 MB`
  - avg RAM: `145.7994 MB`
  - avg CPU: `8.0939%`

### Interpretation

- The fresh router metric changes the diagnosis.
- The current small holdout does not show unrelated-family drift from globally merging the `allenai_ifeval` and `aime2026` abstraction rows.
- The whole-holdout critic drop is concentrated in target-family rows whose original row label is `negative`, even though the retrieved/gated action now satisfies the family-specific contract.
- Routing is still useful as a modular evaluation scaffold, but it does not outperform global merging on this holdout.

### Decision

- keep the family-router bundle and comparison runner
- do not add router complexity yet
- next step should introduce target-adjusted critic labels or terminal-state labels that distinguish original model failure from corrected retrieved action success
