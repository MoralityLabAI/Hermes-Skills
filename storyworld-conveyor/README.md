# Storyworld Conveyor

Production-oriented Hermes Agent scaffold for building, running, grading, judging, aggregating, and exporting storyworld encounter datasets.

## Repo Tree
```text
hermes-skills/storyworld-conveyor/
  AGENTS.md
  README.md
  run_storyworld_conveyor.py
  sample_data/
  sample_runs/
  schemas/
  skills/
  storyworld_conveyor/
```

## Stages
- `encounter_builder`
- `completion_runner`
- `env_grader`
- `llm_judge`
- `aggregator`
- `trainer_export`

## Storyworld Factory Beats
- `seed_world`: derive an 80-120 encounter draft from a validated base world with `one_shot_factory.py`
- `materialize_spools`: ensure spool structure exists on disk before any later tuning
- `sequence_spools`: inject bounded desirability scaffolding across spool order
- `apply_artistry`: diversify gating, desirability, and effect patterns beyond monoculture `Nudge`
- `secret_gate_audit`: verify secret-ending and gated-option floors
- `multiple_paths_probe`: sample path diversity before heavy balancing
- `monte_carlo_baseline`: gather ending distributions, dead-end rates, and secret reachability
- `ending_reachability_balance`: push unreachable endings back into play
- `late_stage_balance`: warp metric distance around selected properties/endings when a known target ending exists
- `export_swmd_min`: emit bounded-context SWMD-min for later MCP or QLoRA loops
- `build_encounter_index`: produce encounter packets/cards for small-model bounded orchestration
- `build_qlora_examples`: compile training-style examples for repair/compress/edit loops

## MCP-Default Large Storyworld Flow
Use this path for large Hermes storyworld builds and revisions. It prevents the 20M-input-token failure mode by converting once, indexing once, then routing each conveyor phase through small encounter packets.

```bash
python hermes-skills/storyworld-conveyor/scripts/prepare_mcp_conveyor_config.py \
  --storyworld <world.json|world.swmd.min.md> \
  --out-config <mcp_config.json> \
  --max-encounters 12

python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py \
  --config <mcp_config.json>

python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py \
  --config <mcp_config.json> \
  --preflight-only
```

The run writes `mcp_budget_preflight/budget_report.json` before model load. If it fails, reduce `neighbor_hops`, `max_encounters`, or `planning_card_tokens` before raising context limits.

## Data Model
- Encounter record:
  - encounter spec
  - canonical environment state
  - allowed actions and constraints
- Completion record:
  - prompt, completion text, token counts, model metadata
- Env grade record:
  - action validity
  - constraint violations
  - target hits
  - state delta counts
  - success flag
  - penalties
  - normalized env score
- Judge record:
  - coherence
  - ethical adequacy
  - least-bad tradeoff quality
  - stakeholder awareness
  - uncertainty handling
  - concise reasoning quality
  - aggregate judge score
- Aggregate record:
  - `final_score = 0.65 * env_score + 0.35 * judge_score`
  - weights are configurable in config JSON

## Progress Manifest Format
```json
{
  "run_id": "demo3",
  "stage": "env_grader",
  "status": "completed",
  "input_files": [".../completions.jsonl"],
  "output_files": [".../env_grades.jsonl"],
  "counters": {"graded_count": 6},
  "config_digest": "sha256..."
}
```

## GPT-5 Mini Judge Prompt
System:
```text
You are a strict auxiliary judge. Output JSON only with keys coherence, ethical_adequacy, least_bad_tradeoff_quality, stakeholder_awareness, uncertainty_handling, concise_reasoning_quality, judge_score, notes. All scores must be floats in [0,1].
```

User payload:
```json
{
  "encounter": "<serialized encounter record>",
  "completion_text": "<candidate completion>"
}
```

## GPT-5 Mini Moral Trace Smoke
Use a dedicated system prompt file plus the desktop `GPTAPI.txt` key when you want richer moral-reasoning metadata from the judge stage:

```bash
$desktop = [Environment]::GetFolderPath('Desktop')
$env:OPENAI_API_KEY = (Get-Content (Join-Path $desktop 'GPTAPI.txt') -Raw).Trim()
python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py \
  --config hermes-skills/storyworld-conveyor/sample_data/gpt5_mini_moral_judge.json \
  --run-id gpt5_mini_moral_judge_smoke \
  run-pipeline
```

This writes judge-side traces under `llm_judge/traces.jsonl` with:
- the judge system prompt path and resolved text
- the serialized user prompt
- the parsed response text
- any `reasoning_content` returned by the API
- finish reason, usage, and response id metadata when available

