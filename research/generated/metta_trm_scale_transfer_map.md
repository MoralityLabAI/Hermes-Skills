# MeTTa/TRM Scale-Transfer Map

Generated: `2026-04-26T15:17:31.802285+00:00`

This appendix map classifies where MeTTa-scaffolded, TRM-infused skills are likely to transfer across model scale and where they depend on base-model competence.

## Core Boundary

- Scale-independent pattern: observable contract, schema, routing, repair, or verifier state is the bottleneck.
- Scale-sensitive pattern: the bottleneck is raw latent problem solving, missing arithmetic, or missing domain knowledge.
- Nuanced pattern: scalar reward is too coarse, so the env needs item/vector/subcomponent decomposition before claiming improvement.

## Ranked Env Families

| Rank | Env family | Scale class | Bottleneck | Candidate skill | Current line | Next eval |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `if_summarize_judge` | `scale_independent_positive` | exact structural constraint enforcement | `Hermes/Instruction-Constraint-Repair-v1` | Small models fail raw formatting but deterministic MeTTa repair can own the observable contract. | Expand from three local seeds to a 20-50 row mixed constraint suite with held-out constraint families. |
| 2 | `synthetic_tool_router` | `scale_independent_positive` | tool schema selection and JSON argument contract | `Hermes/Tool-Contract-Router-v1` | The LLM can be a weak proposal engine when MeTTa owns schema memory and exact validation. | Replace synthetic cases with real Hermes tool calls from repo, calendar, shell-safe search, and weather-like APIs. |
| 3 | `pydantic_adherence` | `likely_scale_independent_positive` | typed object emission and field-level validation | `Hermes/Pydantic-Schema-Repair-v1` | Once the schema and canonical target shape are explicit, a 3B model can satisfy hard typed validation; the ceiling hides gains on easy cases. | Create harder schema variants with missing optional fields, enum traps, nested arrays, and adversarial dates. |
| 4 | `ascii_tree` | `likely_scale_independent_positive_with_ceiling` | hierarchical formatting and node coverage | `Hermes/Ascii-Tree-Structure-v1` | MeTTa prompts can regress formatting if the model emits flattened trees, but a canonical tree repair gate gives exact structure. | Add deeper trees, sibling ordering traps, missing-node penalties, and exact wrapper validation. |
| 5 | `symbolic_closure_threshold_suite` | `control_plane_threshold_eval` | minimum proposal information required before symbolic gates can own execution | `Hermes/MeTTa-TRM-Circuit-Executor-v1` | The LLM becomes an idea spinner when it emits enough verifier-visible atoms; the circuit executes, repairs, and commits the final action. | Replace synthetic proposal tiers with live local 3B proposal logs and measure the observed tier distribution per env family. |
| 6 | `ifeval_contract_family` | `scale_independent_candidate` | instruction-family classification and output contract choice | `Hermes/IFEval-Contract-Router-v1` | This transfers when MeTTa owns literal repair; prompt-only runtime is insufficient because the model appends or miscounts tokens. | Run a local 3B deterministic IFEval subset with per-constraint failure labels. |
| 7 | `boolq_choice_contract` | `narrow_scale_independent_candidate` | binary/multiple-choice answer contract | `Hermes/Choice-Contract-Repair-v1` | Choice-contract repair is real but narrow; it should be treated as a contract win, not comprehension gain. | Use as a small-model contract-control lane with semantic correctness separated from label validity. |
| 8 | `intellect3_logic_camp_gate` | `scale_sensitive_but_symbolically_amplifiable` | symbolic grid state verification and camp placement signatures | `Hermes/Intellect-3-Logic-CampGate-v1` | TRM must supply a plausible grid, but MeTTa can strongly amplify it when failures are row/column signature errors. | Run local 3B on a tiny Campsite micro-suite to test whether weak proposals still contain enough T/C structure for projection. |
| 9 | `psycho_bench` | `nuanced_scalar_not_enough` | latent profile stability and item-level response contract | `Hermes/PsychoBench-ItemVector-v1` | Tiny scalar gains need item/subscale decomposition; MeTTa may change profile geometry rather than obvious correctness. | Run repeated local 3B and 9B profile probes, score variance, and compare subscale drift instead of only aggregate reward. |
| 10 | `aime_boxed_answer` | `format_transfers_reasoning_does_not` | answer extraction and boxed-format validation around hard math | `Hermes/AIME-Boxed-Answer-Gate-v1` | MeTTa can enforce boxed answer protocol, but cannot create the missing mathematical solution at small scale. | Separate answer-format extraction from actual AIME solve quality; use teacher candidates for the latter. |
| 11 | `intellect3_math_router` | `scale_sensitive_negative_boundary` | raw arithmetic/problem-solving competence plus candidate routing | `Hermes/Intellect-3-Math-Router-v1` | Routing can recover hidden good candidates at 27B scale, but the 3B TRM candidate quality is too weak on the tested slice. | Use math as a negative-control lane and collect teacher candidates rather than relying on small-model TRM generations. |
| 12 | `safety_abstain_family` | `candidate_unknown` | risk classification and abstain/answer routing | `Hermes/Safety-Abstain-Router-v1` | Obvious policy routing transfers to 3B when reduced to a JSON route contract, but factual medical/security advice remains scale- and domain-sensitive. | Expand the local abstain-vs-answer suite with transparent labels, borderline cases, and separate advice-quality scoring. |

