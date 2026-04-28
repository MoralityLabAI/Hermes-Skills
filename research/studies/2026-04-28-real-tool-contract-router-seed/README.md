# Real Tool-Contract Router Seed

Generated: `2026-04-28T21:02:09.755980+00:00`

- Route: `new_metta_project`
- Project: `real_tool_contract_router`
- Evidence class: `no_model_validator_smoke`
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

## Next Step

Run a local small-model benchmark with arms matching the mixed-contract runner: `baseline`, `pure_trm`, `metta_runtime`, and `metta_runtime_repair`. Score JSON validity, tool route exactness, argument exactness, and unsafe commit rate separately.
