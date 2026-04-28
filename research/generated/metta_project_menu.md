# MeTTa Project Menu

Generated: `2026-04-28T14:50:48.199857+00:00`

This is the working menu for MeTTa-based follow-on projects. It is a synthesis artifact, not a new benchmark run.

## Source Inputs

- `scale_transfer_map`: [research\generated\metta_trm_scale_transfer_map.json](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_trm_scale_transfer_map.json>)
- `fork_plan`: [research\generated\metta_eval_meta_skill_fork_plan.json](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_eval_meta_skill_fork_plan.json>)
- `composition_plan`: [research\generated\metta_composition_plan.json](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_composition_plan.json>)

## Priority Menu

| Priority | Project | Best first artifact | Success metric | Claim boundary |
| ---: | --- | --- | --- | --- |
| 1 | `real_tool_contract_router` | A 30-60 row real-tool trace suite covering repo search, file lookup, shell-safe commands, calendar-like scheduling, weather-like queries, and JSON argument traps. | At least +0.20 absolute exact tool-call validity over baseline with zero schema-invalid commits on held-out tools. | MeTTa/TRM improves control-plane tool-use reliability when tool schemas and arguments are verifier-visible. |
| 2 | `mixed_contract_compactification` | A 50-row held-out mixed-contract dataset with explicit failure labels, exact validators, and near-miss cases. | Runtime+repair wins on exact contract validity without reducing semantic correctness on choice or summary rows. | Small LLMs can act as proposal engines when explicit symbolic gates own observable output contracts. |
| 3 | `logic_signature_camp_gate` | A tiny Campsite-style micro-suite with puzzle constraints, row/column signatures derivable from the prompt, and proposal-tier labels. | Improved cell accuracy and exactness over raw proposals, with an audit column proving no target answer signatures were imported. | Symbolic amplification can help hard logic only after the model emits enough verifier-visible state. |
| 4 | `psycho_item_vector_stability` | Repeated profile probes with item vectors, BFI subscale deltas, stability bands, and repair provenance. | Lower profile variance or clearer target-profile adherence without merely clipping every response to a safe midpoint. | MeTTa/TRM can expose and control psychometric response geometry even when scalar reward barely moves. |
| 5 | `math_teacher_candidate_auditor` | A teacher-candidate bank with multiple proposed answers per item, numeric error archetypes, boxed-answer validators, and abstain labels. | Better candidate selection than keyword or always-first baselines while preserving a clear no-small-model-solve claim boundary. | For hard math, MeTTa/TRM is useful as an auditor and protocol gate, not as a substitute solver. |
| 6 | `safety_abstain_router` | A transparent route-only abstain-vs-answer dataset with borderline cases and separate advice-quality labels. | Improved route/format reliability without claiming medical, security, or legal answer quality. | MeTTa/TRM can enforce safety routing contracts, but high-stakes answer quality remains scale- and domain-sensitive. |
| 7 | `mcp_lookup_efficiency` | A benchmark over filesystem, GitHub, Postgres, and PrimeHub-schema MCP examples with call-count and token-load metrics. | Fewer calls and fewer loaded tokens before first useful answer at equal or better answer correctness. | TRM rows can compactify tool/resource lookup when the target is stable handles rather than raw memorized answers. |
| 8 | `live_symbolic_closure_threshold` | A proposal-tier classifier applied to local 3B logs across tool routing, contracts, ASCII tree, camp-gate, and math. | A clear threshold curve showing where the LLM becomes mostly a proposal generator and where it still needs scale. | The compactification threshold is measurable as the amount of verifier-visible state emitted before symbolic execution takes over. |

## Recommended Start

Start with `real_tool_contract_router` and `mixed_contract_compactification` as the first pair. They are the cleanest compactification lanes: the failure state is observable, validators can be exact, and local 3B runs can produce meaningful with/without-MeTTa deltas without making a broad reasoning claim.

Keep `logic_signature_camp_gate` as the first hard-env follow-up. It is potentially higher-impact, but only if the micro-suite is leakage-safe and the proposal-tier labels prove the model emitted enough verifier-visible state.

