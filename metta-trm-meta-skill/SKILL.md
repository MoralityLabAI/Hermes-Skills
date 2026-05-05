---
name: metta-trm-meta-skill
description: "Use when a Hermes or Codex workflow needs a MeTTa/TRM control-plane meta-skill: routing broad subject/cognition domains, authoring compact MeTTa packages, repairing small-model MeTTa drafts, exporting TRM controller rows, and evolving task skills through benchmark-gated MeTTa framework optimization."
---

# MeTTa TRM Meta-Skill

Use this as the front-door orchestration skill for compactification work where small models need help routing broad domains, authoring MeTTa, curating TRM data, or improving Hermes skills through typed control-plane gates.

This skill composes, rather than replaces:

- `metta-composition-hermes` for safe gate wiring.
- `metta-trm-hermes-pipeline` for package compilation.
- `metta-eval-optimizer-hermes` for eval fork planning.
- `trm-mcp` for low-token retrieval over memory surfaces.
- `pure-trm-trainer` for controller, verifier, repair, and commit/veto training rows.

## Core Flow

Follow `ROUTE_DOMAIN -> AUTHOR -> REPAIR -> VERIFY -> EXPORT_ROWS -> BENCH_ARMS -> EVOLVE_SKILL`:

1. `ROUTE_DOMAIN`
   If the task is broad or ambiguous, route it through the domain lattice before authoring. Use university-subject/key-cognition domains, not final skill names.
2. `AUTHOR`
   Draft a compact MeTTa package from a task trace, skill failure, benchmark, or MCP memory surface. Keep one top-level atom per line.
3. `REPAIR`
   Canonicalize small-model MeTTa drafts before judging them. Repair syntax and unsupported atom usage separately.
4. `VERIFY`
   Score syntax, contract coverage, retrieval coverage, repair coverage, and TRM export readiness.
5. `EXPORT_ROWS`
   Emit Pure-TRM-Trainer rows for author routing, syntax repair, semantic verification, retrieval routing, skill patch control, and commit/veto.
6. `BENCH_ARMS`
   Compare baseline, TRM-only, MeTTa-runtime, and MeTTa-runtime+repair. Label projected results as methodology unless receipts exist.
7. `EVOLVE_SKILL`
   Propose bounded skill changes only when verifier or benchmark evidence identifies a concrete bottleneck.

## Local References

- Contract: `references/meta_skill_contract.md`
- Domain router lattice: `references/domain_router_lattice.md`

## Local Scripts

Canonical CLI:

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-meta-skill\scripts\metta_trm_meta_skill.py" --help
```

Strict small-model bootstrap bench:

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-meta-skill\scripts\run_small_model_bootstrap_bench.py" --out-dir D:\metta_trm_meta_small_model_bench --prompt-mode compact --max-tokens 1200
```

Use `--generation-mode staged` when testing whether a small model can build the package one file at a time under the same frozen base contract.

Repair-message baseline:

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-meta-skill\scripts\bench_repair_training_messages.py" --messages D:\metta_trm_meta_small_model_bench\small_model_bootstrap_20260505T150037Z\repair_training_messages.jsonl --out-dir D:\metta_trm_meta_small_model_bench\small_model_bootstrap_20260505T150037Z\repair_message_baseline_qwen4b
```

Synthetic repair curriculum:

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-meta-skill\scripts\build_repair_curriculum.py" --out-dir D:\metta_trm_meta_small_model_bench\repair_curriculum_v1 --examples-per-env 60
```

Compact repair controller:

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-meta-skill\scripts\train_repair_controller.py" --train-messages D:\metta_trm_meta_small_model_bench\repair_curriculum_v1\repair_curriculum_train_messages.jsonl --val-messages D:\metta_trm_meta_small_model_bench\repair_curriculum_v1\repair_curriculum_val_messages.jsonl --out-dir D:\metta_trm_meta_small_model_bench\repair_curriculum_v1\template_controller_eval
```

Held-out repair generalization:

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-meta-skill\scripts\run_repair_generalization_study.py" --out-dir D:\metta_trm_meta_small_model_bench\heldout_generalization --controller-train-messages D:\metta_trm_meta_small_model_bench\repair_curriculum_v1\repair_curriculum_train_messages.jsonl
```

