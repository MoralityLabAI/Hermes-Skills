# MeTTa Third-Column Cross-Ref

This joins the local 9B skill benchmark pack against the current MeTTa/TRM evidence.

- Source pack: `C:\projects\Hermes-Skills\Hermes Skills\data\primehub_skill_reasoning_batch_20260416_2100mdt`
- Machine-readable output: [metta_third_column_crossref.json](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_third_column_crossref.json>)
- Structured-map promoted snapshot: [post-fix 3-env findings](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-structured-map-retrieval\artifacts\live_eval_qwen35_9b_post_fix_3env.findings.md>)

## Three-Column View

| Env | 9B without TRM | 9B with TRM best | MeTTa/TRM third column | Evidence type | Read |
| --- | ---: | ---: | ---: | --- | --- |
| `aime2026` | 0.0000 (failure:bridge_failure) | 0.0000 `three-model-basket-v3-reasoning-heavy` (failure:bridge_failure) | 1.0000 `gated_boxed_exact_rate` | local_trm_router_benchmark | MeTTa delta vs its matched control: +1.0000 |
| `allenai_ifeval` | 0.0000 (completed) | 0.0000 `three-model-basket-v3-reasoning-heavy` (completed) | 1.0000 `gated_contract_success_rate` | local_trm_router_benchmark | MeTTa delta vs its matched control: +1.0000 |
| `ascii_tree` | 0.0000 (completed) | 0.0000 `three-model-basket-v3-reasoning-heavy` (completed) | 0.8000 `reward` | live_9b_reward | MeTTa delta vs its matched control: +0.0000 |
| `if_summarize_judge` | - (not_in_pack) | - | 1.0000 `avg_reward` | live_9b_reward | MeTTa delta vs its matched control: +0.6667 |
| `psycho_bench` | 0.0000 (failure:bridge_failure) | 0.0000 `three-model-basket-v3-reasoning-heavy` (failure:bridge_failure) | 3.3483 `reward` | live_9b_reward | MeTTa delta vs its matched control: +0.0200 |
| `pydantic_adherence` | 0.0000 (failure:bridge_failure) | 0.0000 `three-model-basket-v3-reasoning-heavy` (failure:bridge_failure) | 1.0000 `reward` | live_9b_reward | MeTTa delta vs its matched control: +0.0000 |

## Interpretation Boundary

- The `9B without TRM` and `9B with TRM best` columns come from the same local skill benchmark pack and are directly comparable within an environment.
- The MeTTa column is a cross-reference column, not a single pooled metric. `live_9b_reward` rows are closest to direct comparison; `local_trm_router_benchmark` rows are evidence for training/control-plane effectiveness.
- The strongest publishable claim is currently scoped: MeTTa improves structured constraint framing and router-specialized training signals, with the cleanest live reward gains on `psycho_bench` and `if_summarize_judge` and strongest exact-structure evidence on `ascii_tree`/`pydantic_adherence`.

## Local Fallback Run

After Snacksack access was lost, local-only survivability runs were executed for `if_summarize_judge`: [0.8B HF local results](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_eval_qwen35_0p8b_if_summarize_metta\local_if_summarize_metta.results.md>), [3B HF local results](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_eval_smollm3_3b_if_summarize_metta\local_if_summarize_metta.results.md>), [3B Q4 GGUF tok16 results](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_eval_qwen25_3b_q4km_llamacli_probe_ctx2048_tok16\local_if_summarize_metta.results.md>), and [3B Q4 GGUF tok64 v2 results](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\local_eval_qwen25_3b_q4km_llamacli_3seed_tok64_repairfix_v2\local_if_summarize_metta.results.md>).

| Local model | Env | Setting | without_metta | with_metta_runtime | with_metta_runtime_repair | Read |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `qwen35_0p8b_local` | `if_summarize_judge` | HF, 3 seeds | 0.3333 | 0.3333 | 1.0000 | Repair layer reproduces the same constraint-framing pattern locally, but this is not a 9B-equivalent run. |
| `smollm3_3b_local` | `if_summarize_judge` | HF CPU, 3 seeds | 0.0000 | 0.0000 | 1.0000 | Larger local model also fails raw structure but reaches exact compliance through MeTTa-framed repair across the same three seeds. |
| `qwen25_3b_q4km_llamacli` | `if_summarize_judge` | GGUF CUDA, seed 7, max_tokens 16 | 0.0000 | 0.0000 | 1.0000 | VRAM-first GGUF path works operationally; repair succeeds when the candidate is detected as wrong sentence count. |
| `qwen25_3b_q4km_llamacli` | `if_summarize_judge` | GGUF CUDA, 3 seeds, max_tokens 64, post-repair-fix-v2 | 0.0000 | 0.0000 | 1.0000 | VRAM-first local 3B slice: metric-aware MeTTa repair restores exact compliance on all three longer-output cases. |

