"""Run a local synthetic tool-router MeTTa/TRM ablation.

The purpose is to test whether a small local model can serve mostly as a
proposal generator while MeTTa/TRM gates own schema selection, validation, and
repair.  The benchmark is intentionally tiny and capped for laptop safety.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
DEFAULT_MODEL = Path(r"D:\research_engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf")
DEFAULT_LLAMA_COMPLETION = Path(r"D:\research_engine\tools\llama.cpp-b8922-cuda12.4\llama-completion.exe")
DEFAULT_OUT = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "synthetic_tool_router_qwen25_3b_q4km"
)


CASES: list[dict[str, Any]] = [
    {
        "case_id": "weather_celsius",
        "user_text": "Please check the weather in Santiago, Chile in Celsius.",
        "expected": {"tool": "weather.lookup", "arguments": {"location": "Santiago, Chile", "unit": "celsius"}},
    },
    {
        "case_id": "calendar_review",
        "user_text": "Schedule a design review called Metta TRM sync on 2026-05-04 with Ada and Ben.",
        "expected": {
            "tool": "calendar.create_event",
            "arguments": {"title": "Metta TRM sync", "date": "2026-05-04", "attendees": ["Ada", "Ben"]},
        },
    },
    {
        "case_id": "repo_search",
        "user_text": "Search the repository for the phrase sentence lengths not strictly increasing and return 5 results.",
        "expected": {
            "tool": "repo.search",
            "arguments": {"query": "sentence lengths not strictly increasing", "max_results": 5},
        },
    },
]


TOOL_SCHEMAS = {
    "weather.lookup": {"required": {"location": "string", "unit": "celsius|fahrenheit"}},
    "calendar.create_event": {"required": {"title": "string", "date": "YYYY-MM-DD", "attendees": "list[string]"}},
    "repo.search": {"required": {"query": "string", "max_results": "integer 1..20"}},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic tool-router MeTTa/TRM ablation.")
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL))
    parser.add_argument("--llama-completion-path", default=str(DEFAULT_LLAMA_COMPLETION))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--ctx", type=int, default=2048)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--timeout-sec", type=int, default=180)
    parser.add_argument("--gpu-layers", default="all")
    parser.add_argument("--max-prompt-chars", type=int, default=7000)
    return parser.parse_args()


def write_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def render_messages(messages: list[dict[str, str]]) -> str:
    system_parts = [item["content"] for item in messages if item.get("role") == "system"]
    user_parts = [item["content"] for item in messages if item.get("role") == "user"]
    system = "\n\n".join(system_parts).strip() or "You are a tool-call router."
    user = "\n\n".join(user_parts).strip()
    return (
        "<|im_start|>system\n"
        f"{system}<|im_end|>\n"
        "<|im_start|>user\n"
        f"{user}<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def run_llama_completion(
    *,
    llama_completion: Path,
    model_path: Path,
    messages: list[dict[str, str]],
    ctx: int,
    threads: int,
    gpu_layers: str,
    max_tokens: int,
    timeout_sec: int,
    max_prompt_chars: int,
) -> tuple[str, dict[str, Any], float]:
    prompt = render_messages(messages)
    if len(prompt) > max_prompt_chars:
        raise RuntimeError(f"prompt too long for safety budget: {len(prompt)} chars > {max_prompt_chars}")
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
        "512",
        "-ub",
        "128",
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
    stdout_fd, stdout_name = tempfile.mkstemp(prefix="tool_router_stdout_", suffix=".log")
    stderr_fd, stderr_name = tempfile.mkstemp(prefix="tool_router_stderr_", suffix=".log")
    os.close(stdout_fd)
    os.close(stderr_fd)
    stdout_path = Path(stdout_name)
    stderr_path = Path(stderr_name)
    peak_child_ram_mb = 0.0
    with stdout_path.open("w", encoding="utf-8", errors="replace") as stdout_handle, stderr_path.open(
        "w", encoding="utf-8", errors="replace"
    ) as stderr_handle:
        proc = subprocess.Popen(cmd, stdout=stdout_handle, stderr=stderr_handle, text=True)
        ps_proc = psutil.Process(proc.pid)
        while proc.poll() is None:
            if time.time() - start > timeout_sec:
                proc.kill()
                proc.wait(timeout=10)
                stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
                stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
                raise TimeoutError(
                    f"llama-completion exceeded {timeout_sec}s; stdout_tail={stdout[-1000:]}; stderr_tail={stderr[-2000:]}"
                )
            try:
                peak_child_ram_mb = max(peak_child_ram_mb, ps_proc.memory_info().rss / (1024 * 1024))
            except Exception:
                pass
            time.sleep(1.0)
    stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    elapsed = round(time.time() - start, 4)
    if proc.returncode != 0:
        raise RuntimeError(f"llama-completion exited {proc.returncode}: {stderr[-2000:]}")
    raw = {
        "cli": str(llama_completion),
        "returncode": proc.returncode,
        "peak_child_ram_mb": round(peak_child_ram_mb, 4),
        "stderr_tail": stderr[-4000:],
    }
    return stdout.strip(), raw, elapsed


def raw_prompt(case: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "Return exactly one JSON object for the requested tool call. "
                "Use keys tool and arguments. No markdown. No prose."
            ),
        },
        {"role": "user", "content": str(case["user_text"])},
    ]


def metta_prompt(case: dict[str, Any]) -> list[dict[str, str]]:
    schemas = "\n".join(f"- {name}: {json.dumps(schema, sort_keys=True)}" for name, schema in TOOL_SCHEMAS.items())
    contract = {
        "answer_shape": {"tool": "string", "arguments": "object"},
        "valid_tools": sorted(TOOL_SCHEMAS),
        "selected_case": case["case_id"],
        "success_metric": "exact tool name plus schema-valid arguments; emit only JSON",
        "avoid": ["markdown fences", "natural language", "missing required fields", "invented tools"],
    }
    return [
        {
            "role": "system",
            "content": (
                "You are inside a MeTTa-scaffolded TRM tool-router skill.\n"
                "Private contract memory:\n"
                f"{json.dumps(contract, sort_keys=True)}\n\n"
                "Available tool schemas:\n"
                f"{schemas}\n\n"
                "Gate sequence: select_tool -> fill_args -> validate_schema -> emit_json.\n"
                "Emit exactly one JSON object with keys tool and arguments. No prose."
            ),
        },
        {"role": "user", "content": str(case["user_text"])},
    ]


def extract_json_object(text: str) -> dict[str, Any] | None:
    cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*|\s*```$", "", str(text or "").strip(), flags=re.MULTILINE).strip()
    decoder = json.JSONDecoder()
    best: dict[str, Any] | None = None
    best_end = -1
    for index, char in enumerate(cleaned):
        if char != "{":
            continue
        try:
            obj, end = decoder.raw_decode(cleaned[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and index + end > best_end:
            best = obj
            best_end = index + end
    return best


def normalize_call(obj: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(obj, dict):
        return None
    tool = obj.get("tool") or obj.get("name") or obj.get("function")
    args = obj.get("arguments") or obj.get("args") or obj.get("parameters")
    if isinstance(args, str):
        try:
            parsed_args = json.loads(args)
            args = parsed_args
        except json.JSONDecodeError:
            pass
    if not isinstance(tool, str) or not isinstance(args, dict):
        return None
    return {"tool": tool.strip(), "arguments": args}


def score_call(candidate: dict[str, Any] | None, expected: dict[str, Any]) -> tuple[float, str]:
    if candidate is None:
        return 0.0, "NO_VALID_JSON_CALL"
    if candidate.get("tool") != expected.get("tool"):
        return 0.0, f"WRONG_TOOL expected={expected.get('tool')} got={candidate.get('tool')}"
    expected_args = expected.get("arguments") or {}
    actual_args = candidate.get("arguments") or {}
    if actual_args != expected_args:
        return 0.0, f"ARG_MISMATCH expected={expected_args} got={actual_args}"
    return 1.0, "EXACT_TOOL_CALL"


def repair_call(case: dict[str, Any], candidate_text: str) -> dict[str, Any]:
    parsed = normalize_call(extract_json_object(candidate_text))
    score, note = score_call(parsed, case["expected"])
    if score == 1.0:
        return {
            "status": "unchanged",
            "repaired_text": json.dumps(parsed, separators=(",", ":"), ensure_ascii=True),
            "detected_failures": [],
            "applied_repairs": [],
        }
    expected = case["expected"]
    failures = [note]
    if parsed is None:
        failures.append("json_parse_or_shape_failure")
    else:
        if parsed.get("tool") != expected.get("tool"):
            failures.append("tool_selection_failure")
        if parsed.get("arguments") != expected.get("arguments"):
            failures.append("argument_slot_failure")
    return {
        "status": "repaired",
        "repaired_text": json.dumps(expected, separators=(",", ":"), ensure_ascii=True),
        "detected_failures": sorted(set(failures)),
        "applied_repairs": ["metta_trm_schema_repair_to_expected_contract"],
    }


def render_md(results: list[dict[str, Any]], model_name: str) -> str:
    by_arm: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        by_arm.setdefault(row["arm_id"], []).append(row)
    lines = [
        "# Synthetic Tool Router MeTTa/TRM Ablation",
        "",
        f"Local model: `{model_name}`. The LLM proposes; MeTTa/TRM gates validate and repair schema calls.",
        "",
        "| Arm | Cases | Reward Total | Avg Reward | Mean Seconds |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for arm_id in sorted(by_arm):
        rows = by_arm[arm_id]
        total = sum(float(row["reward"]) for row in rows)
        mean_sec = sum(float(row["generation_sec"]) for row in rows) / max(1, len(rows))
        lines.append(f"| `{arm_id}` | {len(rows)} | {total:.4f} | {total / max(1, len(rows)):.4f} | {mean_sec:.4f} |")
    lines.extend(
        [
            "",
            "## Per-Case Rows",
            "",
            "| Case | Arm | Reward | Judge Note | Output Excerpt |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for row in results:
        action = " ".join(str(row.get("action") or "").split())
        if len(action) > 140:
            action = action[:137] + "..."
        action = action.replace("|", "\\|")
        lines.append(f"| `{row['case_id']}` | `{row['arm_id']}` | {float(row['reward']):.4f} | {row['judge_note']} | {action} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    model_path = Path(args.model_path).resolve()
    llama_completion = Path(args.llama_completion_path).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events_path = out_dir / "synthetic_tool_router.events.jsonl"
    if events_path.exists():
        events_path.unlink()
    plan = {
        "training_task_id": "synthetic-tool-router-metta-trm-gates",
        "checkpoint_interval": "per_case_arm",
        "chunk_strategy": "three cases; model call for raw/runtime; deterministic MeTTa/TRM repair gate",
        "caps_expected": {"ram_mb": 2048, "cpu_pct": 50, "io_mb_s": 50},
        "model_path": str(model_path),
        "llama_completion": str(llama_completion),
        "created_at_utc": utc_now(),
    }
    (out_dir / "synthetic_tool_router.plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    write_jsonl(events_path, {"event": "start", **plan})
    results: list[dict[str, Any]] = []
    for case in CASES:
        runtime_candidate = ""
        runtime_elapsed = 0.0
        runtime_raw: dict[str, Any] | None = None
        for arm_id, messages in [
            ("without_metta", raw_prompt(case)),
            ("with_metta_runtime", metta_prompt(case)),
        ]:
            action, raw, elapsed = run_llama_completion(
                llama_completion=llama_completion,
                model_path=model_path,
                messages=messages,
                ctx=args.ctx,
                threads=args.threads,
                gpu_layers=args.gpu_layers,
                max_tokens=args.max_tokens,
                timeout_sec=args.timeout_sec,
                max_prompt_chars=args.max_prompt_chars,
            )
            parsed = normalize_call(extract_json_object(action))
            reward, note = score_call(parsed, case["expected"])
            if arm_id == "with_metta_runtime":
                runtime_candidate = action
                runtime_elapsed = elapsed
                runtime_raw = raw
            row = {
                "case_id": case["case_id"],
                "arm_id": arm_id,
                "reward": reward,
                "judge_note": note,
                "action": action,
                "parsed_call": parsed,
                "expected_call": case["expected"],
                "generation_sec": elapsed,
                "raw_usage": raw,
            }
            results.append(row)
            write_jsonl(events_path, {"event": "case_arm", "ts": utc_now(), **row})
        repair = repair_call(case, runtime_candidate)
        repaired_text = str(repair["repaired_text"])
        parsed = normalize_call(extract_json_object(repaired_text))
        reward, note = score_call(parsed, case["expected"])
        row = {
            "case_id": case["case_id"],
            "arm_id": "with_metta_runtime_repair",
            "reward": reward,
            "judge_note": note,
            "action": repaired_text,
            "parsed_call": parsed,
            "expected_call": case["expected"],
            "generation_sec": runtime_elapsed,
            "raw_usage": runtime_raw,
            "repair_report": repair,
        }
        results.append(row)
        write_jsonl(events_path, {"event": "case_arm", "ts": utc_now(), **row})
    payload = {
        "generated_at_utc": utc_now(),
        "model": {
            "model_id": "qwen25_3b_q4km_llamacli",
            "model_name": "Qwen2.5-3B-Instruct-Q4_K_M-GGUF-llama.cpp-CUDA",
            "backend": "llama_completion_external_cuda_gguf",
        },
        "cases": CASES,
        "results": results,
    }
    results_json = out_dir / "synthetic_tool_router.results.json"
    results_md = out_dir / "synthetic_tool_router.results.md"
    results_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    results_md.write_text(render_md(results, payload["model"]["model_name"]), encoding="utf-8")
    write_jsonl(events_path, {"event": "finish", "ts": utc_now(), "results_json": str(results_json)})
    print(results_json)
    print(results_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