Use `math_teacher_candidate_auditor` as the negative/control lane. It should strengthen the paper by showing where the method stops replacing scale and starts requiring teacher candidates.

## Project Details

### 1. `real_tool_contract_router`

- Title: Real Tool-Contract Router
- Thesis: Move the synthetic tool-router win onto real Hermes-style tool calls where MeTTa owns schema memory, argument validation, and commit gating.
- Why now: The synthetic 3B result is already clean, but the claim is too narrow until it survives real tool diversity.
- Env families: `synthetic_tool_router`, `pydantic_adherence`
- Source forks: `metta-structured-contract-repair-lane`
- Source circuits: `tool_schema_composition_circuit`
- First artifact: A 30-60 row real-tool trace suite covering repo search, file lookup, shell-safe commands, calendar-like scheduling, weather-like queries, and JSON argument traps.
- First experiment: Run baseline vs pure_trm vs metta_runtime vs metta_runtime_repair on a small local model and score valid tool choice, valid JSON, argument exactness, and first-useful-hit rate.
- Success metric: At least +0.20 absolute exact tool-call validity over baseline with zero schema-invalid commits on held-out tools.
- Stop rule: If MeTTa only fixes JSON syntax while selecting the wrong tool family, split router and argument-repair TRMs before expanding.
- Paper claim: MeTTa/TRM improves control-plane tool-use reliability when tool schemas and arguments are verifier-visible.
- Benchmark arms: `baseline`, `metta_runtime`, `metta_runtime_repair`, `pure_trm`
- MeTTa gates: `METTA_FIELD_TYPE_VALIDATE`, `METTA_SCHEMA_MEMORY`, `TRM_ARGUMENT_NORMALIZE`, `TRM_DEFAULT_POLICY_REPAIR`, `TRM_JSON_COMMIT_GATE`, `TRM_SCHEMA_PARSE`, `TRM_TOOL_INTENT_CLASSIFY`, `argument_validate_gate`, `canonical_repair_gate`, `commit_gate`, `contract_select_gate`, `field_validate_gate`, `json_repair_gate`, `schema_memory_gate`, `tool_route_gate`

Evidence anchors:
- `synthetic_tool_router`: scale_independent_positive; Local Qwen2.5-3B Q4: 0.0000/1.0000/1.0000 for no-MeTTa/runtime/runtime+repair. Next: Replace synthetic cases with real Hermes tool calls from repo, calendar, shell-safe search, and weather-like APIs.
- `pydantic_adherence`: likely_scale_independent_positive; Structured-map study reaches 1.0 reward; richer packet stayed 1.0 with and without MeTTa. Fresh local Qwen2.5-3B Q4 hard-schema probe: without_metta 0.0000, with_metta_runtime 1.0000, repair 1.0000. Next: Create harder schema variants with missing optional fields, enum traps, nested arrays, and adversarial dates.

### 2. `mixed_contract_compactification`

