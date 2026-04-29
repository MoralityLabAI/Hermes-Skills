# Logic Signature Camp-Gate Leakage-Safe Micro-Suite

Generated: `2026-04-29T13:58:48.413187+00:00`

- Route: `hard_env_boundary`
- Project: `logic_signature_camp_gate`
- Evidence classes: `no_model_proposal_tier_smoke`, `live_model_local_3b`
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

## Local 3B Result

The local Qwen2.5-3B Q4 run completed under the Windows job-cap wrapper with a 3,000 MB RAM cap, 50% CPU cap, 50 MB/s IO cap, and 7,200 second timeout. Runner-level child RSS peaked at `2373.23 MB`; the wrapper reported `success`.

| Arm | Exact | Exact Rate | Contract Valid | Avg Cell Acc | Tier Counts |
| --- | ---: | ---: | ---: | ---: | --- |
| `baseline` | 0/12 | 0.0000 | 0/12 | 0.0781 | none:10, weak_surface:2 |
| `pure_trm` | 0/12 | 0.0000 | 0/12 | 0.1562 | none:7, weak_surface:5 |
| `metta_runtime` | 0/12 | 0.0000 | 0/12 | 0.2792 | none:3, weak_surface:9 |
| `metta_signature_projection` | 9/12 | 0.7500 | 9/12 | 0.7500 | full_candidate:9, none:3 |

Interpretation: the projection column is the key hard-env measurement. It tests whether local 3B emits enough verifier-visible grid state for prompt-derived signature projection to close the solution. It is not a trained TRM lift claim.
