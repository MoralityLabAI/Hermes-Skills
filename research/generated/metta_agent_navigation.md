# MeTTa Agent Navigation Guide

Generated: `2026-04-28T14:56:48.100134+00:00`

This guide tells a future agent how to move from the current paper artifacts into the MeTTa project menu without losing claim discipline.

## Source Spine

- `project_menu`: [research\generated\metta_project_menu.json](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_project_menu.json>)
- `paper_data_campaign_plan`: [research\generated\paper_latex\metta_trm_repair_addendum\data_campaign_plan.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_latex\metta_trm_repair_addendum\data_campaign_plan.md>)
- `benchmark_crossref`: [research\generated\trm_infused_baseline_crossref.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\trm_infused_baseline_crossref.md>)

## Claim Router

| Route | User intent | Primary projects | Evidence class | First action | Overclaim risk |
| --- | --- | --- | --- | --- | --- |
| `paper_main_claim_extension` | Extend the current MeTTa/TRM paper with the cleanest next positive evidence. | `mixed_contract_compactification`, `real_tool_contract_router` | `live_or_replay_with_exact_validators` | Create held-out rows and exact validators before adding model runs. | Do not describe format or tool-contract wins as broad reasoning gains. |
| `hard_env_boundary` | Show whether the method transfers to hard logic and where it fails. | `logic_signature_camp_gate`, `live_symbolic_closure_threshold` | `leakage_audited_hard_env_probe` | Write the leakage audit and proposal-tier labels before scoring improvements. | Post-hoc projection can look strong while leaking target information; require a prompt-derived signature audit. |
| `negative_control` | Make the paper more credible by showing where MeTTa/TRM does not replace scale. | `math_teacher_candidate_auditor` | `negative_control_or_teacher_candidate_audit` | Build or import a teacher-candidate bank with numeric validators and error archetypes. | Do not claim small-model math solving unless the model produced the correct candidate unaided. |
| `nuanced_metric_extension` | Develop the psychometric/nuanced benchmark line rather than chase tiny scalar reward lifts. | `psycho_item_vector_stability` | `multi_signal_interpretability_probe` | Run repeated probes and emit item vectors, subscale deltas, and stability bands. | Variance reduction can be over-regularization if the gate collapses personality signal. |
| `tooling_infrastructure` | Build reusable infrastructure for future skills and agents. | `mcp_lookup_efficiency`, `real_tool_contract_router` | `infrastructure_efficiency_benchmark` | Define first-useful-hit, token-load, and call-count metrics before collecting traces. | If the resource surface is tiny, direct scanning is the right baseline and TRM overhead is not justified. |
| `scale_campaign` | Prepare for Snacksack or equivalent 9B/27B matched runs. | `mixed_contract_compactification`, `logic_signature_camp_gate`, `math_teacher_candidate_auditor` | `matched_scale_matrix` | Freeze row IDs, prompt construction, output schema, and validator code before changing models. | Changing row selection or validators between scales makes the trend uninterpretable. |

## Recommended Agent Path

If the user says to continue the paper-adjacent work, choose `paper_main_claim_extension`: start `mixed_contract_compactification` plus `real_tool_contract_router` because both preserve exact validators and small-model compactification claims.

If the user asks for harder envs or generalization, choose `hard_env_boundary`: start `logic_signature_camp_gate`, but freeze the leakage audit before any score table.

If the user asks what makes the claim credible, choose `negative_control`: use `math_teacher_candidate_auditor` to show that MeTTa/TRM audits candidates and protocols but does not replace missing math competence.

If the user asks for new research texture, choose `nuanced_metric_extension`: use `psycho_item_vector_stability` and report item-vector geometry rather than scalar reward.

## Agent Loop

