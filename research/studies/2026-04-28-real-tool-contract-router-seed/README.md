# Real Tool-Contract Router Seed

Generated: `2026-04-29T13:28:25.533271+00:00`

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
- Alias V2 run: `results/local_qwen25_3b_tool_router_alias_v2/local_qwen25_3b_tool_router.results.md`
- Static safety overlay: `results/local_qwen25_3b_tool_router_alias_v2_static_safety/tool_router_static_safety.results.md`
- V2 findings: `v2_findings.md`
- Alias V3 live run: `results/local_qwen25_3b_tool_router_alias_v3/local_qwen25_3b_tool_router.results.md`
- Alias V3 arg-canonicalizer: `results/local_qwen25_3b_tool_router_alias_v3_argcanon/tool_router_v3_argcanon.results.md`
- V3 findings: `v3_findings.md`

## Local 3B Result

The full 36-row run completed under the Windows job-cap wrapper with a 3,000 MB RAM cap, 50% CPU cap, 50 MB/s IO cap, and 7,200 second timeout. Runner-level child RSS peaked at `2373.54 MB`; the job-cap wrapper reported `success`.

| Arm | Exact | JSON Obj | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits | Exact Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0/36 | 34 | 0 | 22 | 0 | 25 | 2 | 0.0000 |
| `pure_trm` | 3/36 | 36 | 25 | 30 | 3 | 34 | 2 | 0.0833 |
| `metta_runtime` | 4/36 | 35 | 29 | 29 | 4 | 30 | 2 | 0.1111 |
| `metta_runtime_repair` | 4/36 | 36 | 29 | 29 | 4 | 32 | 1 | 0.1111 |

This is a diagnostic seed result. MeTTa/TRM prompting improves schema and tool-route reliability, but exact argument recovery remains the bottleneck. The next iteration should add explicit alias memory and argument-normalization gates before claiming tool-use compactification.

## Alias V2 Result

Alias V2 exposes `alias_memory`, `command_templates`, and `argument_normalization_rules` to non-baseline arms. The full run completed under a 3,000 MB RAM cap with runner child RSS peak `2372.63 MB`; the job-cap wrapper reported `success`.

| Arm | Exact | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits | Exact Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0/36 | 0 | 22 | 0 | 25 | 2 | 0.0000 |
| `pure_trm` | 14/36 | 26 | 30 | 14 | 33 | 2 | 0.3889 |
| `metta_runtime` | 3/36 | 13 | 15 | 3 | 17 | 2 | 0.0833 |
| `metta_runtime_repair` | 11/36 | 25 | 28 | 11 | 30 | 1 | 0.3056 |

## Static Safety Overlay

The deterministic static safety gate flips obvious ambiguous/missing/destructive requests to `safe_to_execute=false` without calling the model again.

| Arm | Exact | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits | Exact Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `pure_trm_static_safety` | 14/36 | 26 | 30 | 14 | 35 | 0 | 0.3889 |
| `metta_runtime_repair_static_safety` | 11/36 | 25 | 28 | 11 | 31 | 0 | 0.3056 |

Alias V2 plus static safety meets the initial promotion rule on the `pure_trm_static_safety` arm: `14/36` exact, `30/36` tool-route exact, and `0` unsafe commits. This is a bounded tool-router compactification lane, not solved tool use.

## Alias V3 Live Result

Alias V3 uses compact retrieval: one prompt-relevant argument template is retrieved before the 3B call instead of dumping the full template memory into context. The full run completed under a 3,000 MB RAM cap with runner child RSS peak `2374.68 MB`; the job-cap wrapper reported `success`.

| Arm | Exact | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits | Exact Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0/36 | 0 | 22 | 0 | 25 | 2 | 0.0000 |
| `pure_trm` | 33/36 | 36 | 36 | 33 | 36 | 0 | 0.9167 |
| `metta_runtime` | 35/36 | 36 | 36 | 35 | 36 | 0 | 0.9722 |
| `metta_runtime_repair` | 35/36 | 36 | 36 | 35 | 36 | 0 | 0.9722 |

## Alias V3 Argument Canonicalizer

The V3 arg-canonicalizer is a deterministic post-parse compiler over live model outputs. It uses prompt-visible intent templates, alias memory, shell templates, weather location suffixes, title normalization, and safety overrides.

| Arm | Exact | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits | Templates Applied | Exact Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `metta_runtime_repair_v3_argcanon` | 36/36 | 36 | 36 | 36 | 36 | 0 | 36 | 1.0000 |
| `pure_trm_v3_argcanon` | 36/36 | 36 | 36 | 36 | 36 | 0 | 36 | 1.0000 |