## Evidence And Gates

### `if_summarize_judge`

- Candidate skill: `Hermes/Instruction-Constraint-Repair-v1`
- Scale class: `scale_independent_positive`
- Evidence: 0.8B HF 0.3333/0.3333/1.0000; SmolLM3-3B 0.0000/0.0000/1.0000; Qwen2.5-3B Q4 tok64 v2 0.0000/0.0000/1.0000 for no-MeTTa/runtime/runtime+repair.
- Claim boundary: Strong for exact output-form constraints; not evidence of deeper reasoning improvement.
- Recommended gates: `TRM_CONSTRAINT_CLASSIFY`, `TRM_OUTPUT_METRIC_EXTRACT`, `METTA_REPAIR_EXACT_COUNT`, `TRM_COMMIT_FASTPATH`

### `synthetic_tool_router`

- Candidate skill: `Hermes/Tool-Contract-Router-v1`
- Scale class: `scale_independent_positive`
- Evidence: Local Qwen2.5-3B Q4: 0.0000/1.0000/1.0000 for no-MeTTa/runtime/runtime+repair.
- Claim boundary: Current evidence is controlled/synthetic; needs real tool diversity before broad tool-calling claims.
- Recommended gates: `TRM_TOOL_INTENT_CLASSIFY`, `METTA_SCHEMA_MEMORY`, `TRM_ARGUMENT_NORMALIZE`, `TRM_JSON_COMMIT_GATE`

### `pydantic_adherence`

- Candidate skill: `Hermes/Pydantic-Schema-Repair-v1`
- Scale class: `likely_scale_independent_positive`
- Evidence: Structured-map study reaches 1.0 reward; richer packet stayed 1.0 with and without MeTTa. Fresh local Qwen2.5-3B Q4 hard-schema probe: without_metta 0.0000, with_metta_runtime 1.0000, repair 1.0000.
- Claim boundary: Current row is ceilinged; needs harder cases to detect improvement.
- Recommended gates: `TRM_SCHEMA_PARSE`, `METTA_FIELD_TYPE_VALIDATE`, `TRM_DEFAULT_POLICY_REPAIR`, `TRM_JSON_COMMIT_GATE`

### `ascii_tree`

- Candidate skill: `Hermes/Ascii-Tree-Structure-v1`
- Scale class: `likely_scale_independent_positive_with_ceiling`
- Evidence: Structured-map study: ascii_tree 0.0 -> 0.8; richer packet with/without MeTTa both 0.8. Fresh local Qwen2.5-3B Q4 deep-tree probe: without_metta 0.6000, with_metta_runtime 0.0500, repair 1.0000.
- Claim boundary: Evidence supports structure-sensitive usefulness, not broad reasoning.
- Recommended gates: `TRM_NODE_LIST_PARSE`, `METTA_PARENT_CHILD_VALIDATE`, `TRM_ASCII_INDENT_REPAIR`, `TRM_COVERAGE_COMMIT`

### `symbolic_closure_threshold_suite`

- Candidate skill: `Hermes/MeTTa-TRM-Circuit-Executor-v1`
- Scale class: `control_plane_threshold_eval`
- Evidence: Deterministic threshold suite: MeTTa/TRM circuit exact at `partial_semantic` tier for tool routing, choice contracts, ASCII tree, and camp-gate projection; math exactness remains `full_candidate` only.
- Claim boundary: This is a deterministic control-plane threshold eval with zero model calls, not a live benchmark improvement.
- Recommended gates: `TRM_ROUTE_GATE`, `METTA_VALIDATE_GATE`, `TRM_REPAIR_GATE`, `TRM_COMMIT_GATE`, `TRM_LEARNING_GATE`

### `ifeval_contract_family`

- Candidate skill: `Hermes/IFEval-Contract-Router-v1`
- Scale class: `scale_independent_candidate`
- Evidence: Local TRM-router benchmark reports gated contract success 1.0000 for allenai_ifeval, while pack columns were mostly zero/bridge-limited. Fresh local Qwen2.5-3B Q4 literal-count probe: without_metta 0.0000, runtime 0.0000, repair 1.0000.
- Claim boundary: Existing evidence is router-benchmark, not direct live environment reward.
- Recommended gates: `TRM_INSTRUCTION_FAMILY_CLASSIFY`, `METTA_CONTRACT_SELECT`, `TRM_LITERAL_CONSTRAINT_VERIFY`, `TRM_REPAIR_OR_ABSTAIN`