| Step | Name | Output | Check |
| ---: | --- | --- | --- |
| 1 | Classify the requested claim | Select one route_id and one primary project_id. | The selected project must have an evidence class that matches the requested paper claim. |
| 2 | Open the source spine | Read the project menu row, scale-transfer row, fork plan, and composition plan for the selected project. | Record source paths in the new study README so later agents can reproduce the reasoning. |
| 3 | Create a study folder | Use `research/studies/YYYY-MM-DD-<project_id>/` or a project subfolder under the active MeTTa study if it is clearly an extension. | Do not dump large model artifacts into Git unless they are small, interpretable result files. |
| 4 | Freeze rows and validators first | Emit row JSONL, validator code, and a row manifest before running models. | Rows must include split, env_family, expected observable state, and failure labels. |
| 5 | Run the smallest meaningful arms | Start with baseline, pure_trm, metta_runtime, and metta_runtime_repair unless the project defines a different matrix. | For local models, keep memory caps explicit and preserve prompt/output schemas for later 9B/27B runs. |
| 6 | Separate evidence classes | Mark each result as live model, deterministic replay, post-hoc projection, no-model verifier sweep, or control-plane simulation. | Never mix post-hoc projection with live benchmark columns. |
| 7 | Write the paper hook | Add a short findings.md with claim, limitation, metric table, and next run command. | Every positive claim must name the exact verifier-visible state that MeTTa/TRM controlled. |

## Required Study Artifacts

| Path | Purpose |
| --- | --- |
| `README.md` | One-page study index: route, project, source inputs, active claim, and artifact links. |
| `study_plan.md` | Hypothesis, arms, validators, splits, stop rules, and paper claim boundary. |
| `rows/*.jsonl` | Frozen benchmark rows or proposal traces with stable IDs and split labels. |
| `validators/*.py` | Exact validators or metric extractors used before model results are interpreted. |
| `configs/*.json` | Prompt, model, memory, and arm configuration with enough detail for 9B/27B reruns. |
| `results/*.json` | Machine-readable result table with per-row arm scores and evidence_class. |
| `results/*.md` | Human-readable finding with metric table, failure breakdown, and paper-ready claim. |
| `claim_audit.md` | Explicit separation of live, deterministic, post-hoc, and control-plane evidence. |

## Route Details

### `paper_main_claim_extension`

- User intent: Extend the current MeTTa/TRM paper with the cleanest next positive evidence.
- Evidence class: `live_or_replay_with_exact_validators`
- Why this route: These projects keep the claim near the paper's strongest result: explicit symbolic gates expose verifier-visible state and improve small-model control-plane reliability.
- First action: Create held-out rows and exact validators before adding model runs.
- Paper section: Main results extension or short addendum.
- Overclaim risk: Do not describe format or tool-contract wins as broad reasoning gains.

Projects:
- `mixed_contract_compactification`: Mixed Contract Compactification Suite
- First artifact for `mixed_contract_compactification`: A 50-row held-out mixed-contract dataset with explicit failure labels, exact validators, and near-miss cases.
- Success metric for `mixed_contract_compactification`: Runtime+repair wins on exact contract validity without reducing semantic correctness on choice or summary rows.
- Paper claim for `mixed_contract_compactification`: Small LLMs can act as proposal engines when explicit symbolic gates own observable output contracts.
- `real_tool_contract_router`: Real Tool-Contract Router
- First artifact for `real_tool_contract_router`: A 30-60 row real-tool trace suite covering repo search, file lookup, shell-safe commands, calendar-like scheduling, weather-like queries, and JSON argument traps.
- Success metric for `real_tool_contract_router`: At least +0.20 absolute exact tool-call validity over baseline with zero schema-invalid commits on held-out tools.
- Paper claim for `real_tool_contract_router`: MeTTa/TRM improves control-plane tool-use reliability when tool schemas and arguments are verifier-visible.

### `hard_env_boundary`

