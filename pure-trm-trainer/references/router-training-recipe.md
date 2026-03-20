# Router QLoRA Recipe

Use this recipe when the goal is to train a router/TRM adapter with the same low-VRAM QLoRA shape used in `tesseract_persistent`.

## Source corpus

- Primary source: `D:/Research_Engine/tesseract_persistent/data/router/tesseract-router-dataset-v1.jsonl`
- Optional filter spec: a JSON config that points at a source JSONL and an output JSONL.
- Corpus shape: `messages`-format JSONL for `train_qlora_sft.py`.

## Conversion rule

Convert each router row into a compact chat sample:

- `system`: emit compact JSON only; no prose and no hidden reasoning dump.
- `user`: the router prompt text.
- `assistant`: the route decision plus short visible rationale summary and route metadata.

Keep the target small and inspectable. Do not train on long chain-of-thought text.

## Training recipe

Use the same persistent-tesseract QLoRA scaffold:

- 4-bit NF4 loading
- `q_proj,k_proj,v_proj,o_proj`
- LoRA `r=16`
- LoRA `alpha=32`
- LoRA `dropout=0.05`
- `seq_len=512`
- `batch_size=1`
- `grad_accum=16`
- `lr=2e-4`
- streaming JSONL dataset input

Canonical trainer:

```powershell
python D:\Research_Engine\prime_lab\storyworld_sft\train_qlora_sft.py `
  --model %TRM_ROUTER_BASE_MODEL% `
  --data <messages-jsonl> `
  --out <run-dir> `
  --max-steps 200 `
  --seq-len 512 `
  --batch-size 1 `
  --lr 2e-4 `
  --grad-accum 16 `
  --lora-r 16 `
  --lora-alpha 32 `
  --lora-dropout 0.05 `
  --target-modules q_proj,k_proj,v_proj,o_proj
```

## Baseline comparison

- Keep the baseline model fixed while mutating router candidates.
- Record `baseline_model` and `router_model` in the resolved bench spec.
- Reuse the PrimeHub env slice as the anchor set for the comparison pass.

## Expected outputs

- `router_messages.jsonl`
- `train_launch_manifest.json`
- `adapter/`
- `summary.json`
- `scorecard.json`

