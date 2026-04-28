# MeTTa TRM Hermes Pipeline

This folder is the concrete bridge from symbolic MeTTa contracts to TRM infusion artifacts for Hermes skills.

## Why This Exists

Hermes skills already have:

- base answer contracts
- TRM overlays
- study packets

What is missing is a symbolic compiler layer that can define the task rules once and then emit:

- compact runtime packets
- critic and verifier hints
- trace labels
- training rows and negatives
- deterministic repair logic

MeTTa is a good fit for that symbolic layer because it can hold:

- env-specific constraints
- output schemas
- validator facts
- failure modes
- repair hints
- routing cues
- profile-specific structural families inside one env

## Folder Layout

```text
metta-trm-hermes-pipeline/
  SKILL.md
  README.md
  package_contract.md
  plans/
    primehub_next_three_families.json
  scripts/
    compile_metta_package.py
    compile_metta_runtime_packet.py
    compile_metta_rows.py
    metta_multi_signal_scorecard.py
    compile_metta_trainer_policy_bundle.py
    run_metta_trainer_policy_rollup.py
    metta_repair_pass.py
    build_primehub_next_three_family_workplan.py
  examples/
    primehub_structured_map/
      package.manifest.json
      package.metta
      contracts.metta
      retrieval_policy.metta
      failure_modes.metta
      examples/
        minimal_valid.json
    if_summarize_judge_constraints/
      package.manifest.json
      package.metta
      contracts.metta
      retrieval_policy.metta
      profiles.metta
      failure_modes.metta
```

## Compiler Outputs

The base bundle compiler emits:

- `bundle.manifest.json`
- `atoms.json`
- `retrieval_packet.json`
- `critic_hints.json`
- `trace_labels.json`
- `artifact_contract.json`
- `compiler_summary.md`

Then the follow-on scripts emit:

- `runtime_packet.json`
  - compact runtime packet for Hermes prompt injection
- `metta_trm_rows.jsonl`
  - deterministic TRM supervision rows synthesized from the symbolic contract
- `metta_multi_signal_scorecard.jsonl`
  - multi-signal TRM scorecard units with separate selection, success, critic, repair, and transport labels
- `metta_trainer_policy_bundle.jsonl`
  - standard TRM train rows compiled from the multi-signal scorecard through the repo's trainer-policy weights
- repair pass reports or repaired outputs
  - deterministic env-specific cleanup for strict-format answers

## Intended Integration

`MeTTa package -> rich bundle -> compact runtime packet + offline rows + repair pass -> Hermes runtime / study`

That means:

- the MeTTa package is the research source
- the rich bundle is the symbolic truth-preserving slice
- the runtime packet is the prompt-facing slice
- the TRM rows are the training-facing slice
- the repair pass is the post-generation contract-enforcement slice
- the study packet records whether the symbolic layer actually helped

## Example Command

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_package.py" `
  "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\examples\primehub_structured_map" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_runtime_packet.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_rows.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_rows"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\metta_multi_signal_scorecard.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_multisignal"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_trainer_policy_bundle.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle" `
  --scorecard-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_multisignal" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_trainer_policy"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\run_metta_trainer_policy_rollup.py" `
  --input "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_trainer_policy\metta_trainer_policy_bundle.jsonl" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_trainer_policy\rollup"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\metta_repair_pass.py" `
  --bundle-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_structured_map_bundle" `
  --env-id pydantic_adherence `
  --use-demo-corruption `
  --emit-report

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\compile_metta_package.py" `
  "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\examples\if_summarize_judge_constraints" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\if_summarize_judge_bundle"

python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\scripts\build_primehub_next_three_family_workplan.py" `
  --source "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-hermes-pipeline\plans\primehub_next_three_families.json" `
  --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_next_three_family_workplan"
```