- User intent: Show whether the method transfers to hard logic and where it fails.
- Evidence class: `leakage_audited_hard_env_probe`
- Why this route: Logic is the plausible hard positive target, but only if prompt-derived constraints, not answer signatures, drive projection.
- First action: Write the leakage audit and proposal-tier labels before scoring improvements.
- Paper section: Boundary and generalization appendix.
- Overclaim risk: Post-hoc projection can look strong while leaking target information; require a prompt-derived signature audit.

Projects:
- `logic_signature_camp_gate`: Leakage-Safe Logic Signature Gate
- First artifact for `logic_signature_camp_gate`: A tiny Campsite-style micro-suite with puzzle constraints, row/column signatures derivable from the prompt, and proposal-tier labels.
- Success metric for `logic_signature_camp_gate`: Improved cell accuracy and exactness over raw proposals, with an audit column proving no target answer signatures were imported.
- Paper claim for `logic_signature_camp_gate`: Symbolic amplification can help hard logic only after the model emits enough verifier-visible state.
- `live_symbolic_closure_threshold`: Live Symbolic Closure Threshold
- First artifact for `live_symbolic_closure_threshold`: A proposal-tier classifier applied to local 3B logs across tool routing, contracts, ASCII tree, camp-gate, and math.
- Success metric for `live_symbolic_closure_threshold`: A clear threshold curve showing where the LLM becomes mostly a proposal generator and where it still needs scale.
- Paper claim for `live_symbolic_closure_threshold`: The compactification threshold is measurable as the amount of verifier-visible state emitted before symbolic execution takes over.

### `negative_control`

- User intent: Make the paper more credible by showing where MeTTa/TRM does not replace scale.
- Evidence class: `negative_control_or_teacher_candidate_audit`
- Why this route: Hard math separates protocol/candidate-auditing gains from missing base-model solving competence.
- First action: Build or import a teacher-candidate bank with numeric validators and error archetypes.
- Paper section: Limitations or scale-boundary appendix.
- Overclaim risk: Do not claim small-model math solving unless the model produced the correct candidate unaided.

Projects:
- `math_teacher_candidate_auditor`: Math Teacher-Candidate Auditor
- First artifact for `math_teacher_candidate_auditor`: A teacher-candidate bank with multiple proposed answers per item, numeric error archetypes, boxed-answer validators, and abstain labels.
- Success metric for `math_teacher_candidate_auditor`: Better candidate selection than keyword or always-first baselines while preserving a clear no-small-model-solve claim boundary.
- Paper claim for `math_teacher_candidate_auditor`: For hard math, MeTTa/TRM is useful as an auditor and protocol gate, not as a substitute solver.

### `nuanced_metric_extension`

- User intent: Develop the psychometric/nuanced benchmark line rather than chase tiny scalar reward lifts.
- Evidence class: `multi_signal_interpretability_probe`
- Why this route: PsychoBench needs item-vector, subscale, and stability analysis; scalar reward alone hides the interesting effect.
- First action: Run repeated probes and emit item vectors, subscale deltas, and stability bands.
- Paper section: Nuanced benchmark appendix.
- Overclaim risk: Variance reduction can be over-regularization if the gate collapses personality signal.

Projects:
- `psycho_item_vector_stability`: PsychoBench Item-Vector Stability
- First artifact for `psycho_item_vector_stability`: Repeated profile probes with item vectors, BFI subscale deltas, stability bands, and repair provenance.
- Success metric for `psycho_item_vector_stability`: Lower profile variance or clearer target-profile adherence without merely clipping every response to a safe midpoint.
- Paper claim for `psycho_item_vector_stability`: MeTTa/TRM can expose and control psychometric response geometry even when scalar reward barely moves.

### `tooling_infrastructure`

- User intent: Build reusable infrastructure for future skills and agents.
- Evidence class: `infrastructure_efficiency_benchmark`
- Why this route: MCP/tool lookup is a broad substrate where TRMs can optimize stable handles, call count, and token load.
- First action: Define first-useful-hit, token-load, and call-count metrics before collecting traces.
- Paper section: Future work or systems appendix.
- Overclaim risk: If the resource surface is tiny, direct scanning is the right baseline and TRM overhead is not justified.

