---
name: pure-trm-trainer
description: Build and run pure TRM controller training workflows under Hermes, including corpus assembly from TRM play logs, event logs, reasoning traces, normalized JSONL datasets, router QLoRA training, and hill-climbing search loops over generalization level. Use when Codex needs to curate cross-environment controller data, turn logs into conductor-style training corpora, launch a Hermes-wrapped trainer, or optimize a TRM bench by iterating on generalization breadth without mixing in prose or adapter authoring.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, TRM, Training, Generalization, Benchmarks, Router]
    related_skills: [qmd]
---

# Pure TRM Trainer

Use this skill to keep TRM training narrow: controller behavior, transition choice, constraint satisfaction, verifier logic, and rebalance reasoning, not prose generation.

Start from normalized `state/tools/action` records whenever possible. If the source data is raw, convert it once into that shape before training.

## Workflow

1. Decide the target controller behavior.
   - Use TRM for topology, action selection, constraint satisfaction, rebalancing, and verifier-style reasoning.
   - Do not mix in story prose quality unless the user explicitly wants a hybrid model.
2. Arrange the corpus.
   - Read [data-arrangement.md](./references/data-arrangement.md) for source selection and split rules.
   - Read [source-patterns.md](./references/source-patterns.md) for concrete source recipes.
3. Build a normalized corpus.
   - Canonical builder:
     - `python hermes-skills/pure-trm-trainer/scripts/build_router_training_corpus.py --out <messages-jsonl>`
4. Launch Hermes-wrapped training.
   - Router QLoRA recipe:
     - Build a router corpus from the persistent-tesseract router dataset, then launch `train_qlora_sft.py` through the Hermes bridge.
     - Canonical sample spec:
       - `python hermes-skills/pure-trm-trainer/scripts/run_trm_trainer_hermes.py --config hermes-skills/pure-trm-trainer/references/router-training-spec.sample.json`
     - This follows the same low-VRAM recipe used in persistent-tesseract: 4-bit NF4, `q_proj,k_proj,v_proj,o_proj`, and a compact messages JSONL corpus.
   - Canonical runner:
     - `python hermes-skills/pure-trm-trainer/scripts/run_trm_trainer_hermes.py --config hermes-skills/pure-trm-trainer/references/router-training-spec.sample.json`
   - Bench menu:
     - `python hermes-skills/pure-trm-trainer/scripts/run_trm_bench.py --bench routerbench`
     - `python hermes-skills/pure-trm-trainer/scripts/run_trm_bench.py --bench primehub-envs`
     - `python hermes-skills/pure-trm-trainer/scripts/run_trm_bench.py --bench primehub-baseline`
     - Add `--dry-run` to resolve the chosen bench config without launching.
   - Router bench runner:
     - `python hermes-skills/pure-trm-trainer/scripts/run_trm_routerbench.py`
     - Add `--dry-run` to resolve the portable bench config without launching.
     - Add `--template-root <path>` or `--corpus-spec <path>` if your local checkout lives outside the usual `C:/projects` or `/mnt/c/projects` roots.
   - One-click routerBench action:
     - Use this when the user asks to run `trm-routerBench`.
     - This path is isolated from the full trainer pipeline and is the preferred UI prompt flow for bench-only runs.
   - Watch / tail helper:
     - `python hermes-skills/pure-trm-trainer/scripts/watch_trm_routerbench.py --run-dir <run_dir>`
     - Use this to monitor an already-running bench without relaunching it.
     - Add `--once` for a single snapshot render, or omit it to follow updates.
   - Bench watcher alias:
     - `python hermes-skills/pure-trm-trainer/scripts/watch_trm_bench.py --run-dir <run_dir>`
     - Use this when you want a neutral name that matches the bench menu.
   - Hill-climb runner:
     - `python hermes-skills/pure-trm-trainer/scripts/run_trm_generalization_hillclimb.py --config <search-spec>.json`
   - Smoke wrapper:
     - `powershell -ExecutionPolicy Bypass -File hermes-skills/pure-trm-trainer/scripts/run_trm_hillclimb_smoke.ps1`
     - Add `-RunId <name>` to stamp a run directory.
     - Add `-NoEval` to skip the evaluator command and rely on scorecard fallback from the trainer summary.
5. Inspect artifacts.
   - Check `prepare_corpus/manifest.json`
   - Check `trainer_config.resolved.json`
   - Check `launch_trainer/manifest.json`
   - Check final `summary.json`
   - For hill-climb runs, also check `hillclimb_ledger.jsonl` and each candidate `result.json`

## Run Telemetry

Research and training runs should emit a compact Hermes-style status card.

- Show the current phase and candidate or step.
- Show the corpus or data source in use.
- Show the RAM budget or `auto` if the run does not know it yet.
- Show ETA once at least one completed candidate can anchor an estimate.
- Show percent complete and a short ASCII progress bar.
- Show the current candidate metrics and the best-so-far metrics.
- Keep the output short enough to tail in a terminal without scrolling noise.
- Write the same snapshot into `progress.snapshot.json` so other tools can read it.

## Hill-Climbing Loop

Use this when the user wants the best TRM bench score, not just a one-off trainer run.

1. Define the search axis as a generalization ladder.
   - Step 0: in-domain only, minimal state, no held-out envs.
   - Step 1: light generalization, a few held-out episodes.
   - Step 2: cross-run generalization within the same env family.
   - Step 3: cross-environment generalization across related families.
   - Step 4: broad generalization across families and action namespaces.
   - Step 5: hardest setting, strongest compression and weakest memorization.
2. Hold the evaluation anchors fixed.
   - Keep a small anchor set for the benchmark.
   - Do not tune on the anchors.
   - Preserve the same score definition across iterations.
