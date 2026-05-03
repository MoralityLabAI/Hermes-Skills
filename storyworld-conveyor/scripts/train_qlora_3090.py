import argparse
import json
import torch
from pathlib import Path
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

def main():
    parser = argparse.ArgumentParser(description="Train a Qwen model with QLoRA on 3090 (24GB VRAM) for 16k context.")
    parser.add_argument("--model-name", required=True, help="Base model name (e.g., Qwen/Qwen2.5-1.5B-Instruct)")
    parser.add_argument("--data-path", required=True, help="Path to training jsonl")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--max-length", type=int, default=16384, help="Target context length")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    args = parser.parse_args()

    # Model Loading with QLoRA
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        # attn_implementation="flash_attention_2"  # Requires flash-attn
    )

    # Gradient Checkpointing is crucial for 16k
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

    # LoRA Config
    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules="all-linear",
    )
    model = get_peft_model(model, lora_config)

    # Dataset Preparation
    def tokenize(sample):
        # Flatten messages to text if they are list of dicts
        if isinstance(sample["messages"], list):
            text = tokenizer.apply_chat_template(sample["messages"], tokenize=False, add_generation_prompt=False)
        else:
            text = sample["messages"]
            
        return tokenizer(
            text,
            truncation=True,
            max_length=args.max_length,
            padding=False,
        )

    dataset = load_dataset("json", data_files=args.data_path, split="train")
    tokenized_dataset = dataset.map(tokenize, remove_columns=dataset.column_names)

    # Training Args optimized for 3090
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.learning_rate,
        bf16=True,  # 3090 supports bf16
        logging_steps=1,
        save_strategy="epoch",
        evaluation_strategy="no",
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        # Optimized for memory
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

if __name__ == "__main__":
    main()
