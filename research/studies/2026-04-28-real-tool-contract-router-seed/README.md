# Real Tool-Contract Router Seed

Generated: `2026-04-29T00:38:20.734462+00:00`

- Route: `new_metta_project`
- Project: `real_tool_contract_router`
- Evidence class: `no_model_validator_smoke`, `live_model_local_3b`
- Source menu: `research/generated/metta_project_menu.md`

## Purpose

This starts the next MeTTa project after mixed-contract compactification. The suite moves from synthetic output contracts to Hermes-style tool calls where MeTTa can own schema memory, argument validation, safety routing, and commit gating.

## Family Counts

| Family | Rows |
| --- | ---: |
| `file_lookup` | 6 |
| `json_argument_trap` | 6 |
| `repo_search` | 6 |
| `scheduling_query` | 6 |
| `shell_safe_command` | 6 |
| `weather_query` | 6 |

## Artifacts

- Rows: `rows/real_tool_contract_router_seed_rows.jsonl`
- Validator: `validators/validate_tool_contracts.py`
- Suite config: `configs/real_tool_contract_router_seed.json`
- Canonical smoke: `results/canonical_validator_smoke/canonical_validator_smoke.results.md`
- Local 3B run: `results/local_qwen25_3b_tool_router_seed/local_qwen25_3b_tool_router.results.md`
- Job-cap receipt: `results/local_qwen25_3b_tool_router_seed/jobcap.summary.json`

## Local 3B Result

The full 36-row run completed under the Windows job-cap wrapper with a 3,000 MB RAM cap, 50% CPU cap, 50 MB/s IO cap, and 7,200 second timeout. Runner-level child RSS peaked at `2373.54 MB`; the job-cap wrapper reported `success`.

| Arm | Exact | JSON Obj | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits | Exact Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0/36 | 34 | 0 | 22 | 0 | 25 | 2 | 0.0000 |
| `pure_trm` | 3/36 | 36 | 25 | 30 | 3 | 34 | 2 | 0.0833 |
| `metta_runtime` | 4/36 | 35 | 29 | 29 | 4 | 30 | 2 | 0.1111 |
| `metta_runtime_repair` | 4/36 | 36 | 29 | 29 | 4 | 32 | 1 | 0.1111 |

This is a diagnostic seed result. MeTTa/TRM prompting improves schema and tool-route reliability, but exact argument recovery remains the bottleneck. The next iteration should add explicit alias memory and argument-normalization gates before claiming tool-use compactification.