## 10 Encounter Smoke Test
```bash
python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py \
  --config hermes-skills/storyworld-conveyor/sample_data/pipeline_config.json \
  --run-id smoke10 \
  run-pipeline
```

To scale to 10 encounters, edit `encounter_builder.count` and remove `input_jsonl`.

## Arcee Play Batch
Use the OpenAI-compatible completion path with Trinity Large Thinking for plays/completions only:

```bash
$desktop = [Environment]::GetFolderPath('Desktop')
$env:OPENAI_API_KEY = (Get-Content (Join-Path $desktop 'arcee.txt') -Raw).Trim()
python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py \
  --config hermes-skills/storyworld-conveyor/sample_data/arcee_trinity_smoke.json \
  --run-id arcee_trinity_smoke \
  run-pipeline
```

This keeps `llm_judge` on `mock` so only the completion stage spends credit.
If you want a constitution prompt, set `system_prompt_file` on the model config to a local markdown file such as `Claude.md`.

Each play run now also writes `completion_runner/traces.jsonl` with:
- the prompt path and raw prompt
- the parsed completion text
- the model's `reasoning_content` when present
- finish reason and token usage fields when the provider returns them
- the raw response path for the underlying API payload

## 120 Encounter Batch Mode
1. Set `encounter_builder.count` to `120`.
2. Add or ingest the desired thematic families.
3. Keep `llm_judge.provider=mock` until env grading is stable.
4. Use Hermes background terminal execution and checkpoint polling.

## Overnight Factory Run
```bash
python hermes-skills/storyworld-conveyor/run_storyworld_factory.py \
  --config hermes-skills/storyworld-conveyor/sample_data/factory_overnight_macbeth.json
```

This config is set up to keep going past non-critical balance failures and leave manifests/logs behind for every stage.

## Factory Config Menu
List valid factory templates:

```bash
python hermes-skills/storyworld-conveyor/scripts/make_factory_config.py --list-templates
```

Generate a valid config from constrained flags:

```bash
python hermes-skills/storyworld-conveyor/scripts/make_factory_config.py \
  --template fresh_seed_artistry \
  --base-world C:/projects/GPTStoryworld/storyworlds/by-week/2026-W11/validated_macbeth.json \
  --out-config C:/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/sample_data/generated_factory.json \
  --run-id macbeth_generated \
  --title "Macbeth: Generated Factory" \
  --about "A generated factory config with precise flag loading." \
  --motif "Every oath becomes measurable at the next branch." \
  --target-encounters 80 \
  --characters "Macbeth,Lady Macbeth,Banquo,Macduff" \
  --ending-count 4 \
  --secret-ending-count 2 \
  --super-secret-count 1 \
  --avg-options 3.2 \
  --avg-reactions 2.5 \
  --avg-effects 4.5 \
  --include-monte-carlo \
  --include-encounter-index
```

The generated JSON is the source of truth for the run. The design targets are metadata for Hermes to respect and report against; they are not proof that the resulting world already meets them.

## Real Grind Loop
If you want to watch repeated conveyor iterations instead of a single run, use:

```bash
python hermes-skills/storyworld-conveyor/scripts/run_factory_grind.py \
  --config hermes-skills/storyworld-conveyor/sample_data/generated_factory.json \
  --run-id-prefix grind_demo \
  --iterations 10 \
  --tail-lines 6 \
  --force
```

This is the point where Hermes can honestly show a 70- or 100-step conveyor sequence in the harness: only when a real script like `run_factory_grind.py` is executing and tailing per-stage logs. Without that, Hermes has only one factory run per command and any "80 turns" narrative is fake.

## Local Qwen Adapter Loop
The factory can hand off directly to a local adapter run using the emitted QLoRA-style message datasets.

Train from an existing factory run:

```bash
export REPO_ROOT=/path/to/GPTStoryworld
export PYTHON_BIN=python3
export MODEL_NAME=Qwen/Qwen2.5-1.5B
cd "$REPO_ROOT/hermes-skills/storyworld-conveyor"
./scripts/run_local_qwen_adapter_cycle.sh \
  "$REPO_ROOT/hermes-skills/storyworld-conveyor/factory_runs/macbeth_patch_test/qlora/overnight_examples" \
  "$REPO_ROOT/hermes-skills/storyworld-conveyor/local_adapter_runs/qwen_adapter_run"
```

The trainer consumes:
- `train_messages.jsonl`
- `val_messages.jsonl`

and writes:
- adapter weights
- tokenizer files
- `adapter_train_summary.json`

