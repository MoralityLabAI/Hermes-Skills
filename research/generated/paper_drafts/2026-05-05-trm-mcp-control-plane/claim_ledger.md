# Claim Ledger

## Allowed Claims

| Claim | Label | Evidence |
| --- | --- | --- |
| The generic MCP matrix contains `15` traces and `42` TRM rows across filesystem, GitHub, and Postgres surfaces. | `training_corpus_plan` | `data\trm_mcp_example_matrix\merged\trm_mcp_example_matrix.manifest.json` |
| The matrix separates route, retrieve, and verify row families. | schema/design evidence | same manifest |
| The storyworld play-diary MCP run used `15` scenarios, `20` plays, max depth `7`, and branch limit `1024`. | environment study | `C:\projects\metta-storyworld\metta-etc\artifacts\overnight_policy_v2\overnight_summary.json` |
| Diary-aided NAV reached average diary lift `+0.619333`. | environment study | `C:\projects\metta-storyworld\metta-etc\README.md` and `overnight_policy_v2` artifacts |
| Diary memory corrected four negative-NAV cases back to baseline. | environment study | `OVERNIGHT_SUMMARY.md` and `benchmesh\summary.md` |

## Disallowed Claims For Current Evidence

| Claim | Reason |
| --- | --- |
| A trained TRM-MCP neural controller has been validated. | Current generic matrix is a row corpus, not a trained model result. |
| MCP makes context literally free. | MCP still has lookup, retrieval, serialization, and verification costs. |
| Storyworld diary evidence proves generic QA improvement. | It is a repeated-play environment result, not a general QA benchmark. |
| The current run proves raw small LLMs can solve storyworlds through MCP. | The cited run is deterministic/NAV/diary policy evidence unless an LLM-backed receipt is added. |

## Best Short Claim

TRM-MCP reframes context management as a low-bandwidth routing, retrieval, verification, and stop/escalate task over structured memory surfaces, creating a concrete path toward quality-per-token gains.
