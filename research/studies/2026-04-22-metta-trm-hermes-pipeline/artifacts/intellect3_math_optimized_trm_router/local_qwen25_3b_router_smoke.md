# Local Qwen2.5-3B Math Router Smoke

Date: 2026-04-25

Model: `Qwen2.5-3B-Instruct-Q4_K_M.gguf` via local `llama-server.exe`.

Server profile:

- Endpoint: `http://127.0.0.1:8089`
- Context: `2048`
- GPU layers: `all`
- KV cache: `q8_0`
- llama.cpp reported CUDA model buffer: `1834.83 MiB`
- llama.cpp reported CPU-mapped model buffer: `166.92 MiB`

## Results

| Config | Rows | Vanilla Exact | math_skill_trm Exact | Route Policy | Route Sources | Read |
| --- | ---: | ---: | ---: | --- | --- | --- |
| `local_qwen25_3b_intellect3_math_optimized_trm_router_smoke` | 5 | `0.4000` | `0.2000` | `always_trm` | `math_skill_trm:5` | Local 3B does not reproduce the 27B offline replay lift on this tiny first-5-row smoke. |
| `local_qwen25_3b_intellect3_math_generic_guard_router_smoke` | 5 | `0.4000` | `0.2000` | `generic_retrieval_guard` | `math_skill_trm:5` | Guard made no route difference on these five rows. |

## Artifacts

- Always-TRM summary: `C:\projects\trm_observability_harness\data\local_qwen25_3b_intellect3_math_optimized_trm_router_smoke\summary.json`
- Always-TRM predictions: `C:\projects\trm_observability_harness\data\local_qwen25_3b_intellect3_math_optimized_trm_router_smoke\predictions.jsonl`
- Generic-guard summary: `C:\projects\trm_observability_harness\data\local_qwen25_3b_intellect3_math_generic_guard_router_smoke\summary.json`
- Generic-guard predictions: `C:\projects\trm_observability_harness\data\local_qwen25_3b_intellect3_math_generic_guard_router_smoke\predictions.jsonl`
- Server logs: `C:\projects\trm_observability_harness\data\local_qwen25_3b_server_logs`

## Interpretation

This smoke validates that the patched harness and local llama.cpp server path work. It is not evidence that the optimized router improves local 3B math. On this small slice, vanilla is stronger than both TRM-router policies. The 27B offline replay claim remains separate: it says the existing 27B `math_skill_trm` receipt should have committed the hidden TRM-conditioned candidate more often.
