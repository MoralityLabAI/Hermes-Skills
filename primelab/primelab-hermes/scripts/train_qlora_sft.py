import argparse
import json
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

try:
    from PIL import Image
    from transformers import image_utils as _transformers_image_utils

    if not hasattr(_transformers_image_utils, "PILImageResampling"):
        _transformers_image_utils.PILImageResampling = getattr(Image, "Resampling", Image)
except Exception:
    pass

from trl import SFTConfig, SFTTrainer

from primelab_hermes.trainer_compat import load_patched_config


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", type=str, required=True, help="HF model id, e.g. Qwen/Qwen3.5-27B")
    p.add_argument("--data", type=str, required=True, help="Path to JSONL with {'messages':[...]} rows")
    p.add_argument("--out", type=str, required=True, help="Output dir for adapter")
    p.add_argument("--max-steps", type=int, default=200)
    p.add_argument("--seq-len", type=int, default=512)
    p.add_argument("--batch-size", type=int, default=1)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--grad-accum", type=int, default=16)
    p.add_argument("--lora-r", type=int, default=16)
    p.add_argument("--lora-alpha", type=int, default=32)
    p.add_argument("--lora-dropout", type=float, default=0.05)
    p.add_argument(
        "--target-modules",
        type=str,
        default="q_proj,k_proj,v_proj,o_proj",
        help="Comma-separated module names for LoRA injection",
    )
    p.add_argument("--streaming", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--seed", type=int, default=1)
    args = p.parse_args()

    data_path = Path(args.data)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    cfg, tok, patch_meta = load_patched_config(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        config=cfg,
        quantization_config=bnb,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

    target_modules = [s.strip() for s in args.target_modules.split(",") if s.strip()]
    lora = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=target_modules,
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    ds = load_dataset("json", data_files=str(data_path), split="train", streaming=bool(args.streaming))

    def formatting_func(example):
        return tok.apply_chat_template(example["messages"], tokenize=False, add_generation_prompt=False)

    sft_config = SFTConfig(
        output_dir=str(out_dir),
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        max_steps=args.max_steps,
        logging_steps=1,
        save_strategy="steps",
        save_steps=max(10, args.max_steps // 5),
        optim="paged_adamw_8bit",
        fp16=False,
        bf16=False,
        report_to="none",
        remove_unused_columns=False,
        seed=args.seed,
        max_length=args.seq_len,
        dataset_text_field="unused",
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=ds,
        formatting_func=formatting_func,
        args=sft_config,
    )
    trainer.train()

    adapter_dir = out_dir / "adapter"
    trainer.model.save_pretrained(str(adapter_dir))
    tok.save_pretrained(str(adapter_dir))

    meta = {
        "model": args.model,
        "data": str(data_path),
        "out": str(adapter_dir),
        "max_steps": args.max_steps,
        "seq_len": args.seq_len,
        "batch_size": args.batch_size,
        "grad_accum": args.grad_accum,
        "lr": args.lr,
        "lora": {
            "r": args.lora_r,
            "alpha": args.lora_alpha,
            "dropout": args.lora_dropout,
            "target_modules": target_modules,
        },
        "patch_meta": patch_meta,
    }
    (adapter_dir / "run_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=True), encoding="utf-8")
    print(f"OK: saved adapter to {adapter_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