Resource caveat: the run used the capped launcher configured for `2048 MB RAM`, `50% CPU`, `50 MB/s IO`, but the monitor reported `3114.4375 MB` peak working set. Treat the result as local evidence, not a resource-clean benchmark receipt, until rerun with an approved higher cap or a smaller working backend.
The 3B run required an `8192 MB RAM` cap because the only complete local 3B asset is a CPU-side `bfloat16` HF model; the capped receipt reported `7665.3984 MB` peak working set.
The Qwen2.5-3B Q4_K_M GGUF runs used llama.cpp CUDA full offload. llama.cpp reported about `1834 MiB` model buffer on CUDA and `166-170 MiB` host mapped model memory in single-seed probes; the promoted three-seed tok64 v2 Windows job wrapper reported `2053.1406 MB` peak working set.

## Synthetic Tool Router

A controlled tool-calling surrogate was added for the small-model claim: [synthetic tool-router results](<C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\synthetic_tool_router_qwen25_3b_q4km\synthetic_tool_router.results.md>).

| Local model | Task | without_metta | with_metta_runtime | with_metta_runtime_repair | Read |
| --- | --- | ---: | ---: | ---: | --- |
| `qwen25_3b_q4km_llamacli` | `synthetic_tool_router` | 0.0000 | 1.0000 | 1.0000 | MeTTa contract memory turns wrong raw tool names/slots into exact JSON tool calls; repair is unchanged because runtime already satisfies all three schemas. |

Resource caveat: the outer job receipt records the parent process only for this subprocess-heavy runner, but per-child telemetry captured by the runner shows `2139-2343 MB` peak child RSS and llama.cpp reports about `1834 MiB` CUDA model buffer plus `166-170 MiB` host mapped model memory.

## Full Pack Coverage

| Env | Baseline status | TRM variants seen | MeTTa evidence |
| --- | --- | --- | --- |
| `agency_bench` | completed | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1` | - |
| `aime2024` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-hard-reasoning-v1` | - |
| `aime2025` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-hard-reasoning-v1` | - |
| `aime2026` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-hard-reasoning-v1` | local_trm_router_benchmark |
| `allenai_ifeval` | completed | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1` | local_trm_router_benchmark |
| `antislop` | completed | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-contract-repair-v1` | - |
| `arc` | completed | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1` | - |
| `ascii_tree` | completed | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-contract-repair-v1` | live_9b_reward |
| `bixbench` | completed | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-hard-reasoning-v1` | - |
| `boolq` | completed | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1` | - |
| `gauss` | completed | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-hard-reasoning-v1` | - |
| `hellaswag` | completed | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1` | - |
| `if_summarize_judge` | not_in_pack | - | live_9b_reward |
| `jailbreak_bench` | completed | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1` | - |
| `lisanbench` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-hard-reasoning-v1` | - |
| `logic_env` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-hard-reasoning-v1` | - |
| `math500` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-hard-reasoning-v1` | - |
| `math_env` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-hard-reasoning-v1` | - |
| `medsafetybench` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1` | - |
| `mmlu_pro` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1`, `two-model-hard-reasoning-v1` | - |
| `psycho_bench` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-contract-repair-v1` | live_9b_reward |
| `pydantic_adherence` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-contract-repair-v1` | live_9b_reward |
| `science_env` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-hard-reasoning-v1` | - |
| `simple_bench` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1` | - |
| `simpleqa` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1` | - |
| `simpleqa_verified` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1` | - |
| `simpleqa_verified_2` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1` | - |
| `truthfulqa` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1` | - |
| `winogrande` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1`, `two-model-contract-repair-v1` | - |
| `wmdp` | failure:bridge_failure | `single-model-baseline`, `three-model-basket-v3-reasoning-heavy`, `two-model-abstain-guard-v1` | - |
