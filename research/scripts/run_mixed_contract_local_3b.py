"""Run a capped local 3B smoke for mixed-contract compactification.

This replaces deterministic seed candidates with local Qwen2.5-3B Q4
completions while preserving the same row IDs and exact validators from the
mixed-contract seed study.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import subprocess
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil


ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "research" / "studies" / "2026-04-28-mixed-contract-compactification-seed"
ROWS_PATH = STUDY / "rows" / "mixed_contract_seed_rows.jsonl"
VALIDATOR_PATH = STUDY / "validators" / "validate_mixed_contracts.py"
DEFAULT_OUT = STUDY / "results" / "local_qwen25_3b_mixed_contract_smoke"

DEFAULT_MODEL = Path(r"D:\research_engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf")
DEFAULT_LLAMA_COMPLETION = Path(r"D:\research_engine\tools\llama.cpp-b8922-cuda12.4\llama-completion.exe")

PROMPT_ARMS = ("baseline", "pure_trm", "metta_runtime")
BLIND_REPAIR_ARM = "metta_runtime_blind_repair"
FEEDBACK_REPAIR_ARM = "metta_runtime_repair"
ALL_ARMS = (*PROMPT_ARMS, BLIND_REPAIR_ARM, FEEDBACK_REPAIR_ARM)
STOP_MARKERS = ("[end of text]", "<|im_end|>", "</s>")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local 3B mixed-contract smoke.")
    parser.add_argument("--rows", default=str(ROWS_PATH))
    parser.add_argument("--validator", default=str(VALIDATOR_PATH))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL))
    parser.add_argument("--llama-completion-path", default=str(DEFAULT_LLAMA_COMPLETION))
    parser.add_argument("--case-ids", default="", help="Comma-separated row IDs. Empty means row order.")
    parser.add_argument("--max-cases", type=int, default=6, help="0 means all selected rows.")
    parser.add_argument("--ctx", type=int, default=1536)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--ubatch-size", type=int, default=32)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--timeout-sec", type=int, default=120)
    parser.add_argument("--gpu-layers", default="all")
    parser.add_argument("--max-prompt-chars", type=int, default=5000)
    parser.add_argument("--max-child-rss-mb", type=float, default=2600.0)
    parser.add_argument("--cooldown-sec", type=float, default=0.5)
    parser.add_argument("--run-title", default="Local Qwen2.5-3B Mixed Contract Run")
    parser.add_argument(
        "--run-note",
        default="This run replaces deterministic candidates with local 3B completions for the supplied row IDs and validators. Interpret it according to the study claim audit.",
    )
    parser.add_argument(
        "--include-blind-repair",
        action="store_true",
        help="Add a repair arm that receives the prior output but not validator feedback.",
    )
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n")


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("mixed_contract_validator", path)
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


def public_validator(row: dict[str, Any]) -> dict[str, Any]:
    validator = dict(row["validator"])
    validator.pop("expected", None)
    validator.pop("expected_values", None)
    return validator


def row_contract(row: dict[str, Any]) -> str:
    return json.dumps(
        {
            "env_family": row["env_family"],
            "failure_labels": row.get("failure_labels", []),
            "validator": public_validator(row),
        },
        ensure_ascii=True,
        sort_keys=True,
    )


def render_messages(messages: list[dict[str, str]]) -> str:
    system = "\n\n".join(item["content"] for item in messages if item.get("role") == "system").strip()
    user = "\n\n".join(item["content"] for item in messages if item.get("role") == "user").strip()
    if not system:
        system = "You return only the requested final answer."
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


def arm_prompt(row: dict[str, Any], arm: str) -> list[dict[str, str]]:
    if arm == "baseline":
        return [
            {
                "role": "system",
                "content": "Return only the final answer. No markdown fences, labels, rationale, or extra explanation.",
            },
            {"role": "user", "content": str(row["prompt"])},
        ]
    if arm == "pure_trm":
        return [
            {
                "role": "system",
                "content": (
                    "You are using a TRM-infused Hermes skill. Parse the contract, draft the answer, "
                    "then internally verify it. Emit only the final answer."
                ),
            },
            {
                "role": "user",
                "content": f"Prompt:\n{row['prompt']}\n\nPublic validator contract:\n{row_contract(row)}",
            },
        ]
    if arm == "metta_runtime":
        return [
            {
                "role": "system",
                "content": (
                    "You are inside a MeTTa-scaffolded TRM circuit. Gate sequence: "
                    "TRM_PARSE_CONTRACT -> METTA_SELECT_CONTRACT -> TRM_DRAFT -> "
                    "METTA_VALIDATE_OBSERVABLE_STATE -> TRM_COMMIT. Emit only the committed answer."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Prompt:\n{row['prompt']}\n\n"
                    f"Verifier-visible state:\n{row_contract(row)}\n\n"
                    "Do not expose chain of thought. Return only the final output that passes the public validator."
                ),
            },
        ]
    raise ValueError(f"unknown prompt arm: {arm}")


def repair_prompt(row: dict[str, Any], previous_output: str, verdict: dict[str, Any]) -> list[dict[str, str]]:
    feedback = {
        "contract_valid": verdict["contract_valid"],
        "semantic_valid": verdict["semantic_valid"],
        "details": verdict["details"],
    }
    return [
        {
            "role": "system",
            "content": (
                "You are the repair gate in a MeTTa/TRM circuit. Repair the previous output using only "
                "the prompt and public validator. Emit only the repaired final answer."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Prompt:\n{row['prompt']}\n\n"
                f"Public validator contract:\n{row_contract(row)}\n\n"
                f"Previous output:\n{previous_output}\n\n"
                f"Validator feedback:\n{json.dumps(feedback, ensure_ascii=True, sort_keys=True)}"
            ),
        },
    ]


def blind_repair_prompt(row: dict[str, Any], previous_output: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are the blind repair gate in a MeTTa/TRM circuit. The previous output failed a hidden check, "
                "but you may not inspect validator feedback. Use only the prompt, public contract, and previous "
                "output. Emit only the repaired final answer."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Prompt:\n{row['prompt']}\n\n"
                f"Public validator contract:\n{row_contract(row)}\n\n"
                f"Previous output:\n{previous_output}\n\n"
                "Return one corrected final output. No explanation."
            ),
        },
    ]


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
    stdout_fd, stdout_name = tempfile.mkstemp(prefix="mixed_contract_stdout_", suffix=".log")
    stderr_fd, stderr_name = tempfile.mkstemp(prefix="mixed_contract_stderr_", suffix=".log")
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
    elapsed_sec = round(time.time() - start, 4)
    diagnostics = {
        "returncode": proc.returncode,
        "elapsed_sec": elapsed_sec,
        "peak_child_ram_mb": round(peak_child_ram_mb, 4),
        "stderr_tail": stderr[-2000:],
    }
    if aborted:
        diagnostics["abort_reason"] = aborted
        raise RuntimeError(aborted)
    if proc.returncode != 0:
        raise RuntimeError(f"llama-completion failed rc={proc.returncode}; stderr_tail={stderr[-2000:]}")
    diagnostics["raw_output_tail"] = stdout[-500:]
    return clean_model_output(stdout), diagnostics


def evaluate_candidate(validator: Any, row: dict[str, Any], output: str, arm: str, diagnostics: dict[str, Any]) -> dict[str, Any]:
    verdict = validator.validate(row, output)
    return {
        "ts": utc_now(),
        "row_id": row["row_id"],
        "env_family": row["env_family"],
        "arm": arm,
        "output": output,
        "evidence_class": "live_model_local_3b",
        "contract_valid": verdict["contract_valid"],
        "semantic_valid": verdict["semantic_valid"],
        "exact_success": verdict["exact_success"],
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
        "details": {"kind": "runner_error", "error": error},
        "diagnostics": {"error": error},
    }


def summarize(evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    by_arm: dict[str, dict[str, Any]] = {}
    by_family: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    arms = sorted({row["arm"] for row in evaluated})
    families = sorted({row["env_family"] for row in evaluated})
    for arm in arms:
        rows = [row for row in evaluated if row["arm"] == arm]
        by_arm[arm] = {
            "rows": len(rows),
            "contract_valid": sum(row["contract_valid"] for row in rows),
            "semantic_valid": sum(row["semantic_valid"] for row in rows),
            "exact_success": sum(row["exact_success"] for row in rows),
            "contract_rate": sum(row["contract_valid"] for row in rows) / max(1, len(rows)),
            "semantic_rate": sum(row["semantic_valid"] for row in rows) / max(1, len(rows)),
            "exact_rate": sum(row["exact_success"] for row in rows) / max(1, len(rows)),
        }
        for family in families:
            family_rows = [row for row in rows if row["env_family"] == family]
            if family_rows:
                by_family[arm][family] = {
                    "rows": len(family_rows),
                    "exact_success": sum(row["exact_success"] for row in family_rows),
                    "exact_rate": sum(row["exact_success"] for row in family_rows) / len(family_rows),
                }
    peak_child_ram_mb = max(
        (float(row.get("diagnostics", {}).get("peak_child_ram_mb", 0.0)) for row in evaluated),
        default=0.0,
    )
    by_key = {(row["row_id"], row["arm"]): row for row in evaluated}
    metta_fail_ids = sorted(
        {
            row["row_id"]
            for row in evaluated
            if row["arm"] == "metta_runtime" and not row["exact_success"]
        }
    )
    repair_opportunities: dict[str, Any] = {"metta_runtime_failed_rows": len(metta_fail_ids), "arms": {}}
    for arm in (BLIND_REPAIR_ARM, FEEDBACK_REPAIR_ARM):
        arm_rows = [by_key[(row_id, arm)] for row_id in metta_fail_ids if (row_id, arm) in by_key]
        if arm_rows:
            repair_opportunities["arms"][arm] = {
                "rows": len(arm_rows),
                "exact_success": sum(row["exact_success"] for row in arm_rows),
                "exact_rate": sum(row["exact_success"] for row in arm_rows) / len(arm_rows),
                "contract_valid": sum(row["contract_valid"] for row in arm_rows),
                "semantic_valid": sum(row["semantic_valid"] for row in arm_rows),
            }
    return {
        "evidence_class": "live_model_local_3b",
        "rows": len({row["row_id"] for row in evaluated}),
        "arms": by_arm,
        "by_family": by_family,
        "repair_opportunities": repair_opportunities,
        "peak_child_ram_mb": peak_child_ram_mb,
        "note": "Local Qwen2.5-3B Q4 smoke. Keep separate from deterministic validator smoke.",
    }


def render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"# {payload.get('run_title', 'Local Qwen2.5-3B Mixed Contract Run')}",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "Evidence class: `live_model_local_3b`",
        "",
        f"Model: `{payload['model_path']}`",
        f"llama.cpp completion: `{payload['llama_completion_path']}`",
        f"Peak child RSS: `{summary['peak_child_ram_mb']:.2f} MB`",
        "",
        str(payload.get("run_note", "")),
        "",
        "## Arm Summary",
        "",
        "| Arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm, metrics in summary["arms"].items():
        lines.append(
            f"| `{arm}` | {metrics['rows']} | {metrics['contract_valid']} | {metrics['semantic_valid']} | {metrics['exact_success']} | {metrics['exact_rate']:.4f} |"
        )
    repair_opportunities = summary.get("repair_opportunities", {})
    if repair_opportunities.get("arms"):
        lines.extend(
            [
                "",
                "## Repair Opportunity Summary",
                "",
                f"Rows where `metta_runtime` failed exactly: `{repair_opportunities.get('metta_runtime_failed_rows', 0)}`",
                "",
                "| Repair arm | Rows | Contract valid | Semantic valid | Exact success | Exact rate |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for arm, metrics in repair_opportunities["arms"].items():
            lines.append(
                f"| `{arm}` | {metrics['rows']} | {metrics['contract_valid']} | {metrics['semantic_valid']} | {metrics['exact_success']} | {metrics['exact_rate']:.4f} |"
            )
    lines.extend(["", "## Case Detail", "", "| Row | Family | Arm | Exact | Contract | Semantic | Output |", "| --- | --- | --- | ---: | ---: | ---: | --- |"])
    for row in payload["evaluated"]:
        output = html.escape(str(row["output"]).replace("\n", "\\n")).replace("|", "\\|")
        lines.append(
            f"| `{row['row_id']}` | `{row['env_family']}` | `{row['arm']}` | {int(row['exact_success'])} | {int(row['contract_valid'])} | {int(row['semantic_valid'])} | <code>{output[:220]}</code> |"
        )
    lines.extend(
        [
            "",
            "## Claim Audit",
            "",
            "- Allowed: this is a live local 3B result against frozen validators.",
            "- Not allowed: do not call this trained TRM lift; interpret benchmark status according to the study claim audit and row-suite scope.",
            "- Not allowed: do not call `metta_runtime_repair` learned TRM lift; it is a repair-prompt arm using the same 3B model plus public validator feedback.",
            "- Not allowed: do not conflate `metta_runtime_blind_repair` with validator-feedback repair; blind repair receives no validator verdict details.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(out_dir: Path, payload: dict[str, Any]) -> None:
    results_json = out_dir / "local_qwen25_3b_mixed_contract.results.json"
    results_md = out_dir / "local_qwen25_3b_mixed_contract.results.md"
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

    out_dir.mkdir(parents=True, exist_ok=True)
    rows = select_rows(load_jsonl(rows_path), args.case_ids, args.max_cases)
    validator = load_validator(validator_path)
    evaluated: list[dict[str, Any]] = []
    events_path = out_dir / "local_qwen25_3b_mixed_contract.events.jsonl"
    if events_path.exists():
        events_path.unlink()

    for row in rows:
        metta_output = ""
        metta_verdict: dict[str, Any] | None = None
        for arm in PROMPT_ARMS:
            try:
                output, diagnostics = run_llama_completion(
                    llama_completion=llama_completion,
                    model_path=model_path,
                    messages=arm_prompt(row, arm),
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
                metta_output = str(result["output"])
                metta_verdict = result
            time.sleep(args.cooldown_sec)
            if "child_rss_cap_exceeded" in str(result.get("diagnostics", {}).get("error", "")):
                break

        if metta_verdict is None:
            continue
        repair_arms = []
        if args.include_blind_repair:
            repair_arms.append(BLIND_REPAIR_ARM)
        repair_arms.append(FEEDBACK_REPAIR_ARM)
        for repair_arm in repair_arms:
            if metta_verdict["exact_success"]:
                repair_result = evaluate_candidate(
                    validator,
                    row,
                    metta_output,
                    repair_arm,
                    {"repair_source": "metta_runtime_already_exact", "elapsed_sec": 0.0, "peak_child_ram_mb": 0.0},
                )
            elif "child_rss_cap_exceeded" in str(metta_verdict.get("diagnostics", {}).get("error", "")):
                repair_result = error_candidate(row, repair_arm, "skipped_after_child_rss_cap_exceeded")
            else:
                try:
                    messages = (
                        blind_repair_prompt(row, metta_output)
                        if repair_arm == BLIND_REPAIR_ARM
                        else repair_prompt(row, metta_output, metta_verdict)
                    )
                    output, diagnostics = run_llama_completion(
                        llama_completion=llama_completion,
                        model_path=model_path,
                        messages=messages,
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
                    repair_result = evaluate_candidate(validator, row, output, repair_arm, diagnostics)
                except RuntimeError as exc:
                    repair_result = error_candidate(row, repair_arm, str(exc))
            evaluated.append(repair_result)
            append_jsonl(events_path, repair_result)
            time.sleep(args.cooldown_sec)
            if "child_rss_cap_exceeded" in str(repair_result.get("diagnostics", {}).get("error", "")):
                break
        if any(
            "child_rss_cap_exceeded" in str(result.get("diagnostics", {}).get("error", ""))
            for result in evaluated[-len(repair_arms) :]
        ):
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
            "run_title": args.run_title,
            "run_note": args.run_note,
            "include_blind_repair": args.include_blind_repair,
        },
        "run_title": args.run_title,
        "run_note": args.run_note,
        "summary": summarize(evaluated),
        "evaluated": evaluated,
    }
    write_outputs(out_dir, payload)
    print(events_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
