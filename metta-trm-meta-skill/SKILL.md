---
name: metta-trm-meta-skill
description: "Use when a Hermes or Codex workflow needs a MeTTa/TRM control-plane meta-skill: authoring compact MeTTa packages, repairing small-model MeTTa drafts, exporting TRM controller rows, and evolving task skills through benchmark-gated MeTTa framework optimization."
---

# MeTTa TRM Meta-Skill

Use this as the front-door orchestration skill for compactification work where small models need help authoring MeTTa, curating TRM data, or improving Hermes skills through typed control-plane gates.

This skill composes, rather than replaces:

- `metta-composition-hermes` for safe gate wiring.
- `metta-trm-hermes-pipeline` for package compilation.
- `metta-eval-optimizer-hermes` for eval fork planning.
- `trm-mcp` for low-token retrieval over memory surfaces.
- `pure-trm-trainer` for controller, verifier, repair, and commit/veto training rows.

## Core Flow

Follow `AUTHOR -> REPAIR -> VERIFY -> EXPORT_ROWS -> BENCH_ARMS -> EVOLVE_SKILL`:

1. `AUTHOR`
   Draft a compact MeTTa package from a task trace, skill failure, benchmark, or MCP memory surface. Keep one top-level atom per line.
2. `REPAIR`
   Canonicalize small-model MeTTa drafts before judging them. Repair syntax and unsupported atom usage separately.
3. `VERIFY`
   Score syntax, contract coverage, retrieval coverage, repair coverage, and TRM export readiness.
4. `EXPORT_ROWS`
   Emit Pure-TRM-Trainer rows for author routing, syntax repair, semantic verification, retrieval routing, skill patch control, and commit/veto.
5. `BENCH_ARMS`
   Compare baseline, TRM-only, MeTTa-runtime, and MeTTa-runtime+repair. Label projected results as methodology unless receipts exist.
6. `EVOLVE_SKILL`
   Propose bounded skill changes only when verifier or benchmark evidence identifies a concrete bottleneck.

## Local References

- Contract: `references/meta_skill_contract.md`

## Local Scripts

Canonical CLI:

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\metta-trm-meta-skill\scripts\metta_trm_meta_skill.py" --help
```

Common commands:

```powershell
python .\metta-trm-meta-skill\scripts\metta_trm_meta_skill.py author-packet --task "Improve storyworld NAV retrieval." --base-skill storyworld-player --target-env storyworld_nav --out-dir .\research\generated\metta_trm_meta\storyworld_nav_package

python .\metta-trm-meta-skill\scripts\metta_trm_meta_skill.py verify-packet --package-dir .\research\generated\metta_trm_meta\storyworld_nav_package --out .\research\generated\metta_trm_meta\storyworld_nav_verify.json

python .\metta-trm-meta-skill\scripts\metta_trm_meta_skill.py export-trm-rows --package-dir .\research\generated\metta_trm_meta\storyworld_nav_package --out .\research\generated\metta_trm_meta\storyworld_nav_trm_rows.jsonl
```

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

