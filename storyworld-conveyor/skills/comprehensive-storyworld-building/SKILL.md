---
name: comprehensive-storyworld-building
category: mlops/datasets
description: End-to-end SweepWeave storyworld workflow with artifact-first Hermes execution, conveyor manifests, Monte Carlo analysis, and TRM-guided rebalance packets.
keywords: [storyworld, sweepweave, swmd, monte-carlo, conveyor, balancing, pathing, trm, hermes]
doc_type: skill
---

# Comprehensive Storyworld Building

Use this skill for full storyworld creation, analysis, revision, export, and batch orchestration.

This is the merged Hermes-facing contract for:
- high-level storyworld workflow
- conveyor-stage discipline
- artifact-first verification
- Monte Carlo and pathing analysis
- TRM-guided rebalance loops

## First Principle
Hermes is the orchestrator, not the source of truth.

Trust only:
- on-disk artifacts
- `manifest.json`
- `progress.json`
- `events.jsonl`
- validator output
- quality gate output
- Monte Carlo output
- delta audit output

Do not claim success from memory, intention, or narrative summary.

## Token Economy Default
For any non-smoke storyworld generation or revision, use MCP packets by default. Do not feed the full storyworld back through every conveyor phase.

Canonical setup:
`python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/prepare_mcp_conveyor_config.py --storyworld <world.json|world.swmd.min.md> --out-config <mcp_config.json> --max-encounters 12`

Canonical run:
`python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py --config <mcp_config.json>`

The MCP config must keep:
- `mcp_default=true`
- `mcp_budget_preflight=true`
- `memory_mode=encounter_packet_only`
- `allow_mcp_budget_overflow=false`

Each model call should receive only world card, target encounter, neighbor encounters, compact planning/TRM constraints, and any ledger summary. If `mcp_budget_preflight/budget_report.json` fails, reduce packet size before model execution.

## Canonical Files
- Conveyor AGENTS:
  - `/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/AGENTS.md`
- Conveyor runner skill:
  - `/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/skills/storyworld-conveyor-runner/SKILL.md`
- Batch auditor skill:
  - `/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/skills/storyworld-batch-auditor/SKILL.md`
- Hard acceptance audit:
  - `/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/audit_storyworld_acceptance.py`

Read only the minimal sections you need, then execute.

## Core Workflow
1. Draft creation
- `one_shot_factory.py`
- trim to target encounter count
- retheme titles/about/motif
- keep IDs stable

2. Structural validation
- `sweepweave_validator.py`
- fail immediately on invalid structure

3. Spool and path shaping
- `materialize_spools.py`
- `spool_sequencing.py`
- optional topology scaffold scripts for explicit ending/secret routing

4. Artistry and operator diversification
- `apply_artistry_pass.py`
- diversify desirability/effect operators
- increase gated visibility and effect richness

5. Pathing analysis
- `multiple_paths.py`
- `monte_carlo_rehearsal.py`
- `ending_reachability_balance.py`
- `late_stage_balance.py`
- For Macbeth-style secret endings, treat `spool_endings` as a required artifact, not an implied consequence of `connected_spools`.
- If `super_secret_reachability` stays at `0.0`, inspect the actual anchor route to `page_secret_0299` and the secret-option desirability/visibility on the epilogue anchor (`page_0087`) before assuming the graph is sound.

6. Quality gates
- `storyworld_quality_gate.py`
- env-style quality metrics outrank textual taste
- Keep desirability scripts nonconstant. A handful of constant desirability reactions can sink `desirability_nonconstant_ratio` even when validator output is clean.
- Check the quality report after any secret-route change; validator success does not imply Monte Carlo reachability.

7. Hard acceptance audit
- `audit_storyworld_acceptance.py`
- This is required before saying a storyworld is ready, excellent, validated, playable, or fixed.
- It must pass after the final world JSON is written, not before late rebalance or polishing.
- It checks duplicate ids, missing consequence targets, bad spool refs, bad bounded-number refs, unreachable encounters, zero-inbound encounters, terminal turn-window failures, and reader compatibility for gated/multi-reaction options.
- If this audit fails, do not paper over it with a narrative explanation; patch the world or the reader and rerun the audit.

8. Export and indexing
- `json_to_swmd.py`
- `swmd_encounter_index.py`
- `swmd_build_qlora_examples.py`

9. Optional batch conveyor
- `run_storyworld_conveyor.py`
- `run_storyworld_factory.py`

## Factory Mode
When running a real storyworld build, prefer the factory pipeline over freehand chat edits.

Canonical pattern:
`python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/run_storyworld_factory.py --config <factory_config.json> --run-id <run_id> --force`

Canonical config-generation pattern:
`python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/make_factory_config.py --template <template_id> --base-world <world.json> --out-config <factory_config.json> [supported flags only]`