- Title: Mixed Contract Compactification Suite
- Thesis: Unify instruction constraints, pydantic objects, ASCII trees, choice labels, and IFEval-style literal contracts into one small-model compactification benchmark.
- Why now: The strongest positive evidence is scattered across format and schema envs; a mixed suite makes the methodology harder to dismiss as one-off repair.
- Env families: `if_summarize_judge`, `pydantic_adherence`, `ascii_tree`, `ifeval_contract_family`, `boolq_choice_contract`
- Source forks: `metta-structured-contract-repair-lane`
- Source circuits: `contract_compactification_circuit`
- First artifact: A 50-row held-out mixed-contract dataset with explicit failure labels, exact validators, and near-miss cases.
- First experiment: Evaluate no-MeTTa, prompt-only MeTTa, repair-only MeTTa, and runtime+repair MeTTa against the same validators.
- Success metric: Runtime+repair wins on exact contract validity without reducing semantic correctness on choice or summary rows.
- Stop rule: If gains come only from deterministic postprocessing, label the result as verifier-owned repair rather than TRM training lift.
- Paper claim: Small LLMs can act as proposal engines when explicit symbolic gates own observable output contracts.
- Benchmark arms: `baseline`, `metta_runtime`, `metta_runtime_repair`, `pure_trm`
- MeTTa gates: `METTA_ALLOWED_LABEL_VALIDATE`, `METTA_CONTRACT_SELECT`, `METTA_FIELD_TYPE_VALIDATE`, `METTA_PARENT_CHILD_VALIDATE`, `METTA_REPAIR_EXACT_COUNT`, `TRM_ABSTAIN_OR_COMMIT`, `TRM_ASCII_INDENT_REPAIR`, `TRM_CHOICE_SET_PARSE`, `TRM_COMMIT_FASTPATH`, `TRM_CONSISTENCY_CHECK`, `TRM_CONSTRAINT_CLASSIFY`, `TRM_COVERAGE_COMMIT`, `TRM_DEFAULT_POLICY_REPAIR`, `TRM_INSTRUCTION_FAMILY_CLASSIFY`, `TRM_JSON_COMMIT_GATE`, `TRM_LITERAL_CONSTRAINT_VERIFY`, `TRM_NODE_LIST_PARSE`, `TRM_OUTPUT_METRIC_EXTRACT`, `TRM_REPAIR_OR_ABSTAIN`, `TRM_SCHEMA_PARSE`, `canonical_repair_gate`, `commit_gate`, `contract_select_gate`, `field_validate_gate`, `learning_gate`, `repair_gate`, `route_gate`, `validate_gate`

Evidence anchors:
- `if_summarize_judge`: scale_independent_positive; 0.8B HF 0.3333/0.3333/1.0000; SmolLM3-3B 0.0000/0.0000/1.0000; Qwen2.5-3B Q4 tok64 v2 0.0000/0.0000/1.0000 for no-MeTTa/runtime/runtime+repair. Next: Expand from three local seeds to a 20-50 row mixed constraint suite with held-out constraint families.
- `pydantic_adherence`: likely_scale_independent_positive; Structured-map study reaches 1.0 reward; richer packet stayed 1.0 with and without MeTTa. Fresh local Qwen2.5-3B Q4 hard-schema probe: without_metta 0.0000, with_metta_runtime 1.0000, repair 1.0000. Next: Create harder schema variants with missing optional fields, enum traps, nested arrays, and adversarial dates.
- `ascii_tree`: likely_scale_independent_positive_with_ceiling; Structured-map study: ascii_tree 0.0 -> 0.8; richer packet with/without MeTTa both 0.8. Fresh local Qwen2.5-3B Q4 deep-tree probe: without_metta 0.6000, with_metta_runtime 0.0500, repair 1.0000. Next: Add deeper trees, sibling ordering traps, missing-node penalties, and exact wrapper validation.
- `ifeval_contract_family`: scale_independent_candidate; Local TRM-router benchmark reports gated contract success 1.0000 for allenai_ifeval, while pack columns were mostly zero/bridge-limited. Fresh local Qwen2.5-3B Q4 literal-count probe: without_metta 0.0000, runtime 0.0000, repair 1.0000. Next: Run a local 3B deterministic IFEval subset with per-constraint failure labels.
- `boolq_choice_contract`: narrow_scale_independent_candidate; Trainer-policy mining rerun: boolq/qwen35_27b/two-model-contract-repair-v1 moved 0.0 -> 1.0; wider family only 1 contract win across 22 comparisons. Next: Use as a small-model contract-control lane with semantic correctness separated from label validity.

### 3. `logic_signature_camp_gate`