Domain router bootstrap study:

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-meta-skill\scripts\run_domain_router_bootstrap_study.py" --out-dir D:\metta_trm_meta_small_model_bench\domain_router --router-mode heuristic
```

Add `--router-mode llm --run-bootstrap` when a local OpenAI-compatible endpoint is live.

Local 3B GGUF OpenAI-compatible shim:

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-meta-skill\scripts\serve_llama_cpp_openai.py" --model-path D:\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf --model-name Qwen2.5-3B-Instruct-Q4_K_M-local --host 127.0.0.1 --port 8084 --n-ctx 4096 --n-threads 6 --n-batch 128 --n-gpu-layers 0
```

Use `--n-gpu-layers 0` when `llama_cpp.llama_supports_gpu_offload()` is false; do not force GPU offload on CPU-only builds.

Common commands:

```powershell
python .\metta-trm-meta-skill\scripts\metta_trm_meta_skill.py author-packet --task "Improve storyworld NAV retrieval." --base-skill storyworld-player --target-env storyworld_nav --out-dir .\research\generated\metta_trm_meta\storyworld_nav_package

python .\metta-trm-meta-skill\scripts\metta_trm_meta_skill.py verify-packet --package-dir .\research\generated\metta_trm_meta\storyworld_nav_package --out .\research\generated\metta_trm_meta\storyworld_nav_verify.json

python .\metta-trm-meta-skill\scripts\metta_trm_meta_skill.py export-trm-rows --package-dir .\research\generated\metta_trm_meta\storyworld_nav_package --out .\research\generated\metta_trm_meta\storyworld_nav_trm_rows.jsonl

python .\metta-trm-meta-skill\scripts\metta_trm_meta_skill.py export-repair-training-rows --input D:\metta_trm_meta_small_model_bench\small_model_bootstrap_20260505T150037Z --out D:\metta_trm_meta_small_model_bench\small_model_bootstrap_20260505T150037Z\repair_training_rows.jsonl --messages-out D:\metta_trm_meta_small_model_bench\small_model_bootstrap_20260505T150037Z\repair_training_messages.jsonl --manifest D:\metta_trm_meta_small_model_bench\small_model_bootstrap_20260505T150037Z\repair_training_manifest.json
```

The messages export includes an `output_contract` in the user payload so small models learn to emit direct action JSON instead of tool-call wrappers.

## TRM Role Set

- `author_router`: chooses the package template, env lane, and source skill.
- `metta_syntax_repair`: repairs one-atom-per-line MeTTa syntax and rejects unsupported heads.
- `semantic_contract_verifier`: checks whether constraints, forbids, examples, and validation paths cover the task.
- `retrieval_policy_router`: chooses which MCP/resource family or prior trace should be loaded first.
- `skill_patch_controller`: maps verified bottlenecks to bounded skill-patch categories.
- `commit_veto`: commits, abstains, or requests more data based on scorecard evidence.

## Hard Rules

- Do not use MeTTa for long prose. Use it for contracts, invariants, retrieval cues, failure modes, repair hints, and gate roles.
- Do not let a small model invent unsupported atom heads without a repair pass.
- Do not train one vague meta-TRM. Export role-specific controller rows.
- Do not let benchmark gains update a skill unless the benchmark arm and evidence class are recorded.
- Do not claim live capability improvement from deterministic replay or post-hoc projection.
- Do not mix prose-generation data with pure controller rows unless a separate hybrid experiment explicitly calls for it.

## Default Claim Labels

Use one of:

- `live_model_run`
- `deterministic_replay`
- `post_hoc_projection`
- `control_plane_threshold_eval`
- `environment_design`
- `training_corpus_plan`
