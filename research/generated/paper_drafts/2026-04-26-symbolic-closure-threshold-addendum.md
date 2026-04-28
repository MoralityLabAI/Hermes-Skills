# Addendum: Symbolic Closure Thresholds For MeTTa/TRM Skill Circuits

Status: draft addendum  
Date: April 26, 2026

## Thesis

The strongest compactification claim is not that a small LLM preserves all large-model capability. The stronger and more defensible claim is that MeTTa-scaffolded TRM circuits can shift the LLM from executor to proposer whenever the task exposes enough verifier-visible state for symbolic gates to route, validate, repair, and commit the final action.

In this framing, model scale matters most before symbolic closure. Once a task can be decomposed into explicit gates, the LLM only needs to emit recoverable atoms: a tool intent, a choice label, a complete node set, a plausible grid, or a candidate answer. The circuit then becomes the executor.

## Threshold Eval

The deterministic threshold suite at [symbolic_closure_threshold.results.md](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\symbolic_closure_threshold_suite\symbolic_closure_threshold.results.md>) evaluates four proposal tiers: `none`, `weak_surface`, `partial_semantic`, and `full_candidate`. It uses zero model calls, so it is a control-plane threshold test rather than a live model benchmark.

| Env family | Direct avg | MeTTa/TRM circuit avg | Min exact circuit tier | Interpretation |
| --- | ---: | ---: | --- | --- |
| `tool_contract_router` | `0.2500` | `0.5000` | `partial_semantic` | Intent plus schema atoms are enough for exact JSON commit. |
| `choice_contract` | `0.2500` | `0.5000` | `partial_semantic` | The LLM only needs to expose a recoverable answer label. |
| `ascii_tree_deep` | `0.4979` | `0.5729` | `partial_semantic` | Complete node coverage lets the circuit own formatting. |
| `intellect3_camp_gate` | `0.6406` | `0.6719` | `partial_semantic` | A plausible grid signature can be projected to an exact gated solution. |
| `math_answer_search` | `0.2500` | `0.2500` | `full_candidate` | Without the answer candidate or a solver, the circuit cannot invent the result. |

The accompanying MeTTa contract is [symbolic_closure_threshold_contract.metta](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\symbolic_closure_threshold_suite\symbolic_closure_threshold_contract.metta>).

## Methodological Implication

This suggests a fifth layer above the existing role taxonomy: a `Flow TRM` or `Circuit TRM`. Its object is not a single answer style or verifier role, but the control flow of the skill:

`observe -> route -> retrieve -> propose -> validate -> repair -> veto/commit -> log`

Each gate produces typed supervision. That changes dataset curation from opaque transcript collection into targeted row production:

- `route_error`: wrong TRM specialization selected.
- `proposal_error`: no candidate with enough verifier-visible atoms.
- `constraint_error`: candidate violates a schema or output contract.
- `repair_success`: symbolic repair recovers an exact action.
- `repair_failure`: symbolic repair cannot recover semantics.
- `critic_false_positive`: verifier accepts a bad candidate.
- `critic_false_negative`: verifier rejects a good candidate.
- `commit_error`: good candidate exists but the wrong branch is emitted.

This is the paper-facing reason MeTTa matters. It is not just an alternate prompt language. It is a circuit grammar for decomposing skill execution into trainable gates and making every gate emit curation labels.

## Claim Boundary

The suite supports a compactification claim for verifier-visible environments: contracts, schemas, tool calls, structured maps, and some logic-grid manifolds. It does not support a claim that MeTTa/TRM replaces latent search in open-ended math, factual QA, or broad reasoning. In those settings, the circuit needs either a stronger proposal model, teacher candidates, or an external solver.

The next publishable experiment should replace the synthetic proposal tiers with live local 3B proposal logs, classify each proposal by tier, and report how often each environment family crosses symbolic closure without needing a full exact answer from the LLM.
