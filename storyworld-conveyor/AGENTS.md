# AGENTS.md

## Purpose
This folder is a production-oriented Hermes Agent scaffold for a storyworld conveyor belt demo.
Hermes is the orchestrator, not the source of truth. The pipeline is CLI-first and artifact-first.

## What This Conveyor Does
- Build or ingest 80-120 encounter definitions
- Generate one or more completions per encounter
- Grade completions with deterministic environment-style metrics
- Add optional GPT-5 mini auxiliary judging
- Aggregate scores into leaderboard-style reports
- Export SFT, verifier, and critique/repair datasets

## Non-Negotiable Rules
- Never claim a stage succeeded without file paths and counts from disk.
- Every stage writes `manifest.json`, `progress.json`, and `events.jsonl`.
- Prefer rerunning one stage over restarting the whole pipeline.
- Deterministic env truth outranks LLM judge outputs.
- LLM judge output is auxiliary only and must never overwrite env metrics.

## Hermes Operational Pattern
- Use `todo` to break work into explicit stages before running anything.
- Use `delegate_task` only for independent stage subsets:
  - shard encounter building by family
  - shard completion runs by model or encounter slice
  - shard audits by failed stage directory
- Use `terminal(background=true)` for long runs such as `run-pipeline`.
- Use process polling/logging/wait to watch the job until a manifest flips to `completed` or `failed`.
- Use `schedule_cronjob` for recurring nightly or hourly batch runs.

## Canonical Commands
- Smoke test:
  - `python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py --config hermes-skills/storyworld-conveyor/sample_data/pipeline_config.json run-pipeline`
- MCP-default config from a large storyworld JSON or SWMD:
  - `python hermes-skills/storyworld-conveyor/scripts/prepare_mcp_conveyor_config.py --storyworld <world.json|world.swmd.min.md> --out-config <mcp_config.json> --max-encounters 12`
- MCP-default bounded conveyor run:
  - `python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py --config <mcp_config.json>`
- MCP budget-only check before any model load:
  - `python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py --config <mcp_config.json> --preflight-only`
- Factory config menu:
  - `python hermes-skills/storyworld-conveyor/scripts/make_factory_config.py --list-templates`
- Factory config generation:
  - `python hermes-skills/storyworld-conveyor/scripts/make_factory_config.py --template fresh_seed_artistry --base-world <world.json> --out-config <factory_config.json> --title <title> --about <about> --motif <motif>`
- Stage-only examples:
  - `python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py --config <config.json> build-encounters`
  - `python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py --config <config.json> run-completions`
  - `python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py --config <config.json> grade-env`
  - `python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py --config <config.json> judge-llm`
  - `python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py --config <config.json> aggregate`
  - `python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py --config <config.json> export-training`
- Storyworld factory smoke:
  - `python hermes-skills/storyworld-conveyor/run_storyworld_factory.py --config hermes-skills/storyworld-conveyor/sample_data/factory_smoke_config.json`
- Storyworld factory overnight:
  - `python hermes-skills/storyworld-conveyor/run_storyworld_factory.py --config hermes-skills/storyworld-conveyor/sample_data/factory_overnight_macbeth.json`
- Repeated grind loop with real tail output:
  - `python hermes-skills/storyworld-conveyor/scripts/run_factory_grind.py --config <factory_config.json> --run-id-prefix grind_demo --iterations 10 --tail-lines 6 --force`

## Factory Beats To Preserve
- Add spool structure before downstream balancing.
- Thread characters and tensions via seed retheming plus artistry pass, not giant freeform rewrites.
- Audit secret options and gated branches explicitly.
- Run the hard acceptance audit before any "ready" claim:
  - duplicate encounter/option/reaction ids
  - dangling consequences and bad spool refs
  - unreachable or zero-inbound encounters
  - terminal pages that cannot land inside their turn windows
  - reader compatibility for gated options and multi-reaction options
- Prefer more interesting effect shapes than pure additive nudges; let artistry passes diversify operator mix.
- Use Monte Carlo and path probes to decide whether rebalance passes are worth applying.
- Treat `late_stage_balance` as optional unless the target ending id is known to exist.

## How Hermes Should Report Progress Each Checkpoint
- Report the stage name, run id, status file path, and counts.
- Example:
  - `encounter_builder completed`
  - `run_id=demo3`
  - `manifest=.../sample_runs/demo3/encounter_builder/manifest.json`
  - `encounter_count=3`
- If a stage is still running, report:
  - active PID or job id
  - last log line or last event record
  - next checkpoint file to watch

## Failure Modes And Anti-Hallucination Controls
- Missing output file:
  - treat as failure even if the model says it wrote the file
- Invented config schema:
  - reject it and regenerate with `make_factory_config.py`
- Partial stage output:
  - do not continue unless `manifest.json` exists and status is `completed`
- Judge API failure:
  - preserve env-grader artifacts and rerun only `judge-llm`
- Batch interruption:
  - resume with the same `run_id`; completed stages are skipped unless `--force`
- Drift between narrative claims and artifacts:
  - trust `manifest.json`, `progress.json`, CSV, and JSONL counts only
- Brittle rebalance heuristics:
  - mark the stage failed in manifest, keep going only if it is tagged non-critical

## Token Burn Controls
- MCP is the default for any storyworld authoring or revision run larger than a smoke test.
- Never inline the full storyworld after the initial JSON-to-SWMD conversion. Use SWMD-min plus encounter MCP packets.
- Default packet contents are: world card, target encounter block, neighbor blocks, compact planning card, TRM constraints, and ledger/state summary.
- Run `prepare_mcp_conveyor_config.py` before model work when the input is a large JSON storyworld; it emits SWMD-min and a config with `mcp_default=true`.
- `run_small_model_storyworld_port.py` runs `mcp_budget_preflight` before model load by default and fails if prompt estimate or input/output ratio exceeds the config limits.
- To widen context intentionally, edit `context_budget_tokens`, `reserve_output_tokens`, `planning_card_tokens`, `neighbor_hops`, and `max_input_output_ratio` in the config. Do not bypass the preflight unless you are doing a controlled overflow experiment.
- Default smoke test is 3 encounters; demo mode is 10; batch mode is 80-120.
- Keep `llm_judge.provider=mock` unless external judging is explicitly needed.
- Shard completion runs by encounter slices or model names.
- Do not attach large raw JSONL files into chat; cite file paths and counts instead.

## Example Cron Usage
- Hourly smoke test:
  - `schedule_cronjob "python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py --config hermes-skills/storyworld-conveyor/sample_data/pipeline_config.json run-pipeline" "0 * * * *"`

## Example delegate_task Plan
- Task 1: build encounter families `scarcity` and `legitimacy`
- Task 2: run completions for model `hermes_teacher_mock`
- Task 3: audit any stage whose `manifest.json` is missing or non-completed
- Task 4: run factory-stage audit on `late_stage_balance` and `quality_gate` outputs before enabling any paid judge shard