Projects:
- `mcp_lookup_efficiency`: TRM-MCP Lookup Efficiency
- First artifact for `mcp_lookup_efficiency`: A benchmark over filesystem, GitHub, Postgres, and PrimeHub-schema MCP examples with call-count and token-load metrics.
- Success metric for `mcp_lookup_efficiency`: Fewer calls and fewer loaded tokens before first useful answer at equal or better answer correctness.
- Paper claim for `mcp_lookup_efficiency`: TRM rows can compactify tool/resource lookup when the target is stable handles rather than raw memorized answers.
- `real_tool_contract_router`: Real Tool-Contract Router
- First artifact for `real_tool_contract_router`: A 30-60 row real-tool trace suite covering repo search, file lookup, shell-safe commands, calendar-like scheduling, weather-like queries, and JSON argument traps.
- Success metric for `real_tool_contract_router`: At least +0.20 absolute exact tool-call validity over baseline with zero schema-invalid commits on held-out tools.
- Paper claim for `real_tool_contract_router`: MeTTa/TRM improves control-plane tool-use reliability when tool schemas and arguments are verifier-visible.

### `scale_campaign`

- User intent: Prepare for Snacksack or equivalent 9B/27B matched runs.
- Evidence class: `matched_scale_matrix`
- Why this route: The paper becomes stronger when the same row schema is run at 3B, 9B, and 27B with the same validators.
- First action: Freeze row IDs, prompt construction, output schema, and validator code before changing models.
- Paper section: Full experiment campaign.
- Overclaim risk: Changing row selection or validators between scales makes the trend uninterpretable.

Projects:
- `mixed_contract_compactification`: Mixed Contract Compactification Suite
- First artifact for `mixed_contract_compactification`: A 50-row held-out mixed-contract dataset with explicit failure labels, exact validators, and near-miss cases.
- Success metric for `mixed_contract_compactification`: Runtime+repair wins on exact contract validity without reducing semantic correctness on choice or summary rows.
- Paper claim for `mixed_contract_compactification`: Small LLMs can act as proposal engines when explicit symbolic gates own observable output contracts.
- `logic_signature_camp_gate`: Leakage-Safe Logic Signature Gate
- First artifact for `logic_signature_camp_gate`: A tiny Campsite-style micro-suite with puzzle constraints, row/column signatures derivable from the prompt, and proposal-tier labels.
- Success metric for `logic_signature_camp_gate`: Improved cell accuracy and exactness over raw proposals, with an audit column proving no target answer signatures were imported.
- Paper claim for `logic_signature_camp_gate`: Symbolic amplification can help hard logic only after the model emits enough verifier-visible state.
- `math_teacher_candidate_auditor`: Math Teacher-Candidate Auditor
- First artifact for `math_teacher_candidate_auditor`: A teacher-candidate bank with multiple proposed answers per item, numeric error archetypes, boxed-answer validators, and abstain labels.
- Success metric for `math_teacher_candidate_auditor`: Better candidate selection than keyword or always-first baselines while preserving a clear no-small-model-solve claim boundary.
- Paper claim for `math_teacher_candidate_auditor`: For hard math, MeTTa/TRM is useful as an auditor and protocol gate, not as a substitute solver.

## Execution Rules

- Prefer exact validators and frozen rows before model calls.
- Keep local 3B, 9B, and 27B comparisons on the same row IDs and output schema.
- Mark every result with one evidence class: `live_model`, `deterministic_replay`, `post_hoc_projection`, `no_model_verifier_sweep`, or `control_plane_simulation`.
- Do not treat deterministic repair as learned TRM lift unless a trained TRM consumed the same features and improved a held split.
- Do not route hard math as a compactification success; route it as candidate auditing unless the model generated the correct solution candidate.
- For safety-like work, separate route/format correctness from advice quality.