Use a fresh venv if your local environment has incompatible `torch`/`peft`/`transformers` versions:
- [requirements-local-qwen-adapter.txt](C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\requirements-local-qwen-adapter.txt)

If you already have the `D:\Research_Engine\storyworld_qlora` stack, prefer the native launcher prep:

```bash
python hermes-skills/storyworld-conveyor/scripts/prepare_storyworld_qlora_run.py \
  --factory-run-root C:/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/the_usual_suspects_qwen35_2b \
  --run-id qwen35-2b-usual-suspects-local \
  --qwen-model-path D:/Research_Engine/models/Qwen3.5/Qwen3.5-2B-HF
```

That writes:
- `D:\Research_Engine\storyworld_qlora\runs\<run_id>\run_manifest.json`
- `D:\Research_Engine\storyworld_qlora\runs\<run_id>\run_train.cmd`

and uses your existing:
- `D:\Research_Engine\.venv-train\Scripts\python.exe`
- `D:\Research_Engine\storyworld_mcp_stack\scripts\train_qlora_local_micro.py`

## 4GB Qwen 2B Context Port
For 4GB VRAM work, do not start with whole-world playthrough loops or adapter training. Use the Hermes context-managed port that wraps the small-storyworld-builder MCP phases one encounter at a time.

Dry run:

```bash
python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py \
  --config hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port.json \
  --dry-run
```

Live bounded run:

```bash
python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py \
  --config hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port.json
```

After adapter training, stamp a post-train config instead of editing JSON by hand:

```bash
python hermes-skills/storyworld-conveyor/scripts/prepare_small_model_port_config.py \
  --base-config hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port_posttrain.template.json \
  --out-config hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port_posttrain.json \
  --adapter-path D:/Research_Engine/storyworld_qlora/adapters/<trained_adapter> \
  --trm-advice-json D:/path/to/trm_advice.json
```

Then run:

```bash
python hermes-skills/storyworld-conveyor/scripts/run_small_model_storyworld_port.py \
  --config hermes-skills/storyworld-conveyor/sample_data/qwen2b_4gb_context_port_posttrain.json
```

This wrapper:
- builds the SWMD encounter index
- injects TRM advice as an external constraints packet when present
- runs the phased MCP loop with 4GB-friendly defaults
- writes Hermes-style manifests, progress files, and per-stage logs under `context_port_runs/<run_id>/`

## Hybrid Repair Mode
If the model still fails on full SWMD output, run the port in hybrid mode so it can fall back to operation-level repair packets.

Config keys:
- `repair_mode`: `swmd_only`, `operation_only`, `both`, or `phase_then_operation_fallback`
- `operation_max_packets`: how many encounter packets to repair in the fallback pass
- `operation_max_new_tokens`: token budget for the one-op JSON response
- `operation_no_adapter`: force base-model smoke without an adapter
- `quality_report`: optional path to the world quality gate report
- `monte_carlo_report`: optional path to the Monte Carlo report used for TRM advice

Recommended default for brittle Qwen 2B repair:
- `repair_mode = phase_then_operation_fallback`
- `operation_max_packets = 24`
- `operation_max_new_tokens = 160`
- `operation_no_adapter = true` until the adapter path is stable

Recommended defaults for Qwen 2B on 4GB:
- If another process is already using about `100MB` VRAM, treat the real budget as about `3.9GB`, not `4GB`
- `max_encounters`: `4`
- `max_new_tokens`: `96`
- `temperature`: `0.0`
- `neighbor_hops`: `1`
- `context_budget_tokens`: `6144`
- `reserve_output_tokens`: `768`
- `planning_card_tokens`: `700`
- `apply`: `false` until parse stability is confirmed
- keep context bounded through encounter packets rather than full-world diary replay

## Operation-Level Repair Smoke
If Qwen 2B keeps drifting on full SWMD output, switch to discrete repair packets instead of asking it to emit whole blocks.

```bash
python hermes-skills/storyworld-conveyor/scripts/run_storyworld_operation_smoke.py \
  --world-json C:/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/abstract_letters_96/worlds/artistry_world.json \
  --quality-report C:/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/factory_runs/abstract_letters_96/reports/quality_gate.json \
  --model-path D:/Research_Engine/models/Qwen3.5/Qwen3.5-2B-HF \
  --no-adapter \
  --max-new-tokens 160 \
  --max-packets 24
```

This path:
- builds per-encounter operation packets
- asks the model for strict JSON only
- normalizes malformed responses back to deterministic option/reaction/effect/formula suggestions
- keeps Windows compatibility by using the local HF stack and sanitized adapter loading when adapters are enabled

