from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_TRAINER = Path(r"D:\Research_Engine\storyworld_mcp_stack\scripts\train_qlora_local_micro.py")
DEFAULT_PYTHON = Path(r"D:\Research_Engine\.venv-train\Scripts\python.exe")
DEFAULT_MODEL = Path(r"D:\Research_Engine\models\Qwen3.5\Qwen3.5-2B-HF")
DEFAULT_QWEN_ROOT = Path(r"D:\Research_Engine\storyworld_qlora")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a D:\\Research_Engine storyworld_qlora run from a conveyor factory run.")
    parser.add_argument("--factory-run-root", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--qwen-model-path", default=str(DEFAULT_MODEL))
    parser.add_argument("--python-exe", default=str(DEFAULT_PYTHON))
    parser.add_argument("--trainer-script", default=str(DEFAULT_TRAINER))
    parser.add_argument("--qlora-root", default=str(DEFAULT_QWEN_ROOT))
    parser.add_argument("--dataset-subdir", default="qlora/overnight_examples")
    parser.add_argument("--max-steps", type=int, default=80)
    parser.add_argument("--seq-len", type=int, default=160)
    parser.add_argument("--grad-accum", type=int, default=10)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--lora-rank", type=int, default=8)
    parser.add_argument("--lora-alpha", type=int, default=16)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--target-modules", default="q_proj,v_proj")
    parser.add_argument("--lora-num-layers", type=int, default=4)
    parser.add_argument("--launch", action="store_true")
    args = parser.parse_args()

    factory_run_root = Path(args.factory_run_root).resolve()
    dataset_dir = (factory_run_root / args.dataset_subdir).resolve()
    train_messages = dataset_dir / "train_messages.jsonl"
    if not train_messages.exists():
        alt = dataset_dir / "train.jsonl"
        if alt.exists():
            train_messages = alt
        else:
            raise SystemExit(f"Missing train_messages dataset under {dataset_dir}")

    qlora_root = Path(args.qlora_root).resolve()
    run_root = qlora_root / "runs" / args.run_id
    train_root = run_root / "train"
    adapter_root = qlora_root / "adapters" / args.run_id
    run_root.mkdir(parents=True, exist_ok=True)
    train_root.mkdir(parents=True, exist_ok=True)
    adapter_root.parent.mkdir(parents=True, exist_ok=True)

    event_jsonl = train_root / "events.jsonl"
    state_json = train_root / "state.json"
    run_manifest = {
        "run_id": args.run_id,
        "run_root": str(run_root),
        "model_path": str(Path(args.qwen_model_path)),
        "dataset_path": str(train_messages),
        "train_output": str(train_root),
        "adapter_path": str(adapter_root),
        "event_jsonl": str(event_jsonl),
        "state_json": str(state_json),
        "lora_num_layers": args.lora_num_layers,
        "target_modules": args.target_modules,
        "use_caps": True,
        "caps": {
            "ram_mb": 1792,
            "cpu_pct": 30,
            "io_mb_s": 20,
            "timeout_sec": 21600,
            "checkpoint_interval_sec": 60,
            "chunk_strategy": "qlora_train_seq_throttle",
        },
        "synced_at_utc": datetime.now(timezone.utc).isoformat(),
        "factory_run_root": str(factory_run_root),
    }
    write_text(run_root / "run_manifest.json", json.dumps(run_manifest, indent=2) + "\n")

    cmd = (
        '@echo off\n'
        f'set HF_DATASETS_CACHE=D:\\Research_Engine\\hf_cache\\{args.run_id}\n'
        f'set HF_HOME=D:\\Research_Engine\\hf_cache\\{args.run_id}\n'
        f'set XDG_CACHE_HOME=D:\\Research_Engine\\hf_cache\\{args.run_id}\n'
        f'set TMPDIR=D:\\Research_Engine\\tmp\\{args.run_id}\n'
        f'set TEMP=D:\\Research_Engine\\tmp\\{args.run_id}\n'
        f'set TMP=D:\\Research_Engine\\tmp\\{args.run_id}\n'
        f'"{args.python_exe}" "{args.trainer_script}" '
        f'--model-path "{args.qwen_model_path}" '
        f'--data-path "{train_messages}" '
        f'--output-dir "{train_root}" '
        f'--run-id "{args.run_id}" '
        f'--max-steps {args.max_steps} '
        f'--seq-len {args.seq_len} '
        f'--grad-accum {args.grad_accum} '
        f'--learning-rate {args.learning_rate} '
        f'--lora-rank {args.lora_rank} '
        f'--lora-alpha {args.lora_alpha} '
        f'--lora-dropout {args.lora_dropout} '
        f'--num-layers {args.lora_num_layers} '
        f'--target-modules {args.target_modules} '
        f'--event-jsonl "{event_jsonl}" '
        f'--state-json "{state_json}"\n'
        'set TRAIN_EXIT=%ERRORLEVEL%\n'
        'if %TRAIN_EXIT% neq 0 exit /b %TRAIN_EXIT%\n'
        f'if exist "{adapter_root}" rmdir /s /q "{adapter_root}"\n'
        f'xcopy /e /i /y "{train_root}\\final_adapter" "{adapter_root}\\" >nul\n'
        'exit /b %ERRORLEVEL%\n'
    )
    run_cmd = run_root / "run_train.cmd"
    write_text(run_cmd, cmd)

    if args.launch:
        import subprocess

        subprocess.run(["cmd.exe", "/c", str(run_cmd)], check=False)

    print(str(run_root))
    print(str(run_root / "run_manifest.json"))
    print(str(run_cmd))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
