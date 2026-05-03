---
name: storyworld-conveyor-runner
description: Run the storyworld conveyor belt safely with Hermes using artifact-first stage execution, manifests, background jobs, and checkpoint reporting.
---

# Storyworld Conveyor Runner

Use this skill when Hermes needs to run the storyworld conveyor in a controlled, resumable way.

## Workflow
1. Read `AGENTS.md` in this folder first.
2. Create a `todo` list with the target stages.
3. Start from the smallest viable run:
   - smoke: 3 encounters
   - demo: 10 encounters
   - batch: 80-120 encounters
4. Use direct CLI commands, never narrative claims.
5. After each stage, inspect:
   - `manifest.json`
   - `progress.json`
   - output JSONL row count
6. If a previous loop produced a `delta_brief.txt`, read that instead of rereading repo docs at length.
7. If the loop includes `trm_rebalance_advice.json`, read it before planning edits and treat it as the default rebalance packet unless current run artifacts disprove it.

## Canonical Command
`python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py --config hermes-skills/storyworld-conveyor/sample_data/pipeline_config.json run-pipeline`

## Storyworld Factory Mode
When the user wants real storyworld production rather than generic encounter scoring, run:
`python hermes-skills/storyworld-conveyor/run_storyworld_factory.py --config hermes-skills/storyworld-conveyor/sample_data/factory_overnight_macbeth.json`

Factory beats to respect:
- seed draft
- materialize and sequence spools
- apply artistry for richer desirability/effect structure
- audit secret gates
- probe path diversity
- Monte Carlo rehearsal
- hard acceptance audit with `scripts/audit_storyworld_acceptance.py`
- optional rebalance passes
- SWMD-min export and encounter indexing

## MCP-Default Conveyor Mode
Use this mode by default when the task involves a large storyworld, multi-stage generation, revision, or "conveyor" work. The goal is to avoid repeating the whole world in every model call.

1. Prepare a bounded config:
`python hermes-skills/storyworld-conveyor/scripts/prepare_mcp_conveyor_config.py --storyworld <world.json|world.swmd.min.md> --out-config <mcp_config.json> --max-encounters 12`

2. Run the MCP-bounded port:
`python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py --config <mcp_config.json>`

Optional budget-only check before model load:
`python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py --config <mcp_config.json> --preflight-only`

3. Inspect these artifacts before reporting success:
- `<run_dir>/build_encounter_index/manifest.json`
- `<run_dir>/mcp_budget_preflight/budget_report.json`
- `<run_dir>/phase_pipeline/manifest.json`
- `<run_dir>/reports/phase_events.jsonl`
- `<run_dir>/summary.json`

MCP packet contract:
- include world card, one target encounter, neighbor encounters, planning card, TRM constraints, and compact state/ledger only
- never inline the whole JSON/SWMD in a phase prompt after conversion/indexing
- fail rather than continue when `mcp_budget_preflight` reports overflow
- lower `neighbor_hops`, `max_encounters`, or `planning_card_tokens` before raising context limits
- keep `apply=false` until parse stability and budget telemetry are clean

## 4GB Small-Model Port
When the user is working with Qwen 2B class models on about 4GB VRAM, prefer the bounded context port instead of whole-world evaluation or immediate adapter training:

`python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py --config hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port.json`

Rules for this mode:
- treat `*.swmd.min.md` as the working source
- keep revision scope to encounter packets, neighbors, planning card, and optional TRM packet
- default `apply=false` until parse stability is proven
- prefer `summary` or `none` memory over full accumulated diary
- do not escalate to QLoRA until the bounded MCP loop produces stable parse and better text

## Hermes-Native Execution
- Long run:
  - use `terminal(background=true)` to launch `run-pipeline`
- Observability:
  - use process polling/logging/wait
- Resume:
  - rerun the same command with the same `run_id`
- Sharding:
  - use `delegate_task` only for independent subsets

## Hard Rules
- Do not say `done` unless a stage manifest says `completed`.
- Do not say a storyworld is ready unless validator, strict quality gate, Monte Carlo, and hard acceptance audit have been run against the final world path.
- Do not overwrite env truth with judge outputs.
- Do not run `judge-llm` against 80-120 encounters until the 10-encounter smoke path is clean.
- If `manifest.json` is missing, treat the stage as failed.
- For overnight factory runs, non-critical rebalance failures may be tolerated only when the manifest records `failed` and later stages still emit artifacts.
- A loop is a no-op failure if metrics and ending distribution are unchanged from baseline.
- After the first checkpoint, do not reread `AGENTS.md` or `SKILL.md` unless you are editing them.
- Every overnight loop must make at least one concrete file edit or explicitly stop as no-op with delta-auditor evidence.

## Delta Audit
Canonical command:
`python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/audit_macbeth_loop.py --baseline-run /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/macbeth_patch_test --candidate-run /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/macbeth_loop_N --out-json <loop_dir>/delta_report.json --out-txt <loop_dir>/delta_brief.txt`

Trust the delta brief over your own memory of prior loops.

## TRM Rebalance Packet
Canonical command:
`python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/trm_storyworld_rebalance.py --base-config /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/sample_data/factory_overnight_macbeth.json --factory-runs-root /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs --log-root /mnt/d/Research_Engine/Hermes-experiment-logs/storyworld-conveyor --out-advice <loop_dir>/trm_rebalance_advice.json --out-config <loop_dir>/factory_overnight_macbeth_loop.json`

Use the emitted patched config for the loop factory run unless the current artifacts prove the advice packet stale.
