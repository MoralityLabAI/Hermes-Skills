---
name: moral-quandary-storyworld-building
category: mlops/datasets
description: Build and audit 20-encounter moral constitution storyworlds with explicit non-secret endings and routing probes.
keywords: [storyworld, morality, constitution, endings, routing, open-manifold, hermes]
doc_type: skill
---

# Moral Quandary Storyworld Building

Use this skill for short-arc moral constitution worlds.

This is the Hermes port of the Codex moral-quandary workflow. It is not a secret-endings skill.

## Contract
- 20 non-terminal moral encounters
- 12 explicit non-secret endings
- intended pacing near 7-9 turns
- open final-turn ending competition
- no secret-ending mechanic by default

## First Principle
Trust only:
- on-disk storyworld JSON
- validator output
- routing probe receipts
- batch summary JSON
- stage manifests and logs if using the conveyor wrapper

Do not claim a moral world exists unless the file path and probe output exist.

## Canonical Files
- Codex source skill:
  - `/mnt/c/projects/GPTStoryworld/codex-skills/moral-quandary-storyworlds/SKILL.md`
- Generator:
  - `/mnt/c/projects/GPTStoryworld/tools/gen_morality_constitution_batch.py`
- Compatibility wrapper:
  - `/mnt/c/projects/GPTStoryworld/codex-skills/moral-quandary-storyworlds/scripts/generate_drama.py`
- Routing probe:
  - `/mnt/c/projects/GPTStoryworld/tools/probe_morality_batch_routing.py`
- Pair-world seed generator:
  - `/mnt/c/projects/GPTStoryworld/tools/gen_morality_pair_worlds.py`
- Pair-world revision pass:
  - `/mnt/c/projects/GPTStoryworld/tools/revise_morality_pair_worlds_v2.py`
- 3D ending-matrix pass:
  - `/mnt/c/projects/GPTStoryworld/tools/impose_morality_3d_ending_matrix.py`

## Core Design Rules
- Keep explicit non-secret ending competition.
- Endings should be gated by availability plus desirability ranking.
- Final-turn available endings should usually be 3-4, not one hidden needle path.
- Use weighted formulas with at least 2-3 moral variables per gate or score.

Canonical axes:
- `Duty_Order`
- `Mercy_Care`
- `Truth_Candor`
- `Loyalty_Bonds`
- `Fairness_Reciprocity`
- `Harm_Aversion`
- `Phase_Clock`
- `Realpolitik_Pressure` for ending-cluster eligibility

## Hermes Execution Pattern
Use direct CLI commands and print exact artifact paths.
Do not use `execute_code` or sandbox path checks for generator, routing-probe, or filesystem work.

Set `REPO_ROOT` to your local clone root.
- On this machine: `/mnt/c/projects/GPTStoryworld`
- On a MacBook: use your local repo path, for example `/Users/you/projects/GPTStoryworld`

For the canonical generator path:

```bash
cd "$REPO_ROOT"
python3 tools/gen_morality_constitution_batch.py
python3 tools/probe_morality_batch_routing.py \
  --batch-dir "$REPO_ROOT/storyworlds/3-5-2026-morality-constitutions-batch-v1" \
  --runs 600 \
  --out "$REPO_ROOT/storyworlds/3-5-2026-morality-constitutions-batch-v1/_reports/routing_probe_latest.json"
```

For a smaller smoke run, use the wrapper:

```bash
export REPO_ROOT=/path/to/GPTStoryworld
export PYTHON_BIN=python3
cd "$REPO_ROOT/hermes-skills/storyworld-conveyor"
./scripts/run_moral_quandary_smoke.sh
```

That prints:
- morality batch dir
- routing probe report path

For a MacBook or smaller local run, prefer a narrower 20-encounter pass and report:
- generated world path
- validator result
- routing probe output path

## Conveyor Wrapper
If you want a visible repeated harness loop, use the live demo wrapper:

```bash
export REPO_ROOT=/mnt/c/projects/GPTStoryworld
cd "$REPO_ROOT/hermes-skills/storyworld-conveyor"
scripts/run_live_factory_demo.sh \
  "$REPO_ROOT/storyworlds/by-week/2026-W11/validated_macbeth.json" \
  "$REPO_ROOT/hermes-skills/storyworld-conveyor/sample_data/live_demo_config.json" \
  moral_demo \
  10
```

That wrapper is for visible grind mechanics only. It does not replace the morality-specific generator and routing probe.

## Anti-Hallucination Controls
- No claims of completion without a world file path and routing probe receipt.
- No claims of “moral balance” without actual probe statistics.
- Do not silently substitute secret-ending topology for open-manifold moral endings.
- If using the conveyor wrapper, do not invent stage names beyond the real factory manifests.
- Do not invent local base files such as `working_worlds/...` unless they already exist and `ls` proves it.

## Suggested Session Opener
```text
Use skill moral-quandary-storyworld-building.

Rules:
- Work artifact-first only.
- Keep explicit non-secret endings.
- Do not use secret-ending logic unless I explicitly ask for it.
- After each command, print exact paths for the generated world and the routing probe report.
```
