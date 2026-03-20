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

- `default_hosted_eval.toml`
- `default_qlora_spec.json`
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

```bash
python scripts/build_qlora_dataset.py --spec-json bench/oss_skill_bench/default_qlora_spec.json --out-root data/qlora_conveyor/bench-default
python scripts/train_qlora_sft.py --model Qwen/Qwen3-4B-Instruct-2507 --data data/qlora_conveyor/bench-default/gsm8k_main_sample/train.jsonl --out runs/qlora_conveyor/bench-default --max-steps 40 --seq-len 384 --batch-size 1 --grad-accum 8 --lora-r 16 --lora-alpha 32 --target-modules q_proj,k_proj,v_proj,o_proj > runs/qlora_conveyor/bench-default/train.log 2>&1
python bench/oss_skill_bench/summarize_bench.py --run-dir runs/qlora_conveyor/bench-default --log runs/qlora_conveyor/bench-default/train.log
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