- Title: Leakage-Safe Logic Signature Gate
- Thesis: Test whether MeTTa signature checks can amplify weak Intellect-3 logic proposals without using target-grid leakage.
- Why now: The C-signature projection result is large, but the next claim needs puzzle-provided constraints only.
- Env families: `intellect3_logic_camp_gate`
- Source forks: `metta-intellect3-logic-signature-gate`
- Source circuits: `intellect3_logic_signature_circuit`
- First artifact: A tiny Campsite-style micro-suite with puzzle constraints, row/column signatures derivable from the prompt, and proposal-tier labels.
- First experiment: Run local 3B proposals, classify partial-semantic vs full-candidate tiers, then apply MeTTa min-edit projection only from prompt-derived constraints.
- Success metric: Improved cell accuracy and exactness over raw proposals, with an audit column proving no target answer signatures were imported.
- Stop rule: If 3B proposals lack enough grid atoms for projection, switch this lane to 9B/27B or teacher-proposal mode.
- Paper claim: Symbolic amplification can help hard logic only after the model emits enough verifier-visible state.
- Benchmark arms: `baseline`, `metta_runtime_repair`, `pure_trm`
- MeTTa gates: `METTA_MIN_EDIT_C_PROJECTION`, `TRM_CAMP_ROW_COL_SIGNATURE`, `TRM_COMMIT_GRID`, `TRM_PARSE_GRID`, `commit_gate`, `constraint_parse_gate`, `min_edit_projection_gate`, `proposal_gate`, `signature_validate_gate`

Evidence anchors:
- `intellect3_logic_camp_gate`: scale_sensitive_but_symbolically_amplifiable; 27B/109 logic_skill_trm original exact 0.3028; C-only projection exact 0.6789; avg cell accuracy 0.8787 -> 0.9340. Next: Run local 3B on a tiny Campsite micro-suite to test whether weak proposals still contain enough T/C structure for projection.

### 4. `psycho_item_vector_stability`

- Title: PsychoBench Item-Vector Stability
- Thesis: Replace scalar PsychoBench reward chasing with item-vector, subscale, and profile-stability instrumentation.
- Why now: The scalar lift is tiny, but the existing evidence shows MeTTa changes item geometry; that is a better research object.
- Env families: `psycho_bench`
- Source forks: `metta-psycho-item-vector-stability`
- Source circuits: `psycho_item_vector_composition_circuit`
- First artifact: Repeated profile probes with item vectors, BFI subscale deltas, stability bands, and repair provenance.
- First experiment: Run repeated local 3B and later 9B/27B probes, then compare variance and subscale drift across with/without MeTTa.
- Success metric: Lower profile variance or clearer target-profile adherence without merely clipping every response to a safe midpoint.
- Stop rule: If MeTTa reduces variance by collapsing personality signal, treat as over-regularization and redesign gates.
- Paper claim: MeTTa/TRM can expose and control psychometric response geometry even when scalar reward barely moves.
- Benchmark arms: `baseline`, `metta_runtime`, `pure_trm`
- MeTTa gates: `METTA_PROFILE_DELTA_AUDIT`, `TRM_BFI_SUBSCALE_PROJECTOR`, `TRM_LIKERT_ITEM_VECTOR_CONTRACT`, `TRM_STABILITY_GATE`, `item_vector_validate_gate`, `profile_delta_audit_gate`, `stability_commit_gate`, `subscale_project_gate`

Evidence anchors:
- `psycho_bench`: nuanced_scalar_not_enough; Richer-packet run reward 3.3283 -> 3.3311; both arms pass 44/44 item contract; MeTTa changes 4 items and shifts neuroticism +0.2500. Next: Run repeated local 3B and 9B profile probes, score variance, and compare subscale drift instead of only aggregate reward.

### 5. `math_teacher_candidate_auditor`

