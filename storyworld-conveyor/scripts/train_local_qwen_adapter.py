from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def import_or_die() -> Dict[str, Any]:
    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, get_peft_model
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            DataCollatorForLanguageModeling,
            Trainer,
            TrainingArguments,
        )
    except Exception as exc:  # pragma: no cover - preflight
        raise SystemExit(
            "Missing or incompatible local training dependencies. "
            "Create a fresh venv and install requirements from "
            "hermes-skills/storyworld-conveyor/requirements-local-qwen-adapter.txt. "
            f"Original error: {type(exc).__name__}: {exc}"
        )
    return {
        "torch": torch,
        "load_dataset": load_dataset,
        "LoraConfig": LoraConfig,
        "get_peft_model": get_peft_model,
        "AutoModelForCausalLM": AutoModelForCausalLM,
        "AutoTokenizer": AutoTokenizer,
        "DataCollatorForLanguageModeling": DataCollatorForLanguageModeling,
        "Trainer": Trainer,
        "TrainingArguments": TrainingArguments,
    }


def flatten_messages(messages: List[Dict[str, str]], tokenizer: Any) -> str:
    if hasattr(tokenizer, "apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
        except Exception:
            pass
    parts: List[str] = []
    for msg in messages:
        role = str(msg.get("role", "user")).upper()
        content = str(msg.get("content", ""))
        parts.append(f"{role}: {content}")
    return "\n\n".join(parts)


def load_records(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def infer_dtype(torch: Any) -> Any:
    if torch.cuda.is_available():
        return torch.float16
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.float16
    return torch.float32


def main() -> int:
    libs = import_or_die()
    torch = libs["torch"]
    load_dataset = libs["load_dataset"]
    LoraConfig = libs["LoraConfig"]
    get_peft_model = libs["get_peft_model"]
    AutoModelForCausalLM = libs["AutoModelForCausalLM"]
    AutoTokenizer = libs["AutoTokenizer"]
    DataCollatorForLanguageModeling = libs["DataCollatorForLanguageModeling"]
    Trainer = libs["Trainer"]
    TrainingArguments = libs["TrainingArguments"]

    parser = argparse.ArgumentParser(description="Train a local LoRA adapter on storyworld QLoRA message examples.")
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--train-jsonl", required=True)
    parser.add_argument("--val-jsonl", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--train-batch-size", type=int, default=1)
    parser.add_argument("--eval-batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--save-steps", type=int, default=50)
    parser.add_argument("--logging-steps", type=int, default=5)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    args = parser.parse_args()

    train_path = Path(args.train_jsonl).resolve()
    val_path = Path(args.val_jsonl).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    train_records = load_records(train_path)
    val_records = load_records(val_path)

    flat_train = [{"text": flatten_messages(row["messages"], tokenizer)} for row in train_records]
    flat_val = [{"text": flatten_messages(row["messages"], tokenizer)} for row in val_records]

    tmp_train = output_dir / "train_flat.jsonl"
    tmp_val = output_dir / "val_flat.jsonl"
    tmp_train.write_text("\n".join(json.dumps(row, ensure_ascii=True) for row in flat_train) + "\n", encoding="utf-8")
    tmp_val.write_text("\n".join(json.dumps(row, ensure_ascii=True) for row in flat_val) + "\n", encoding="utf-8")

    dataset = load_dataset("json", data_files={"train": str(tmp_train), "validation": str(tmp_val)})

    def tokenize(batch: Dict[str, List[str]]) -> Dict[str, Any]:
        encoded = tokenizer(
            batch["text"],
            truncation=True,
            max_length=args.max_length,
            padding=False,
        )
        encoded["labels"] = [ids[:] for ids in encoded["input_ids"]]
        return encoded

    tokenized = dataset.map(tokenize, batched=True, remove_columns=["text"])

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        trust_remote_code=True,
        torch_dtype=infer_dtype(torch),
    )
    model.config.use_cache = False

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules="all-linear",
    )
    model = get_peft_model(model, lora_config)

    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"
    elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        device = "mps"
    model.to(device)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        overwrite_output_dir=True,
        num_train_epochs=args.epochs,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.train_batch_size,
        per_device_eval_batch_size=args.eval_batch_size,
        gradient_accumulation_steps=args.grad_accum,
        save_steps=args.save_steps,
        logging_steps=args.logging_steps,
        evaluation_strategy="steps",
        eval_steps=args.save_steps,
        save_strategy="steps",
        report_to=[],
        fp16=(device == "cuda"),
        bf16=False,
        gradient_checkpointing=True,
        remove_unused_columns=False,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    )
    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    summary = {
        "model_name": args.model_name,
        "train_jsonl": str(train_path),
        "val_jsonl": str(val_path),
        "output_dir": str(output_dir),
        "train_rows": len(train_records),
        "val_rows": len(val_records),
        "device": device,
        "max_length": args.max_length,
        "epochs": args.epochs,
    }
    (output_dir / "adapter_train_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(str(output_dir))
    print(str(output_dir / "adapter_train_summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
