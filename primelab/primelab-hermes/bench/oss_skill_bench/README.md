# OSS Skill Bench

This subfolder is for testing whether a local model or an API-routed OSS model can handle the default PrimeLab workflow well enough to be useful.

The benchmark has two parts:

1. A real environment baseline on a hub environment such as `primeintellect/wiki-search`
2. A small QLoRA training run on an exported slice such as `gsm8k`

The point is not just "did the model answer a few eval items." The point is whether the model can support the full skill loop:

- baseline eval
- dataset shaping
- QLoRA launch
- stable training
- readable receipts

## Files

- `bootstrap_local_gpu_bench.ps1`
- `default_hosted_eval.toml`
- `default_qlora_spec.json`
- `run_local_model_bench.ps1`
- `summarize_bench.py`

## Suggested loop

### 1) Run a baseline environment check

```bash
prime eval run primeintellect/wiki-search -m Qwen/Qwen3-30B-A3B-Instruct-2507 -n 16 -r 1
```

If you are using a different eval-capable model, keep the environment and sample count fixed.

### 2) Export or place a small training slice

The default spec is already pointed at the local exported `gsm8k` parquet tree at `D:/Research_Engine/prime_envs/gsm8k`. Keep it small so you can compare multiple models cheaply.

### 3) Run the local QLoRA bench

```powershell
powershell -ExecutionPolicy Bypass -File bench\oss_skill_bench\bootstrap_local_gpu_bench.ps1
powershell -ExecutionPolicy Bypass -File bench\oss_skill_bench\run_local_model_bench.ps1 -Model Qwen/Qwen2.5-0.5B-Instruct -RunId bench-qwen25-05b
```

## How to read the result

Useful capability signals:

- the run reaches real optimizer steps
- final loss is finite and not obviously divergent
- an adapter is produced under `adapter/`
- the model does not collapse into format boilerplate

Do not overread a single loss number. Use this bench to compare models on the same small task and ask:

- which models can actually run the workflow
- which models produce cleaner training signal
- which models are cheap enough to use as skill operators
