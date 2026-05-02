# Remote 9B/27B Repair Rudder Benchmark

Date: 2026-05-02

Purpose: fill the Skills paper scale rows for matched 9B and 27B
repair-training rudder benchmarks over the same non-train Pure-TRM split used by
the local 3B run.

## Snacksack Setup

The stock `/home/snacksack/llama-b8645/llama-server` binary is CPU-only. It can
serve Qwen3.5 if launched with `--reasoning off`, but it does not allocate model
weights in VRAM.

For the completed runs, snacksack used the user-local CUDA wheel:

- `llama-cpp-python==0.3.21`
- `nvidia-cuda-runtime-cu12`
- `nvidia-cublas-cu12`

Required environment:

```bash
export PYTHONPATH=/home/snacksack/.local/lib/python3.12/site-packages
export LD_LIBRARY_PATH=/home/snacksack/.local/lib/python3.12/site-packages/nvidia/cublas/lib:/home/snacksack/.local/lib/python3.12/site-packages/nvidia/cuda_runtime/lib:/home/snacksack/.local/lib/python3.12/site-packages/llama_cpp/lib:$LD_LIBRARY_PATH
```

9B CUDA server used for the full run:

```bash
python3 -m llama_cpp.server \
  --model /home/snacksack/Qwopus_v2/models/Qwen_Qwen3.5-9B-Q4_K_M.gguf \
  --model_alias Qwen_Qwen3.5-9B-Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8084 \
  --n_gpu_layers -1 \
  --n_ctx 4096 \
  --n_threads 8 \
  --n_batch 512
```

27B CUDA server used for the full run:

```bash
python3 -m llama_cpp.server \
  --model /home/snacksack/Qwopus_v2/models/Qwen3.5-27B.Q4_K_M.gguf \
  --model_alias Qwen3.5-27B.Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8081 \
  --n_gpu_layers -1 \
  --n_ctx 2048 \
  --n_threads 8 \
  --n_batch 256
```

The Python server's chat endpoint leaves Qwen thinking enabled. The benchmark
therefore used `--api-mode completions --no-think-prefill`, which renders a
manual ChatML prompt ending in an empty `<think></think>` block.

## Completed Runs

9B full run:

```powershell
python research\scripts\run_remote_repair_training_rudder_benchmark.py --model-scale 9b --base-url-9b http://snacksack-ms-7d32.tail3156cd.ts.net:8084/v1 --max-cases 0 --arm raw_3b_rudder --arm repair_training_rudder --arm metta_action_space_rudder --arm metta_static_gate_rudder --request-timeout 180 --max-runtime-minutes 120 --max-tokens 128 --no-think-prefill --api-mode completions --skip-endpoint-check
```

Output:

- `../remote_9b_repair_training_rudder_20260502T203509Z/remote_repair_training_rudder.results.json`
- `../remote_9b_repair_training_rudder_20260502T203509Z/remote_repair_training_rudder.results.md`
- `../remote_9b_repair_training_rudder_20260502T203509Z/remote_repair_training_rudder.rows.jsonl`

27B full run:

```powershell
python research\scripts\run_remote_repair_training_rudder_benchmark.py --model-scale 27b --max-cases 0 --arm raw_3b_rudder --arm repair_training_rudder --arm metta_action_space_rudder --arm metta_static_gate_rudder --request-timeout 180 --max-runtime-minutes 120 --max-tokens 128 --no-think-prefill --api-mode completions --skip-endpoint-check
```

Output:

- `../remote_27b_repair_training_rudder_20260502T204314Z/remote_repair_training_rudder.results.json`
- `../remote_27b_repair_training_rudder_20260502T204314Z/remote_repair_training_rudder.results.md`
- `../remote_27b_repair_training_rudder_20260502T204314Z/remote_repair_training_rudder.rows.jsonl`

## Summary

| model | arm | n | target action | repair action | joint | JSON parse |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 9B | `raw_3b_rudder` | 88 | 0.7273 | 0.4091 | 0.3636 | 1.0000 |
| 9B | `repair_training_rudder` | 88 | 0.9659 | 0.7955 | 0.7955 | 1.0000 |
| 9B | `metta_action_space_rudder` | 88 | 0.7500 | 1.0000 | 0.7500 | 1.0000 |
| 9B | `metta_static_gate_rudder` | 88 | 0.9545 | 1.0000 | 0.9545 | 1.0000 |
| 27B | `raw_3b_rudder` | 88 | 0.7614 | 0.5341 | 0.4886 | 1.0000 |
| 27B | `repair_training_rudder` | 88 | 0.9318 | 0.7955 | 0.7955 | 1.0000 |
| 27B | `metta_action_space_rudder` | 88 | 0.8068 | 1.0000 | 0.8068 | 1.0000 |
| 27B | `metta_static_gate_rudder` | 88 | 0.9432 | 1.0000 | 0.9432 | 1.0000 |

The main signal is that repair-training context materially improves raw
model-rudder joint accuracy, while MeTTa static gating remains the strongest
compact control-plane intervention at both tested scales.
