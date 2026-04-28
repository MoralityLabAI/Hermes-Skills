# MeTTa Eval Optimizer Contract

This meta-skill treats MeTTa as a circuit grammar for eval optimization. It does not train adapters directly and does not replace benchmark harnesses. It decides which gate should own which part of the skill flow, then routes data to the right infrastructure.

## Infrastructure Split

Pure-TRM-Trainer source path:

`C:\projects\Hermes-Skills\Hermes Skills\pure-trm-trainer`

Use it for:

- controller corpora
- router and critic rows
- verifier and recovery examples
- hillclimb search over generalization breadth
- fixed-anchor scorecards

PrimeLab source path:

`C:\projects\Hermes-Skills\Hermes Skills\primelab\primelab-hermes`

Use it for:

- environment definitions
- rubrics and reward functions
- local baseline evals
- hosted Prime eval/RL receipts
- QLoRA conveyor runs
- rollout inspection

## Gate Vocabulary

| Gate | Purpose | Preferred export |
| --- | --- | --- |
| `route_gate` | select skill/TRM role/env lane | Pure-TRM router row |
| `retrieve_gate` | fetch useful prior rows or examples | Pure-TRM retriever row |
| `proposal_gate` | obtain LLM/teacher/solver candidate | PrimeLab rollout trace |
| `validate_gate` | check contract, schema, signature, invariant | Pure-TRM critic/verifier row |
| `repair_gate` | canonicalize or project a near-valid candidate | Pure-TRM recovery row |
| `commit_gate` | choose final answer/action or abstain | Pure-TRM controller row |
| `learning_gate` | label failure mode and update corpus plan | paper/eval artifact row |

## Fork Decision Rules

Create a new fork when at least one condition holds:

- the gate circuit changes the observable answer path
- the fork collects new typed supervision rows
- the fork introduces a new verifier or repair policy
- the fork splits a scalar metric into subcomponent metrics
- the fork changes the train/eval boundary

Do not fork merely to rename a prompt.

## Hard-Env Policy

Intellect-3 logic:

- Treat as symbolically amplifiable.
- Collect grid candidates, row/column signatures, contradiction states, and min-edit projection traces.
- Score exactness, cell accuracy, signature consistency, and repair regret.

Intellect-3 math:

- Treat as scale-sensitive unless candidate sets or invariants are available.
- Collect teacher candidates, exact-answer extraction, numeric error archetypes, and verifier false positives/negatives.
- Do not claim small-model solve gains from format repair.

## Benchmark Arms

Use these arms when possible:

- `baseline`: plain skill or no TRM
- `pure_trm`: TRM role routing/retrieval without MeTTa gates
- `metta_runtime`: MeTTa gate circuit active without deterministic repair
- `metta_runtime_repair`: MeTTa gate circuit plus repair/projection
- `teacher_candidate_metta`: teacher/solver candidates plus MeTTa/TRM auditor

## Claim Labels

Use explicit labels in paper materials:

- `live_model_run`
- `deterministic_replay`
- `post_hoc_projection`
- `control_plane_threshold_eval`
- `environment_design`
- `training_corpus_plan`
