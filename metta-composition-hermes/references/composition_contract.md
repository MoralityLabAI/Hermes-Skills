# MeTTa Composition Contract

This contract defines how Hermes skills compose into TRM-aware MeTTa circuits.

## Role Compatibility

| TRM role family | Action support? | Composition use |
| --- | --- | --- |
| `choice_contract` | yes | final answer wrapper, label extraction, exact choice repair |
| `structured_map` | yes, narrow | schema, field order, line structure, object canonicalization |
| `internal_action` | yes, tiny | hidden continuation or exact latent action token |
| `abstain_guard` | no, critic-first | early veto, risk route, safe refusal validation |
| `hard_reasoning_logic` | limited | branch elimination, contradiction check, grid/signature verifier |
| `hard_reasoning_numeric` | limited | numeric verifier, candidate auditor, answer-form checker |

## Gate Semantics

- `route_gate`: choose the skill circuit and TRM role family.
- `retrieve_gate`: fetch supporting rows, examples, or role cards.
- `proposal_gate`: obtain model, teacher, solver, or replay candidates.
- `validate_gate`: check schema, risk, branch consistency, signature, or invariant.
- `repair_gate`: canonicalize formatting or project near-valid symbolic state.
- `commit_gate`: choose final action, abstain, or emit exact answer.
- `learning_gate`: label the failure mode for training and paper audit.

## Composition Classes

`compactifiable`:

- answer space is explicit
- verifier can see all success conditions
- repair is deterministic or bounded

`symbolically_amplifiable`:

- proposal must contain plausible structure
- MeTTa can project or eliminate alternatives
- exactness improves when signature constraints are available

`scale_sensitive`:

- proposal quality dominates
- MeTTa can audit but not invent the solution
- teacher candidates or external solvers are needed

`interpretability_only`:

- scalar reward is not the main output
- item vectors, subscales, or profile deltas are the evidence

## Export Rules

Pure-TRM-Trainer exports:

- `route_error`
- `retrieval_miss`
- `validate_failure`
- `repair_success`
- `repair_failure`
- `critic_false_positive`
- `critic_false_negative`
- `commit_error`

PrimeLab exports:

- env baseline receipt
- rollout trace
- rubric failure cluster
- candidate set
- teacher candidate receipt
- QLoRA conveyor manifest

Paper exports:

- circuit diagram text
- evidence class
- claim boundary
- artifact links
- next live eval
