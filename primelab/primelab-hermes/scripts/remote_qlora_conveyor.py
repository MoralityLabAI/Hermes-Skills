import argparse
import os
import subprocess
import sys
from pathlib import Path

from primelab_hermes.qlora_conveyor import append_receipt, load_spec, summarize_log, write_stage_state


def main() -> int:
    ap = argparse.ArgumentParser(description="Run a sequential QLoRA conveyor on a remote pod.")
    ap.add_argument("--spec-json", required=True)
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--run-root", required=True)
    ap.add_argument("--python-bin", default=sys.executable)
    args = ap.parse_args()

    spec = load_spec(args.spec_json)
    run_root = Path(args.run_root)
    data_root = Path(args.data_root)
    write_stage_state(run_root, "training", "running", spec_json=args.spec_json, env_count=len(spec["envs"]))
    append_receipt(run_root, "training", "started", spec_json=args.spec_json, env_count=len(spec["envs"]))

    env = dict(os.environ)
    env["PYTHONPATH"] = f"{Path.cwd() / 'src'}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)

    for entry in spec["envs"]:
        env_name = entry["name"]
        env_run_root = run_root / env_name
        env_run_root.mkdir(parents=True, exist_ok=True)
        log_path = run_root / "logs" / f"{env_name}.log"
        data_path = data_root / env_name / "train.jsonl"
        cmd = [
            args.python_bin,
            "scripts/train_qlora_sft.py",
            "--model",
            spec["model"],
            "--data",
            str(data_path),
            "--out",
            str(env_run_root),
            "--max-steps",
            str(spec["max_steps"]),
            "--seq-len",
            str(spec["seq_len"]),
            "--batch-size",
            str(spec["batch_size"]),
            "--lr",
            str(spec["lr"]),
            "--grad-accum",
            str(spec["grad_accum"]),
            "--lora-r",
            str(spec["lora_r"]),
            "--lora-alpha",
            str(spec["lora_alpha"]),
            "--lora-dropout",
            str(spec["lora_dropout"]),
            "--target-modules",
            str(spec["target_modules"]),
            "--seed",
            str(spec.get("seed", 1)),
        ]
        append_receipt(run_root, "training", "env_started", env=env_name, command=cmd, log_path=str(log_path))
        with log_path.open("w", encoding="utf-8") as log:
            proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, check=False, env=env)
        if proc.returncode != 0:
            tail = summarize_log(log_path)
            write_stage_state(run_root, "failed", "error", env=env_name, returncode=proc.returncode, log_path=str(log_path))
            append_receipt(
                run_root,
                "failed",
                "env_failed",
                env=env_name,
                returncode=proc.returncode,
                log_path=str(log_path),
                log_tail=tail,
            )
            raise SystemExit(proc.returncode)
        append_receipt(run_root, "training", "env_completed", env=env_name, log_path=str(log_path))

    write_stage_state(run_root, "validating", "complete", env_count=len(spec["envs"]))
    append_receipt(run_root, "validating", "complete", env_count=len(spec["envs"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