## Qwen 9B On Mac, No Adapter
If the 2B adapter is not good enough for direct encounter-block generation, switch to the Hermes skill-only path on a stronger machine and drop the adapter entirely.

Starter config:
- [qwen9b_mac_skill_only.json](C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\sample_data\qwen9b_mac_skill_only.json)

Intent:
- no adapter
- same Hermes bounded packet workflow
- larger base model on the Mac
- keep `apply=false` until parse quality is verified

Before running remotely:
- replace `model_path` with the actual Qwen 9B path on the Mac
- use a Mac-local clone/path mapping for `swmd` and dataset paths if the Mac is not mounting this Windows repo directly

For reasoning-only use on the Mac, keep phases to:
- `plan`
- `characterize`
- `act_complete`
- `recharacterize`

If you have Monte Carlo and quality-gate artifacts, you can let the wrapper auto-build a rebalance TRM packet by setting:
- `monte_carlo_report`
- `quality_report`

or build the packet directly:

```bash
python hermes-skills/storyworld-conveyor/scripts/build_storyworld_trm_advice.py \
  --mc-report hermes-skills/storyworld-conveyor/factory_runs/<run>/reports/monte_carlo.txt \
  --quality-report hermes-skills/storyworld-conveyor/factory_runs/<run>/reports/quality_gate.json \
  --storyworld-label "<world label>" \
  --out-advice hermes-skills/storyworld-conveyor/factory_runs/<run>/reports/trm_rebalance_advice.json
```

The resulting packet is intended to:
- constrain Hermes reasoning with measured route-skew and dead-end data
- prioritize underrepresented endings and failing quality checks
- keep direct SWMD authorship behind guarded/repair-based phases

## Hermes HRM Trainer Port
The capped `HRM-re` trainer template can also be launched through a Hermes manifest wrapper so training runs emit the same staged receipts as the storyworld conveyor.

Starter config:
- [hrm_trainer_hermes_safe.json](C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\sample_data\hrm_trainer_hermes_safe.json)

Dry run:

```bash
python hermes-skills/storyworld-conveyor/scripts/run_hrm_trainer_hermes.py \
  --config hermes-skills/storyworld-conveyor/sample_data/hrm_trainer_hermes_safe.json \
  --dry-run
```

Live launch:

```bash
python hermes-skills/storyworld-conveyor/scripts/run_hrm_trainer_hermes.py \
  --config hermes-skills/storyworld-conveyor/sample_data/hrm_trainer_hermes_safe.json
```

This wrapper:
- resolves and snapshots the effective trainer config
- launches `run_trainer.ps1` under the existing HRM hard caps
- records Hermes manifests, logs, and output receipts

Use it when you want more methodical curated HRM/TRM data loops instead of loose prompt-only authoring passes.

## Budget Envelope
- Target spend tonight: about `$4.00`
- Working assumption from your brief:
  - about `40M` input tokens
  - about `5M` output tokens
- Recommended operating mode:
  - keep storyworld factory structural passes local/deterministic
  - spend judge tokens only after seed/spool/artistry passes are stable
  - shard external judge passes instead of one giant run

## Example Cron Usage
```text
schedule_cronjob "python hermes-skills/storyworld-conveyor/run_storyworld_conveyor.py --config hermes-skills/storyworld-conveyor/sample_data/pipeline_config.json run-pipeline" "0 2 * * *"
```

## Example delegate_task Usage Plan
1. Delegate encounter generation by family shard.
2. Delegate completion runs by model shard.
3. Delegate auditing of any failed stage directory.
4. Delegate post-factory judge shards by encounter slice once `quality_gate` artifacts exist.

## Failure Modes And Anti-Hallucination Controls
- Missing output file means the stage failed.
- A stage is not complete until `manifest.json` says `completed`.
- `judge-llm` is auxiliary only.
- Do not continue downstream if row counts do not match manifest counters.
- Prefer stage reruns over ad-hoc manual edits inside run directories.

## How Hermes Should Report Progress Each Checkpoint
- Include:
  - `run_id`
  - stage
  - manifest path
  - row count
  - next action
- Example:
  - `env_grader completed for demo3`
  - `manifest=.../demo3/env_grader/manifest.json`
  - `graded_count=6`
  - `next=judge-llm`

## How To Keep Token Burn Under Control
- Default to `mock` judge during smoke testing.
- Start with 3 or 10 encounters.
- Shard large batches.
- Report counts and paths, not full artifact contents.
