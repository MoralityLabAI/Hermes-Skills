# Logic Signature Camp-Gate Leakage-Safe Micro-Suite

Generated: `2026-04-29T19:06:54.015562+00:00`

- Route: `hard_env_boundary`
- Project: `logic_signature_camp_gate`
- Evidence classes: `no_model_proposal_tier_smoke`, `live_model_local_3b`, `live_model_local_3b_constraint_extract`, `no_model_prompt_constraint_graph_router`
- Source menu: `research/generated/metta_project_menu.md`
- Circuit: `intellect3_logic_signature_circuit`

## Purpose

This study turns the prior Intellect-3 camp-gate replay into a leakage-safe micro-suite. The old replay projected against answer-derived signatures from existing receipts; this suite exposes only prompt-derived constraints and audits solver uniqueness before any score table.

## Public Constraint Surface

- Fixed `T` cells are listed in each prompt.
- Row and column `C` counts are listed in each prompt.
- Local adjacency rules define valid campsite grids.
- Target grids are absent from prompts and marked by SHA-256 for audit only.

## Shape Counts

| Grid Shape | Rows |
| --- | ---: |
| `4x4` | 4 |
| `4x5` | 2 |
| `5x4` | 4 |
| `5x5` | 2 |

## Artifacts

- Rows: `rows/logic_signature_camp_gate_rows.jsonl`
- Validator: `validators/validate_logic_signature_camp_gate.py`
- Suite config: `configs/logic_signature_camp_gate_suite.json`
- Proposal-tier smoke: `results/proposal_tier_smoke/proposal_tier_smoke.results.md`
- Local 3B run: `results/local_qwen25_3b_logic_signature_camp_gate/local_qwen25_3b_logic_signature_camp_gate.results.md`
- Job-cap receipt: `results/local_qwen25_3b_logic_signature_camp_gate/jobcap.summary.json`
- Projection ablation: `results/projection_ablation/projection_ablation.results.md`
- Constraint extraction: `results/local_qwen25_3b_constraint_extract/local_qwen25_3b_constraint_extract.results.md`
- Constraint extraction repair: `results/constraint_extract_schema_repair/constraint_extract_schema_repair.results.md`
- Noisy extraction rows: `rows/logic_signature_camp_gate_noisy_extract_rows.jsonl`
- Noisy extraction config: `configs/logic_signature_noisy_extract_suite.json`
- Noisy local 3B graph extraction: `results/local_qwen25_3b_noisy_graph_constraint_extract/local_qwen25_3b_constraint_extract.results.md`
- Noisy graph router control: `results/noisy_graph_router_script/noisy_graph_router.results.md`
- Graph router MeTTa contract: `results/noisy_graph_router_script/camp_gate_graph_router_contract.metta`

## Local 3B Result

The local Qwen2.5-3B Q4 run completed under the Windows job-cap wrapper with a 3,000 MB RAM cap, 50% CPU cap, 50 MB/s IO cap, and 7,200 second timeout. Runner-level child RSS peaked at `2373.23 MB`; the wrapper reported `success`.

| Arm | Exact | Exact Rate | Contract Valid | Avg Cell Acc | Tier Counts |
| --- | ---: | ---: | ---: | ---: | --- |
| `baseline` | 0/12 | 0.0000 | 0/12 | 0.0781 | none:10, weak_surface:2 |
| `pure_trm` | 0/12 | 0.0000 | 0/12 | 0.1562 | none:7, weak_surface:5 |
| `metta_runtime` | 0/12 | 0.0000 | 0/12 | 0.2792 | none:3, weak_surface:9 |
| `metta_signature_projection` | 9/12 | 0.7500 | 9/12 | 0.7500 | full_candidate:9, none:3 |

Interpretation: the projection column is the key hard-env measurement. It tests whether local 3B emits enough verifier-visible grid state for prompt-derived signature projection to close the solution. It is not a trained TRM lift claim.


## Projection Ablation

The projection replay separates candidate-conditioned closure from pure public-constraint solving.

| Arm | Exact | Exact Rate | Contract Valid | Avg Cell Acc | Tier Counts |
| --- | ---: | ---: | ---: | ---: | --- |
| `metta_runtime` | 0/12 | 0.0000 | 0/12 | 0.2792 | none:3, weak_surface:9 |
| `candidate_conditioned_projection` | 9/12 | 0.7500 | 9/12 | 0.7500 | full_candidate:9, none:3 |
| `public_constraint_solver` | 12/12 | 1.0000 | 12/12 | 1.0000 | full_candidate:12 |

The `candidate_conditioned_projection` arm preserves the earlier 9/12 result. The `public_constraint_solver` arm reaches 12/12 because every frozen row has a unique solution from prompt-visible constraints. This is a stronger but narrower claim: once constraints are machine-visible, the LLM is not needed for grid execution.


## Constraint Extraction Follow-Up

The extraction run completed under the Windows job-cap wrapper with a 3,000 MB RAM cap, 50% CPU cap, 50 MB/s IO cap, and 7,200 second timeout. Runner-level child RSS peaked at `2356.16 MB`; the wrapper reported `success`.

| Arm | JSON Parse | Strict Packet Exact | Strict Solve Exact | Repair Packet Exact | Repair Solve Exact |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline_extract` | 0/12 | 0/12 | 0/12 | 0/12 | 0/12 |
| `metta_schema_extract` | 12/12 | 0/12 | 0/12 | 12/12 | 12/12 |

The strict `metta_schema_extract` packets failed because the model omitted `width` in all rows and had one row-count mass-balance error. Deterministic MeTTa-style schema repair inferred missing dimensions from count-vector lengths and accepted the unique row/column-balanced packet only when the public solver closed. This produced 12/12 repaired solve exact.


## Noisy Constraint Extraction

The noisy/paraphrased extraction run completed under the Windows job-cap wrapper with a 3,000 MB RAM cap, 50% CPU cap, 50 MB/s IO cap, and 7,200 second timeout. Runner-level child RSS peaked at `2356.22 MB`; the wrapper reported `success`.

| Arm | JSON Parse | Strict Packet Exact | Strict Solve Exact | Repair Solve Exact | Repair Solve Rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline_extract` | 12/12 | 0/12 | 0/12 | 0/12 | 0.0000 |
| `metta_schema_extract` | 12/12 | 5/12 | 5/12 | 6/12 | 0.5000 |
| `metta_graph_extract` | 12/12 | 7/12 | 7/12 | 9/12 | 0.7500 |
| `canonical_packet_solver` | 12/12 | 12/12 | 12/12 | 12/12 | 1.0000 |

The graph-gated prompt improves the noisy repaired solve score from `metta_schema_extract` 6/12 to `metta_graph_extract` 9/12. The remaining failures are field-transcription mistakes, not grid-execution failures.


## Graph Router Control

The script-owned graph router parses only prompt-visible dimensions, anchor coordinates, row quotas, and column quotas before handing the packet to the public solver. It is the cleanest expression of the current methodology: scripts own stable extraction gates, TRM candidates should target uncertain gates, and the LLM should remain a proposal source rather than the executor.

| Arm | Packet Valid | Packet Exact | Solve Exact | Solve Rate |
| --- | ---: | ---: | ---: | ---: |
| `metta_graph_router_script` | 12/12 | 12/12 | 12/12 | 1.0000 |
| `canonical_packet_solver` | 12/12 | 12/12 | 12/12 | 1.0000 |

This control reaches closure because the noisy prompts are still structured enough for typed script gates. It should be reported as a control-plane threshold, not as language understanding or trained TRM lift.