Required loading pattern:
1. verify repo root and config path
2. if no valid config exists yet, create one with `make_factory_config.py`
3. print the exact command before running it
4. run one factory config at a time
5. print the resulting run root
6. print exact artifact paths from that run root

Supported flags for `run_storyworld_factory.py` only:
- `--config`
- `--run-root`
- `--run-id`
- `--force`
- `--stop-after`

Supported flags for `make_factory_config.py`:
- `--list-templates`
- `--template`
- `--out-config`
- `--base-world`
- `--run-id`
- `--title`
- `--about`
- `--motif`
- `--theme`
- `--genre`
- `--characters`
- `--target-encounters`
- `--ending-count`
- `--secret-ending-count`
- `--super-secret-count`
- `--avg-options`
- `--avg-reactions`
- `--avg-effects`
- `--gate-pct`
- `--mc-runs`
- `--probe-runs`
- `--include-monte-carlo`
- `--include-encounter-index`
- `--include-qlora`

Do not invent flags like:
- `--input`
- `--output`
- `--single-iteration`

If a requested behavior needs those, stop and say the script does not support them.

## Config Menu
Read the menu file when the user asks what kinds of runs are available:
- `/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/sample_data/factory_config_menu.json`

Use one of these template ids only:
- `fresh_seed_artistry`
- `balanced_secret_topology`
- `desirability_grind`

Treat these design targets as config metadata, not proof that the world meets them:
- encounter length
- character roster
- ending counts
- average options per encounter
- average reactions per option
- average effects per reaction

When tuning those targets for actual generation quality:
- push ordinary non-terminal encounters toward about 3 options on average
- keep most options broadly visible by default
- reserve stronger visibility/access gating for only a small late-story slice:
  - about 5% of total options in Act II
  - about 8% of total options in Act III
- use tight filters mainly for secret endings, payoff branches, and route-lock moments
- if the model emits many nominal options but only one is usually visible, loosen gating before adding more branches

The config is valid if:
- it is produced by `make_factory_config.py`
- the resulting JSON exists on disk
- `run_storyworld_factory.py --config <that file>` accepts it and creates a run root

If a static sample config already exists for the requested world, prefer it over inventing a new config schema.

Factory beats to preserve:
- seed draft
- validate
- materialize spools
- sequence spools
- apply artistry
- scaffold topology if needed
- validate again
- audit secret gates
- run path probe
- run Monte Carlo
- optional rebalance
- quality gate
- hard acceptance audit
- export SWMD-min
- build encounter index
- build QLoRA examples

## Required Acceptance Checks
Run these checks on the final candidate world before any readiness claim:

```bash
cd /mnt/c/projects/GPTStoryworld
python3 codex-skills/storyworld-building/scripts/sweepweave_validator.py validate <world.json>
python3 codex-skills/storyworld-building/scripts/storyworld_quality_gate.py --storyworld <world.json> --strict
python3 codex-skills/storyworld-building/scripts/monte_carlo_rehearsal.py <world.json> --runs 1000
python3 hermes-skills/storyworld-conveyor/scripts/audit_storyworld_acceptance.py \
  --storyworld <world.json> \
  --reader storyworld_reader.html \
  --out-json <audit_report.json>
```

The final handoff must include exact paths for:
- final world JSON
- validator output or command receipt
- strict quality-gate report or stdout summary
- Monte Carlo report or stdout summary
- hard acceptance audit JSON

Treat any of these as blockers:
- validator exits non-zero
- strict quality gate fails, unless the user explicitly accepts a named metric failure
- Monte Carlo produces a large `page_end_fallback` rate
- advertised endings or secrets have zero hits without an explicit design reason
- acceptance audit reports duplicate ids, unreachable or zero-inbound encounters, terminal turn-window failures, bad refs, or reader incompatibility

Do not claim a verifier score or "excellent" status unless it comes from a current artifact path generated after the final edit.

## Hermes Execution Rules
- Start with:
  - `pwd && ls -ld /mnt/c/projects/GPTStoryworld /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor`
- Use `todo` for stage planning when the session supports it.
- Use direct CLI commands, not prose.
- For long runs, use background terminal execution if available.
- Poll logs and status files instead of narrating progress from memory.
- Resume by reusing the same `run_id`.
- Filesystem and process truth must come from terminal commands or real factory manifests.
- Do not use `execute_code`, Python snippets, or sandbox path checks for conveyor tasks.
- Do not create ad hoc directories like `working_worlds/` unless the user explicitly requested that path.

## Hard Rules
- Do not say `done` unless the relevant `manifest.json` says `completed`.
- If an output file is missing, the stage failed.
- If `manifest.json` is missing, the stage failed.
- If a stage returns non-zero and is not marked `continue_on_failure`, stop.
- Never overwrite deterministic env truth with LLM judge outputs.
- Never trust a base world just because its title looks correct; scan its actual character ids and internal state.
- After the first checkpoint, do not reread repo docs unless editing them.
- Do not replace the requested command with a different multi-command plan.
- If the user says `do`, execute the next real terminal command immediately.
- If terminal execution is unavailable in the session, say exactly `NO_TERMINAL_EXECUTION` and stop.