3. Run one candidate at a time.
   - Change only a few knobs per iteration:
     - source mix
     - held-out breadth
     - state compression
     - negative-example rate
     - recovery-example rate
     - action-namespace normalization
   - Prefer a local mutation around the current best configuration.
4. Score the run.
   - Record train score, anchor score, failure rate, and recovery rate.
   - Track generalization gap.
   - Prefer the highest anchor score with an acceptable gap, not the highest train score.
5. Keep or mutate.
   - If anchor score improves, keep the candidate as the new baseline.
   - If anchor score drops but a different knob looks promising, branch a sibling candidate.
   - If repeated mutations plateau, move one rung up or down the generalization ladder.
6. Stop when the curve saturates.
   - Stop after the best anchor score fails to improve for several nearby mutations.
   - Prefer a smaller, cleaner dataset over a larger but overfit one.

## Search Heuristics

- Start narrow, then widen.
- Use one controlled mutation per loop when possible.
- Compare candidates on the same anchors.
- Treat train gain without anchor gain as overfitting.
- Favor a model that survives harder held-out envs over one that only spikes on easy repeats.
- Keep the final artifact set small and reproducible: corpus spec, resolved trainer config, run manifest, and summary.
- If you have a separate evaluator, have it write a compact `scorecard.json` with `train_score`, `anchor_score`, `failure_rate`, and `recovery_rate`.
- Emit a Hermes-style status card for training runs, with RAM, ETA, percent complete, data source, and a compact ASCII progress bar.
- Keep the status contract consistent across research training skills.

## Corpus Rules

- Prefer diverse environments over repeated near-duplicates from one environment.
- Keep train/validation splits separated by environment or run when possible, not just by row.
- Preserve source metadata in `meta` so later audits can trace bad behavior back to a world, run, or prompt family.
- Treat reasoning traces as supervision only when they encode decision-relevant state, candidate actions, or critique. Skip decorative chain-of-thought.
- Use Monte Carlo, verifier, or transition metrics to decide what the controller should improve; do not guess from surface prose.

## Hermes Runner

Use [run_trm_trainer_hermes.py](./scripts/run_trm_trainer_hermes.py) for the full Hermes path. It performs three stages:

- `prepare_corpus`
- `prepare_config`
- `launch_trainer`

Use `run_hrm_trainer_hermes.py` only when the user already has a clean conductor dataset and does not need corpus assembly. If that script exists in a sibling checkout, prefer it over reimplementing the same bridge.

## Source Types

Supported directly by the corpus builder:

- `trm_play_root`
  - Expects AICOO/TRM setup output with `worlds/*/trm_traces.jsonl`
  - Converts play logs into `state/tools/action`
- `jsonl`
  - `mode=normalized`: rows already contain `state`, `tools`, `action`
  - `mode=reasoning_trace`: build `state` from selected fields and map action/tool fields explicitly

## Hard Rules

- Keep this skill pure TRM. If the user wants prose, authoring adapters, or encounter block generation, switch to another skill or a separate workflow.
- Do not claim a run succeeded unless the Hermes stage manifests say `completed`.
- Do not train on mixed-quality logs without preserving source metadata.
- Do not let validation rows come from the same environment slice used for training if the task is cross-environment generalization.
- Do not silently strip invalid rows; record counts in the corpus manifest.
- Do not optimize on anchor evals and training evals at the same time; anchors stay fixed while candidates mutate.
- Do not let the search loop drift into generic hyperparameter tuning if the user asked for generalization-level search.

## References

- Data curation guide: [data-arrangement.md](./references/data-arrangement.md)
- Source recipes: [source-patterns.md](./references/source-patterns.md)
- Hill-climb search spec: [hillclimb-spec.sample.json](./references/hillclimb-spec.sample.json)
- Hill-climb smoke spec: [hillclimb-spec.smoke.json](./references/hillclimb-spec.smoke.json)
- Router bench spec: [routerbench-spec.json](./references/routerbench-spec.json)
- PrimeHub envs bench spec: [primehub-envs-bench.json](./references/primehub-envs-bench.json)
- PrimeHub baseline bench spec: [primehub-baseline-bench.json](./references/primehub-baseline-bench.json)
- Router training recipe: [router-training-recipe.md](./references/router-training-recipe.md)
- Router training spec: [router-training-spec.sample.json](./references/router-training-spec.sample.json)
- Bench menu: [bench-menu.md](./references/bench-menu.md)
- Router corpus builder: [build_router_training_corpus.py](./scripts/build_router_training_corpus.py)
- Router trainer bridge: [run_trm_trainer_hermes.py](./scripts/run_trm_trainer_hermes.py)
- Router bench launcher: [run_trm_routerbench.py](./scripts/run_trm_routerbench.py)
- Bench launcher: [run_trm_bench.py](./scripts/run_trm_bench.py)
- Router bench watcher: [watch_trm_routerbench.py](./scripts/watch_trm_routerbench.py)
- Bench watcher alias: [watch_trm_bench.py](./scripts/watch_trm_bench.py)
- Router bench UI prompt: use `trm-routerBench` as the action name in Hermes.
- Local scorecard evaluator: [evaluate_trm_scorecard.py](./scripts/evaluate_trm_scorecard.py)
- Run telemetry standard: [run-telemetry.md](./references/run-telemetry.md)

## Example Requests

- "Use pure-trm-trainer to turn these TRM play logs into a cross-world controller dataset."
- "Build a Hermes-safe TRM training run from verifier traces and held-out validation worlds."
- "Prepare a hub-ready pure TRM workflow that learns from logs and reasoning traces without mixing in prose generation."
