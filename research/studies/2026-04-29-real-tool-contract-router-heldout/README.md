# Real Tool-Contract Router Heldout

Generated: `2026-04-29T13:29:18.090439+00:00`

## Purpose

This suite tests whether Alias V3 compact retrieval generalizes beyond the 36-row seed benchmark. It adds unseen paraphrases, new aliases, and new planned-tool schemas while keeping the same JSON contract and validator family.

## Family Counts

| Family | Rows |
| --- | ---: |
| `file_lookup` | 4 |
| `json_argument_trap` | 4 |
| `repo_search` | 4 |
| `scheduling_query` | 4 |
| `shell_safe_command` | 4 |
| `task_note_browser` | 8 |
| `weather_query` | 4 |

## Artifacts

- Rows: `rows/real_tool_contract_router_heldout_rows.jsonl`
- Validator: `validators/validate_tool_contracts.py`
- Suite config: `configs/real_tool_contract_router_heldout.json`
- Canonical smoke: `results/canonical_validator_smoke/canonical_validator_smoke.results.md`
- Heldout findings: `heldout_findings.md`
- Alias V3 live run: `results/local_qwen25_3b_tool_router_alias_v3/local_qwen25_3b_tool_router.results.md`
- Job-cap receipt: `results/local_qwen25_3b_tool_router_alias_v3/jobcap.summary.json`
- Alias V3 arg-canonicalizer: `results/local_qwen25_3b_tool_router_alias_v3_argcanon/tool_router_v3_argcanon.results.md`

## Alias V3 Held-Out Live Result

The compact-retrieval V3 run completed under a 3,000 MB RAM cap with runner child RSS peak `2374.93 MB`; job-cap status was `success`.

| Arm | Exact | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits | Exact Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0/32 | 0 | 21 | 0 | 25 | 2 | 0.0000 |
| `pure_trm` | 30/32 | 31 | 31 | 30 | 31 | 0 | 0.9375 |
| `metta_runtime` | 31/32 | 32 | 32 | 31 | 32 | 0 | 0.9688 |
| `metta_runtime_repair` | 31/32 | 32 | 32 | 31 | 32 | 0 | 0.9688 |


## Alias V3 Held-Out Argcanon Result

The same generic V3 compiler was applied to held-out live outputs.

| Arm | Exact | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits | Exact Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `pure_trm_v3_argcanon` | 32/32 | 32 | 32 | 32 | 32 | 0 | 1.0000 |
| `metta_runtime_repair_v3_argcanon` | 32/32 | 32 | 32 | 32 | 32 | 0 | 1.0000 |