## Anti-Hallucination Controls
- File write claims require:
  - exact path
  - file size or line count
  - validator or stage output
- Readiness claims require:
  - strict quality gate receipt
  - Monte Carlo receipt
  - hard acceptance audit receipt
- Loop completion claims require:
  - candidate artifact root
  - delta audit output
- If the base world is semantically contaminated, stop and report that before further balancing.
- If stdout contains echoed commands instead of command output, do not present that as execution.
- Do not fabricate JSON wrappers like `{ "exit_status": 0, ... }` unless that exact JSON came from a real tool.

## Base World Resolution
There are only two valid seed modes:

1. Existing base world file
- Example:
  - `/mnt/c/projects/GPTStoryworld/storyworlds/by-week/2026-W11/validated_macbeth.json`
- Use:
  - `one_shot_factory.py`

2. Fresh brief slug
- Example:
  - `fresh:the_usual_suspects`
- Use:
  - `fresh_storyworld_seed.py`

Do not pass `fresh:<slug>` into `one_shot_factory.py`.
Do not invent a local file like `working_worlds/<slug>_base.json` unless that file already exists on disk and has been verified with `ls`.

Canonical fresh-seed shape:

```bash
python3 /mnt/c/projects/GPTStoryworld/codex-skills/storyworld-building/scripts/fresh_storyworld_seed.py \
  --slug <slug> \
  --out <seed_world.json> \
  --target-encounters <N> \
  --title <title> \
  --about <about> \
  --motif <motif>
```

## Delta Audit
Canonical command:
`python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/audit_macbeth_loop.py --baseline-run /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/macbeth_patch_test --candidate-run /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/macbeth_loop_N --out-json <loop_dir>/delta_report.json --out-txt <loop_dir>/delta_brief.txt`

Trust the delta brief over memory.

## TRM Rebalance Packet
If present, read the packet before planning edits.

Canonical command:
`python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/trm_storyworld_rebalance.py --base-config <base_factory_config.json> --factory-runs-root /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs --log-root /mnt/d/Research_Engine/Hermes-experiment-logs/storyworld-conveyor --out-advice <loop_dir>/trm_rebalance_advice.json --out-config <loop_dir>/factory_loop_config.json`

Use the emitted patched config unless current artifacts prove it stale or aimed at the wrong world.

## Suggested Session Pattern
1. Verify workspace and config paths
2. If needed, list templates from the config menu or `make_factory_config.py --list-templates`
3. Create a config with `make_factory_config.py` using only supported flags
4. Read only the current brief, config, and any delta/TRM packet
5. Print the exact factory command using only supported flags
6. Run factory or stage subset
7. Inspect manifests and reports
8. Make one targeted revision if needed
9. Rerun the minimal validating subset
10. Emit exact artifact paths

## Precise Run Dynamic
Use this exact shell shape:

```bash
pwd && ls -ld /mnt/c/projects/GPTStoryworld /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor
cd /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor
python3 scripts/make_factory_config.py --template <template_id> --base-world <world.json> --out-config <factory_config.json> [supported flags only]
python3 run_storyworld_factory.py --config <factory_config.json> --run-id <run_id> --force
```

If the base world starts with `fresh:`, inspect the generated config before running and confirm that the `seed_world` stage uses `fresh_storyworld_seed.py`, not `one_shot_factory.py`.

Then inspect only these files before making claims:
- `<run_root>/<run_id>/<stage>/manifest.json`
- `<run_root>/<run_id>/<stage>/progress.json`
- `<run_root>/<run_id>/reports/*.json`
- `<run_root>/<run_id>/worlds/*.json`

If a world is produced outside the factory run root, run the Required Acceptance Checks directly on that world path before handoff.

If asked to "tail the flow", tail real logs only:
- `<run_root>/<run_id>/<stage>/stdout.log`
- `<run_root>/<run_id>/<stage>/stderr.log`

If asked to grind through dozens of loops, use the real grind script:
`python3 /mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/scripts/run_factory_grind.py --config <factory_config.json> --run-id-prefix <prefix> --iterations <N> --tail-lines 6 --force`

Do not simulate an 80-turn conveyor loop in chat unless `run_factory_grind.py` or another real script is being used.

## What Not To Do
- Do not improvise a new workflow in chat
- Do not claim writes from sandbox paths like `/home/user/...`
- Do not summarize unchanged reports for multiple turns
- Do not continue polishing a poisoned base world
- Do not use `execute_code` for filesystem, config, or factory execution
- Do not invent `working_worlds/...` or other unsourced base-world paths
- Do not invent stage names such as `build_encounters` or `export_json` for the storyworld factory
