"""Run local 3B on the leakage-safe logic signature camp-gate suite."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import subprocess
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil


ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "research" / "studies" / "2026-04-29-logic-signature-camp-gate-leakage-safe"
ROWS_PATH = STUDY / "rows" / "logic_signature_camp_gate_rows.jsonl"
VALIDATOR_PATH = STUDY / "validators" / "validate_logic_signature_camp_gate.py"
DEFAULT_OUT = STUDY / "results" / "local_qwen25_3b_logic_signature_camp_gate"

DEFAULT_MODEL = Path(r"D:\research_engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf")
DEFAULT_LLAMA_COMPLETION = Path(r"D:\research_engine\tools\llama.cpp-b8922-cuda12.4\llama-completion.exe")
PROMPT_ARMS = ("baseline", "pure_trm", "metta_runtime")
PROJECTION_ARM = "metta_signature_projection"
STOP_MARKERS = ("[end of text]", "<|im_end|>", "</s>")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local 3B logic signature camp-gate run.")
    parser.add_argument("--rows", default=str(ROWS_PATH))
    parser.add_argument("--validator", default=str(VALIDATOR_PATH))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL))
    parser.add_argument("--llama-completion-path", default=str(DEFAULT_LLAMA_COMPLETION))
    parser.add_argument("--max-cases", type=int, default=0, help="0 means all rows.")
    parser.add_argument("--case-ids", default="", help="Comma-separated row IDs. Empty means row order.")
    parser.add_argument("--ctx", type=int, default=1536)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--ubatch-size", type=int, default=32)
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--timeout-sec", type=int, default=120)
    parser.add_argument("--gpu-layers", default="all")
    parser.add_argument("--max-prompt-chars", type=int, default=6000)
    parser.add_argument("--max-child-rss-mb", type=float, default=2600.0)
    parser.add_argument("--cooldown-sec", type=float, default=0.5)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n")


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("logic_signature_camp_gate_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_rows(rows: list[dict[str, Any]], case_ids: str, max_cases: int) -> list[dict[str, Any]]:
    if case_ids.strip():
        wanted = [item.strip() for item in case_ids.split(",") if item.strip()]
        by_id = {row["row_id"]: row for row in rows}
        selected = [by_id[row_id] for row_id in wanted if row_id in by_id]
    else:
        selected = list(rows)
    if max_cases > 0:
        selected = selected[:max_cases]
    return selected


def public_contract(row: dict[str, Any], validator: Any) -> str:
    return json.dumps(validator.public_constraints(row), ensure_ascii=True, sort_keys=True)


def render_messages(messages: list[dict[str, str]]) -> str:
    system = "\n\n".join(item["content"] for item in messages if item.get("role") == "system").strip()
    user = "\n\n".join(item["content"] for item in messages if item.get("role") == "user").strip()
    if not system:
        system = "Return only the requested final answer."
    return (
        "<|im_start|>system\n"
        f"{system}<|im_end|>\n"
        "<|im_start|>user\n"
        f"{user}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def clean_model_output(text: str) -> str:
    cleaned = (text or "").strip()
    changed = True
    while changed:
        changed = False
        for marker in STOP_MARKERS:
            if cleaned.endswith(marker):
                cleaned = cleaned[: -len(marker)].strip()
                changed = True
    return cleaned


def arm_prompt(row: dict[str, Any], arm: str, validator: Any) -> list[dict[str, str]]:
    output_contract = (
        "Return only the grid. No markdown fence, no row labels, no explanation. "
        f"Use exactly {row['validator']['height']} lines of {row['validator']['width']} characters."
    )
    if arm == "baseline":
        return [
            {"role": "system", "content": output_contract},
            {"role": "user", "content": str(row["prompt"])},
        ]
    if arm == "pure_trm":
        return [
            {
                "role": "system",
                "content": (
                    "You are using a TRM-infused hard-logic skill. Internally parse the grid contract, "
                    "draft the grid, check row/column signatures, then emit only the final grid. "
                    + output_contract
                ),
            },
            {"role": "user", "content": f"Prompt:\n{row['prompt']}\n\nPublic contract:\n{public_contract(row, validator)}"},
        ]
    if arm == "metta_runtime":
        return [
            {
                "role": "system",
                "content": (
                    "You are inside a MeTTa-scaffolded TRM signature circuit. Gate sequence: "
                    "TRM_PARSE_GRID -> METTA_VALIDATE_FIXED_T -> TRM_CAMP_ROW_COL_SIGNATURE -> "
                    "METTA_ADJACENCY_CHECK -> TRM_COMMIT_GRID. Do not reveal reasoning. " + output_contract
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Prompt:\n{row['prompt']}\n\n"
                    f"Verifier-visible public constraints:\n{public_contract(row, validator)}\n\n"
                    "Commit one grid that passes the public constraints."
                ),
            },
        ]
    raise ValueError(f"unknown arm: {arm}")


def run_llama_completion(
    *,
    llama_completion: Path,
    model_path: Path,
    messages: list[dict[str, str]],
    ctx: int,
    threads: int,
    batch_size: int,
    ubatch_size: int,
    gpu_layers: str,
    max_tokens: int,
    timeout_sec: int,
    max_prompt_chars: int,
    max_child_rss_mb: float,
) -> tuple[str, dict[str, Any]]:
    prompt = render_messages(messages)
    if len(prompt) > max_prompt_chars:
        raise RuntimeError(f"prompt too long: {len(prompt)}>{max_prompt_chars}")
    cmd = [
        str(llama_completion),
        "-m",
        str(model_path),
        "-ngl",
        str(gpu_layers),
        "-c",
        str(ctx),
        "-t",
        str(threads),
        "-b",
        str(batch_size),
        "-ub",
        str(ubatch_size),
        "-n",
        str(max_tokens),
        "--no-warmup",
        "-ctk",
        "q8_0",
        "-ctv",
        "q8_0",
        "--temp",
        "0",
        "--top-p",
        "1",
        "--no-display-prompt",
        "--no-conversation",
        "--single-turn",
        "-p",
        prompt,
    ]
    start = time.time()
    stdout_fd, stdout_name = tempfile.mkstemp(prefix="camp_gate_stdout_", suffix=".log")
    stderr_fd, stderr_name = tempfile.mkstemp(prefix="camp_gate_stderr_", suffix=".log")
    os.close(stdout_fd)
    os.close(stderr_fd)
    stdout_path = Path(stdout_name)
    stderr_path = Path(stderr_name)
    peak_child_ram_mb = 0.0
    aborted = ""
    with stdout_path.open("w", encoding="utf-8", errors="replace") as stdout_handle, stderr_path.open(
        "w", encoding="utf-8", errors="replace"
    ) as stderr_handle:
        proc = subprocess.Popen(cmd, stdout=stdout_handle, stderr=stderr_handle, text=True)
        ps_proc = psutil.Process(proc.pid)
        while proc.poll() is None:
            elapsed = time.time() - start
            if elapsed > timeout_sec:
                aborted = f"timeout:{elapsed:.2f}>{timeout_sec}"
                proc.kill()
                proc.wait(timeout=10)
                break
            try:
                current_rss_mb = ps_proc.memory_info().rss / (1024 * 1024)
                peak_child_ram_mb = max(peak_child_ram_mb, current_rss_mb)
                if max_child_rss_mb > 0 and current_rss_mb > max_child_rss_mb:
                    aborted = f"child_rss_cap_exceeded:{current_rss_mb:.2f}>{max_child_rss_mb:.2f}"
                    proc.kill()
                    proc.wait(timeout=10)
                    break
            except psutil.Error:
                pass
            time.sleep(0.5)
    stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    stdout_path.unlink(missing_ok=True)
    stderr_path.unlink(missing_ok=True)
    diagnostics = {
        "returncode": proc.returncode,
        "elapsed_sec": round(time.time() - start, 4),
        "peak_child_ram_mb": round(peak_child_ram_mb, 4),
        "stderr_tail": stderr[-2000:],
        "raw_output_tail": stdout[-500:],
    }
    if aborted:
        diagnostics["abort_reason"] = aborted
        raise RuntimeError(aborted)
    if proc.returncode != 0:
        raise RuntimeError(f"llama-completion failed rc={proc.returncode}; stderr_tail={stderr[-2000:]}")
    return clean_model_output(stdout), diagnostics


def evaluate_candidate(validator: Any, row: dict[str, Any], output: str, arm: str, diagnostics: dict[str, Any]) -> dict[str, Any]:
    verdict = validator.validate_output(row, output)
    return {
        "ts": utc_now(),
        "row_id": row["row_id"],
        "env_family": row["env_family"],
        "arm": arm,
        "output": output,
        "evidence_class": "live_model_local_3b" if arm != PROJECTION_ARM else "live_model_local_3b_prompt_constraint_projection",
        "contract_valid": verdict["contract_valid"],
        "semantic_valid": verdict["semantic_valid"],
        "exact_success": verdict["exact_success"],
        "cell_accuracy": verdict["cell_accuracy"],
        "proposal_tier": verdict["proposal_tier"],
        "details": verdict["details"],
        "diagnostics": diagnostics,
    }


def error_candidate(row: dict[str, Any], arm: str, error: str) -> dict[str, Any]:
    return {
        "ts": utc_now(),
        "row_id": row["row_id"],
        "env_family": row["env_family"],
        "arm": arm,
        "output": "",
        "evidence_class": "live_model_local_3b_error",
        "contract_valid": False,
        "semantic_valid": False,
        "exact_success": False,
        "cell_accuracy": 0.0,
        "proposal_tier": "none",
        "details": {"kind": "runner_error", "error": error},
        "diagnostics": {"error": error},
    }


def summarize(evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    arms = sorted({row["arm"] for row in evaluated})
    by_arm: dict[str, dict[str, Any]] = {}
    for arm in arms:
        rows = [row for row in evaluated if row["arm"] == arm]
        tiers = Counter(str(row.get("proposal_tier", "unknown")) for row in rows)
        by_arm[arm] = {
            "rows": len(rows),
            "contract_valid": sum(1 for row in rows if row["contract_valid"]),
            "semantic_valid": sum(1 for row in rows if row["semantic_valid"]),
            "exact_success": sum(1 for row in rows if row["exact_success"]),
            "contract_rate": sum(1 for row in rows if row["contract_valid"]) / max(1, len(rows)),
            "exact_rate": sum(1 for row in rows if row["exact_success"]) / max(1, len(rows)),
            "avg_cell_accuracy": sum(float(row.get("cell_accuracy", 0.0)) for row in rows) / max(1, len(rows)),
            "proposal_tier_counts": dict(tiers),
        }
    return {
        "evidence_class": "live_model_local_3b",
        "rows": len({row["row_id"] for row in evaluated}),
        "arms": by_arm,
        "peak_child_ram_mb": max(
            (float(row.get("diagnostics", {}).get("peak_child_ram_mb", 0.0)) for row in evaluated),
            default=0.0,
        ),
        "note": "Projection uses prompt-derived constraints only; do not report it as trained TRM lift.",
    }


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Local Qwen2.5-3B Logic Signature Camp-Gate Run",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "Evidence class: `live_model_local_3b` plus prompt-constraint projection.",
        "",
        f"Model: `{payload['model_path']}`",
        f"llama.cpp completion: `{payload['llama_completion_path']}`",
        f"Peak child RSS: `{payload['summary']['peak_child_ram_mb']:.2f} MB`",
        "",
        "## Arm Summary",
        "",
        "| Arm | Rows | Exact | Exact Rate | Contract Valid | Avg Cell Acc | Tier Counts |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for arm, metrics in payload["summary"]["arms"].items():
        tiers = ", ".join(f"{key}:{value}" for key, value in sorted(metrics["proposal_tier_counts"].items()))
        lines.append(
            f"| `{arm}` | {metrics['rows']} | {metrics['exact_success']} | {metrics['exact_rate']:.4f} | "
            f"{metrics['contract_valid']} | {metrics['avg_cell_accuracy']:.4f} | {tiers or '-'} |"
        )
    lines.extend(
        [
            "",
            "## Case Detail",
            "",
            "| Row | Arm | Tier | Exact | Contract | Cell Acc | Output |",
            "| --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in payload["evaluated"]:
        output = html.escape(str(row.get("output", "")).replace("\n", "\\n")).replace("|", "\\|")
        lines.append(
            f"| `{row['row_id']}` | `{row['arm']}` | `{row.get('proposal_tier', '-')}` | "
            f"{int(row['exact_success'])} | {int(row['contract_valid'])} | {float(row.get('cell_accuracy', 0.0)):.4f} | "
            f"<code>{output[:220]}</code> |"
        )
    lines.extend(
        [
            "",
            "## Claim Audit",
            "",
            "- Allowed: this measures whether local 3B emits enough verifier-visible grid state for prompt-derived symbolic closure.",
            "- Not allowed: do not call the projection arm trained TRM lift or hidden reasoning improvement.",
            "- Not allowed: do not treat this as an Intellect-3 leaderboard result; it is a leakage-safe micro-env.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(out_dir: Path, payload: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    results_json = out_dir / "local_qwen25_3b_logic_signature_camp_gate.results.json"
    results_md = out_dir / "local_qwen25_3b_logic_signature_camp_gate.results.md"
    results_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    results_md.write_text(render_md(payload), encoding="utf-8")
    print(results_md)
    print(results_json)


def main() -> int:
    args = parse_args()
    rows_path = Path(args.rows).resolve()
    validator_path = Path(args.validator).resolve()
    out_dir = Path(args.out_dir).resolve()
    model_path = Path(args.model_path).resolve()
    llama_completion = Path(args.llama_completion_path).resolve()

    if not model_path.exists():
        raise SystemExit(f"model not found: {model_path}")
    if not llama_completion.exists():
        raise SystemExit(f"llama-completion not found: {llama_completion}")

    rows = select_rows(load_jsonl(rows_path), args.case_ids, args.max_cases)
    validator = load_validator(validator_path)
    events_path = out_dir / "local_qwen25_3b_logic_signature_camp_gate.events.jsonl"
    if events_path.exists():
        events_path.unlink()
    evaluated: list[dict[str, Any]] = []

    for row in rows:
        metta_output = ""
        metta_result: dict[str, Any] | None = None
        for arm in PROMPT_ARMS:
            try:
                output, diagnostics = run_llama_completion(
                    llama_completion=llama_completion,
                    model_path=model_path,
                    messages=arm_prompt(row, arm, validator),
                    ctx=args.ctx,
                    threads=args.threads,
                    batch_size=args.batch_size,
                    ubatch_size=args.ubatch_size,
                    gpu_layers=args.gpu_layers,
                    max_tokens=args.max_tokens,
                    timeout_sec=args.timeout_sec,
                    max_prompt_chars=args.max_prompt_chars,
                    max_child_rss_mb=args.max_child_rss_mb,
                )
                result = evaluate_candidate(validator, row, output, arm, diagnostics)
            except RuntimeError as exc:
                result = error_candidate(row, arm, str(exc))
            evaluated.append(result)
            append_jsonl(events_path, result)
            if arm == "metta_runtime":
                metta_output = str(result.get("output", ""))
                metta_result = result
            time.sleep(args.cooldown_sec)
            if "child_rss_cap_exceeded" in str(result.get("diagnostics", {}).get("error", "")):
                break

        if metta_result is None:
            continue
        projected, projection = validator.project_output(row, metta_output)
        if projected is None:
            projection_result = error_candidate(row, PROJECTION_ARM, projection.get("reason", "projection_failed"))
            projection_result["diagnostics"] = projection
        else:
            projection_result = evaluate_candidate(
                validator,
                row,
                projected,
                PROJECTION_ARM,
                {"projection": projection, "peak_child_ram_mb": 0.0, "elapsed_sec": 0.0},
            )
        evaluated.append(projection_result)
        append_jsonl(events_path, projection_result)
        if "child_rss_cap_exceeded" in str(projection_result.get("diagnostics", {}).get("error", "")):
            break

    payload = {
        "generated_at_utc": utc_now(),
        "model_path": str(model_path),
        "llama_completion_path": str(llama_completion),
        "rows_path": str(rows_path),
        "validator_path": str(validator_path),
        "config": {
            "case_ids": [row["row_id"] for row in rows],
            "ctx": args.ctx,
            "threads": args.threads,
            "batch_size": args.batch_size,
            "ubatch_size": args.ubatch_size,
            "max_tokens": args.max_tokens,
            "timeout_sec": args.timeout_sec,
            "gpu_layers": args.gpu_layers,
            "max_child_rss_mb": args.max_child_rss_mb,
        },
        "summary": summarize(evaluated),
        "evaluated": evaluated,
    }
    write_outputs(out_dir, payload)
    print(events_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
