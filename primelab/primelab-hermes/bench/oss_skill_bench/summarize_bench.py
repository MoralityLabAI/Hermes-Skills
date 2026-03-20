import argparse
import ast
import json
import math
import re
from pathlib import Path


LOSS_PATTERN = re.compile(r"'loss':\s*([0-9eE.+-]+)")


def parse_log(log_path: Path) -> dict:
    losses = []
    last_step_line = ""
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if "loss" in line:
                match = LOSS_PATTERN.search(line)
                if match:
                    try:
                        losses.append(float(match.group(1)))
                    except ValueError:
                        pass
            if "train_loss" in line or "loss" in line:
                last_step_line = line
    final_loss = losses[-1] if losses else None
    return {
        "loss_points": len(losses),
        "final_loss": final_loss,
        "finite_final_loss": final_loss is not None and math.isfinite(final_loss),
        "last_loss_line": last_step_line,
    }


def parse_run_meta(run_dir: Path) -> dict:
    meta_path = run_dir / "adapter" / "run_meta.json"
    if not meta_path.exists():
        return {"adapter_present": False}
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    payload["adapter_present"] = True
    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description="Summarize a small OSS skill bench run.")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--log", required=True)
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    log_path = Path(args.log)

    summary = {
      "run_dir": str(run_dir),
      "log": str(log_path),
      "log_summary": parse_log(log_path),
      "run_meta": parse_run_meta(run_dir),
    }

    out_path = run_dir / "bench_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
