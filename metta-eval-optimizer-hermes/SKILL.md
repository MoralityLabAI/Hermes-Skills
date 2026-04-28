---
name: metta-eval-optimizer-hermes
description: "Use for designing MeTTa-scaffolded meta-skills that optimize Hermes/PrimeHub/Intellect evals, fork task skills into gate-circuit variants, and route artifacts into Pure-TRM-Trainer or PrimeLab without mixing their responsibilities."
---

# MeTTa Eval Optimizer Hermes

Use this meta-skill when the goal is to improve an eval or fork a Hermes task skill by adding MeTTa/TRM gate structure.

## Local References

- Contract: `references/meta_skill_contract.md`

## Local Scripts

- `scripts/build_metta_eval_fork_plan.py`

## Skill Contract

Follow the `Hermes-MeTTa-Eval-Optimizer-v1` flow:

1. `METTA_ENV_DIAGNOSE`: classify the env bottleneck as contract, schema, routing, structure, logic, math, safety, or latent-profile.
2. `TRM_ROLE_SELECT`: choose the TRM role family: formatter, router, critic, verifier, repairer, candidate auditor, or circuit controller.
3. `METTA_GATE_SPEC`: write the gate circuit: route, retrieve, propose, validate, repair, commit, and log.
4. `FORK_SKILL`: create a new skill fork only when the gate circuit changes behavior or data collection.
5. `PURE_TRM_EXPORT`: emit typed controller rows for Pure-TRM-Trainer when the useful signal is routing, verification, repair, or recovery.
6. `PRIMELAB_EXPORT`: emit env/rubric/eval specs for PrimeLab when the useful signal is environment quality, hosted eval, QLoRA conveyor, or rollout inspection.
7. `BENCH_COMPARE`: compare pure baseline, TRM-only, MeTTa-runtime, and MeTTa-runtime+repair arms.
8. `PAPER_LOG`: record claim boundary, artifact paths, and whether the result is live-model, deterministic replay, or post-hoc projection.

## Routing Rules

- Use Pure-TRM-Trainer for controller behavior, router corpora, verifier rows, recovery rows, hillclimb loops, and fixed anchor scorecards.
- Use PrimeLab for environment packaging, rubric design, baseline evals, hosted RL, QLoRA conveyors, and rollout inspection.
- Use MeTTa as the circuit grammar between them, not as a replacement for either infrastructure layer.
- For Intellect-3 logic, prioritize symbolic signature gates and min-edit projection around plausible grid candidates.
- For Intellect-3 math, treat the env as a scale boundary unless candidate sets, teacher traces, or solver-compatible invariants exist.
- For schema/tool/choice/IFEval tasks, prioritize deterministic validators and repair gates before training.
- For psycho or latent-profile tasks, decompose aggregate reward into item vectors, subscales, and stability metrics before claiming improvement.

## Output Artifacts

For each new fork or eval optimization, emit:

- fork name and source skill
- env family and bottleneck
- MeTTa gate list
- TRM role list
- Pure-TRM-Trainer export rows to collect
- PrimeLab env/rubric/eval work to perform
- benchmark arms
- claim boundary
- next experiment

Use `scripts/build_metta_eval_fork_plan.py` to generate the current paper-facing fork plan.