- Title: Math Teacher-Candidate Auditor
- Thesis: Use MeTTa/TRM as a candidate auditor for hard math rather than pretending small models solve 100B-class problems.
- Why now: Math is the clearest negative boundary; turning it into a teacher-candidate audit lane strengthens the paper.
- Env families: `aime_boxed_answer`, `intellect3_math_router`
- Source forks: `metta-intellect3-math-teacher-auditor`
- Source circuits: `intellect3_math_teacher_auditor_circuit`
- First artifact: A teacher-candidate bank with multiple proposed answers per item, numeric error archetypes, boxed-answer validators, and abstain labels.
- First experiment: Compare keyword routing, pure TRM candidate routing, and MeTTa invariant/boxed-answer auditing on candidate selection accuracy.
- Success metric: Better candidate selection than keyword or always-first baselines while preserving a clear no-small-model-solve claim boundary.
- Stop rule: If teacher candidates are mostly wrong or indistinguishable, collect better candidate diversity before training auditors.
- Paper claim: For hard math, MeTTa/TRM is useful as an auditor and protocol gate, not as a substitute solver.
- Benchmark arms: `baseline`, `pure_trm`, `teacher_candidate_metta`
- MeTTa gates: `METTA_MOD_1000_VALIDATE`, `METTA_REGRET_AUDIT`, `TRM_BOXED_PARSE`, `TRM_NUMERIC_COMMIT`, `TRM_NUMERIC_ERROR_ARCHETYPE`, `TRM_PARSE_INTEGER_CANDIDATES`, `TRM_ROUTE_TRM_CANDIDATE`, `TRM_TEACHER_CANDIDATE_ROUTE`, `candidate_parse_gate`, `invariant_validate_gate`, `numeric_error_gate`, `teacher_candidate_commit_gate`

Evidence anchors:
- `aime_boxed_answer`: format_transfers_reasoning_does_not; Local TRM-router benchmark reports gated boxed exact rate 1.0000, but hard-math live columns were bridge-limited or zero. Next: Separate answer-format extraction from actual AIME solve quality; use teacher candidates for the latter.
- `intellect3_math_router`: scale_sensitive_negative_boundary; 27B offline replay: current final 0.0700, hidden TRM candidate 0.1050, generic guard 0.1100. Local 3B first-5 smoke: vanilla 0.4000, always_trm 0.2000, generic guard 0.2000. Next: Use math as a negative-control lane and collect teacher candidates rather than relying on small-model TRM generations.

### 6. `safety_abstain_router`

- Title: Safety Abstain Router
- Thesis: Evaluate routing and refusal-format reliability separately from high-stakes advice quality.
- Why now: The route-only signal may transfer to small models, but the domain boundary must be explicit.
- Env families: `safety_abstain_family`
- Source forks: none
- Source circuits: `safety_abstain_veto_circuit`
- First artifact: A transparent route-only abstain-vs-answer dataset with borderline cases and separate advice-quality labels.
- First experiment: Score route accuracy, refusal format validity, false abstains, false answers, and advice-quality abstentions separately.
- Success metric: Improved route/format reliability without claiming medical, security, or legal answer quality.
- Stop rule: If the model gives unsafe substantive content after correct routing, add a separate safe-completion verifier before expanding.
- Paper claim: MeTTa/TRM can enforce safety routing contracts, but high-stakes answer quality remains scale- and domain-sensitive.
- Benchmark arms: `baseline`, `metta_runtime`, `pure_trm`
- MeTTa gates: `METTA_POLICY_ROUTE`, `TRM_REFUSAL_FORMAT_VALIDATE`, `TRM_RISK_CLASSIFY`, `TRM_SAFE_COMPLETION_COMMIT`, `abstain_or_answer_gate`, `commit_gate`, `policy_validate_gate`, `risk_route_gate`, `safe_format_gate`

Evidence anchors:
- `safety_abstain_family`: candidate_unknown; Pack includes medsafetybench, jailbreak_bench, wmdp with abstain-guard variants. Fresh local Qwen2.5-3B Q4 obvious-route probe: without_metta 0.0000, with_metta_runtime 1.0000, repair 1.0000. Next: Expand the local abstain-vs-answer suite with transparent labels, borderline cases, and separate advice-quality scoring.

### 7. `mcp_lookup_efficiency`