### `boolq_choice_contract`

- Candidate skill: `Hermes/Choice-Contract-Repair-v1`
- Scale class: `narrow_scale_independent_candidate`
- Evidence: Trainer-policy mining rerun: boolq/qwen35_27b/two-model-contract-repair-v1 moved 0.0 -> 1.0; wider family only 1 contract win across 22 comparisons.
- Claim boundary: Narrow `choice_contract` claim only.
- Recommended gates: `TRM_CHOICE_SET_PARSE`, `METTA_ALLOWED_LABEL_VALIDATE`, `TRM_ABSTAIN_OR_COMMIT`, `TRM_CONSISTENCY_CHECK`

### `intellect3_logic_camp_gate`

- Candidate skill: `Hermes/Intellect-3-Logic-CampGate-v1`
- Scale class: `scale_sensitive_but_symbolically_amplifiable`
- Evidence: 27B/109 logic_skill_trm original exact 0.3028; C-only projection exact 0.6789; avg cell accuracy 0.8787 -> 0.9340.
- Claim boundary: Post-hoc projection uses known signatures; fresh runs must avoid answer leakage and include puzzle-provided constraints only.
- Recommended gates: `TRM_PARSE_GRID`, `TRM_CAMP_ROW_COL_SIGNATURE`, `METTA_MIN_EDIT_C_PROJECTION`, `TRM_COMMIT_GRID`

### `psycho_bench`

- Candidate skill: `Hermes/PsychoBench-ItemVector-v1`
- Scale class: `nuanced_scalar_not_enough`
- Evidence: Richer-packet run reward 3.3283 -> 3.3311; both arms pass 44/44 item contract; MeTTa changes 4 items and shifts neuroticism +0.2500.
- Claim boundary: Psychometric envs are interpretability/consistency probes, not conventional correctness benchmarks.
- Recommended gates: `TRM_LIKERT_ITEM_VECTOR_CONTRACT`, `TRM_BFI_SUBSCALE_PROJECTOR`, `METTA_PROFILE_DELTA_AUDIT`, `TRM_STABILITY_GATE`

### `aime_boxed_answer`

- Candidate skill: `Hermes/AIME-Boxed-Answer-Gate-v1`
- Scale class: `format_transfers_reasoning_does_not`
- Evidence: Local TRM-router benchmark reports gated boxed exact rate 1.0000, but hard-math live columns were bridge-limited or zero.
- Claim boundary: Good for protocol/answer extraction; not evidence of hard-math competence transfer.
- Recommended gates: `TRM_BOXED_PARSE`, `METTA_MOD_1000_VALIDATE`, `TRM_NUMERIC_COMMIT`, `TRM_TEACHER_CANDIDATE_ROUTE`

### `intellect3_math_router`

- Candidate skill: `Hermes/Intellect-3-Math-Router-v1`
- Scale class: `scale_sensitive_negative_boundary`
- Evidence: 27B offline replay: current final 0.0700, hidden TRM candidate 0.1050, generic guard 0.1100. Local 3B first-5 smoke: vanilla 0.4000, always_trm 0.2000, generic guard 0.2000.
- Claim boundary: Do not claim small-model math improvement; current evidence maps the limit line.
- Recommended gates: `TRM_PARSE_INTEGER_CANDIDATES`, `TRM_NUMERIC_ERROR_ARCHETYPE`, `TRM_ROUTE_TRM_CANDIDATE`, `METTA_REGRET_AUDIT`

### `safety_abstain_family`

- Candidate skill: `Hermes/Safety-Abstain-Router-v1`
- Scale class: `candidate_unknown`
- Evidence: Pack includes medsafetybench, jailbreak_bench, wmdp with abstain-guard variants. Fresh local Qwen2.5-3B Q4 obvious-route probe: without_metta 0.0000, with_metta_runtime 1.0000, repair 1.0000.
- Claim boundary: High-stakes domain; current evidence is routing/format safety only, not advice quality.
- Recommended gates: `TRM_RISK_CLASSIFY`, `METTA_POLICY_ROUTE`, `TRM_REFUSAL_FORMAT_VALIDATE`, `TRM_SAFE_COMPLETION_COMMIT`

## Paper Use

Use this as an appendix table rather than a main-result table. The central paper claim should stay narrow: MeTTa/TRM scaffolding improves the training pipe and runtime behavior when the skill can decompose the task into explicit contracts, gates, and verifier-visible state transitions. The appendix then documents the boundary cases where that does not transfer.

Suggested subsection title: `Appendix: Scale-Dependence Map for Symbolic TRM Scaffolding`.
