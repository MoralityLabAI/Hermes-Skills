# Addendum: MeTTa Meta-Skills For Eval Optimization

Status: draft addendum  
Date: April 26, 2026

## Thesis

The next layer should be a meta-skill layer: skills that do not solve a benchmark directly, but improve how new skill forks are evaluated, trained, and curated. In this layer, MeTTa provides the gate grammar, Pure-TRM-Trainer provides controller/corpus training, and PrimeLab provides environment, rubric, hosted-eval, and QLoRA infrastructure.

This keeps responsibilities clean:

- MeTTa defines `route -> retrieve -> propose -> validate -> repair -> commit -> learn`.
- Pure-TRM-Trainer consumes typed rows for routers, critics, verifiers, recovery, and controller hillclimbs.
- PrimeLab owns environment quality, baseline evals, rubrics, rollout inspection, hosted training receipts, and QLoRA conveyor runs.

## New Meta-Skill Artifact

The meta-skill lives at [metta-eval-optimizer-hermes/SKILL.md](<C:\projects\Hermes-Skills\Hermes Skills\metta-eval-optimizer-hermes\SKILL.md>). Its contract is [meta_skill_contract.md](<C:\projects\Hermes-Skills\Hermes Skills\metta-eval-optimizer-hermes\references\meta_skill_contract.md>).

The generated fork plan is [metta_eval_meta_skill_fork_plan.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_eval_meta_skill_fork_plan.md>), with machine-readable JSON at [metta_eval_meta_skill_fork_plan.json](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_eval_meta_skill_fork_plan.json>).

## Fork Targets

| Fork | Purpose | Claim boundary |
| --- | --- | --- |
| `metta-flow-trm-circuit-controller` | Shared controller for gate-circuit skill forks. | Infrastructure only until live env arms run. |
| `metta-intellect3-logic-signature-gate` | Use MeTTa signatures and projection on hard logic grids. | Positive hard-env target, but must avoid answer leakage. |
| `metta-intellect3-math-teacher-auditor` | Use teacher candidates, invariants, and TRM auditors for math. | Boundary case; gains must come from candidate auditing, not invented math. |
| `metta-structured-contract-repair-lane` | Expand schema/tool/choice/IFEval repair lanes. | Compactification lane; not latent reasoning evidence. |
| `metta-psycho-item-vector-stability` | Turn aggregate psychometric scores into item/subscale stability metrics. | Interpretability and stability, not conventional exact correctness. |

## Paper Methodology Upgrade

This meta-skill layer gives the paper a cleaner methodology section. Rather than saying "we added MeTTa to TRM," the method becomes:

1. classify each env by bottleneck,
2. express the skill flow as MeTTa gates,
3. route each gate's failures into typed Pure-TRM-Trainer rows,
4. use PrimeLab for env/rubric/baseline or QLoRA work when the experiment needs a real environment path,
5. compare `baseline`, `pure_trm`, `metta_runtime`, `metta_runtime_repair`, and when needed `teacher_candidate_metta`.

The key contribution is not one more prompt variant. It is a reproducible way to generate new skill forks whose evals produce training data by construction.

## Immediate Next Experiments

The first fork should be `metta-intellect3-logic-signature-gate`, because it is hard but still symbolically structured. The second should be `metta-structured-contract-repair-lane`, because it is the clearest compactification lane. Intellect-3 math should remain the negative/control lane until teacher candidates or solver-compatible invariants are available.