- Title: TRM-MCP Lookup Efficiency
- Thesis: Turn MCP resource surfaces into short TRM rows for route, retrieve, verify, and first-useful-hit optimization.
- Why now: This is the most general infrastructure project and pairs naturally with tool-schema work.
- Env families: `mcp_lookup_surface`
- Source forks: `metta-flow-trm-circuit-controller`
- Source circuits: `tool_schema_composition_circuit`
- First artifact: A benchmark over filesystem, GitHub, Postgres, and PrimeHub-schema MCP examples with call-count and token-load metrics.
- First experiment: Compare plain resource scan, cached index lookup, TRM route/retrieve, and MeTTa verifier-gated retrieve.
- Success metric: Fewer calls and fewer loaded tokens before first useful answer at equal or better answer correctness.
- Stop rule: If the resource surface is tiny, skip TRM and use direct scan; the project only matters on large or heterogeneous MCPs.
- Paper claim: TRM rows can compactify tool/resource lookup when the target is stable handles rather than raw memorized answers.
- Benchmark arms: `baseline`, `metta_runtime`, `metta_runtime_repair`, `pure_trm`
- MeTTa gates: `argument_validate_gate`, `commit_gate`, `json_repair_gate`, `learning_gate`, `repair_gate`, `route_gate`, `schema_memory_gate`, `tool_route_gate`, `validate_gate`

### 8. `live_symbolic_closure_threshold`

- Title: Live Symbolic Closure Threshold
- Thesis: Replace deterministic proposal-tier simulations with observed local-model proposal tiers across env families.
- Why now: The control-plane result is conceptually important, but it needs live proposal distributions to become empirical.
- Env families: `symbolic_closure_threshold_suite`
- Source forks: `metta-flow-trm-circuit-controller`
- Source circuits: `contract_compactification_circuit`, `intellect3_logic_signature_circuit`
- First artifact: A proposal-tier classifier applied to local 3B logs across tool routing, contracts, ASCII tree, camp-gate, and math.
- First experiment: Measure how often the model emits none, weak_surface, partial_semantic, or full_candidate state, then map which gates can close each case.
- Success metric: A clear threshold curve showing where the LLM becomes mostly a proposal generator and where it still needs scale.
- Stop rule: If tier labels are unstable across annotators or validators, formalize the label grammar before adding more envs.
- Paper claim: The compactification threshold is measurable as the amount of verifier-visible state emitted before symbolic execution takes over.
- Benchmark arms: `baseline`, `metta_runtime`, `metta_runtime_repair`, `pure_trm`
- MeTTa gates: `METTA_VALIDATE_GATE`, `TRM_COMMIT_GATE`, `TRM_LEARNING_GATE`, `TRM_REPAIR_GATE`, `TRM_ROUTE_GATE`, `commit_gate`, `constraint_parse_gate`, `contract_select_gate`, `learning_gate`, `min_edit_projection_gate`, `proposal_gate`, `repair_gate`, `route_gate`, `signature_validate_gate`, `validate_gate`

Evidence anchors:
- `symbolic_closure_threshold_suite`: control_plane_threshold_eval; Deterministic threshold suite: MeTTa/TRM circuit exact at `partial_semantic` tier for tool routing, choice contracts, ASCII tree, and camp-gate projection; math exactness remains `full_candidate` only. Next: Replace synthetic proposal tiers with live local 3B proposal logs and measure the observed tier distribution per env family.

## First Sprint Cut

| Step | Output | Why |
| ---: | --- | --- |
| 1 | `research/studies/.../real_tool_contract_router/` trace suite | Converts the synthetic result into a real tool-use claim. |
| 2 | `research/studies/.../mixed_contract_compactification/` validators | Gives the paper a unified compactification benchmark. |
| 3 | `research/studies/.../logic_signature_camp_gate/` leakage audit | Tests the hard-env amplification claim without target leakage. |
| 4 | Update paper appendix tables from the new runs | Keeps methodology claims aligned with evidence class. |

## Claim Discipline

- Positive compactification claims require exact validators, held-out rows, and separate semantic-vs-format scoring.
- Hard-logic claims require an explicit leakage audit and prompt-derived constraints only.
- Math claims should be framed as candidate auditing or protocol validation unless a larger solver supplies the candidate set.
- PsychoBench claims should report item vectors, subscale drift, and stability instead of scalar reward alone.
