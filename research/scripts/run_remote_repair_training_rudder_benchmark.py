"""Benchmark remote 9B/27B endpoints as Hermes repair-training rudders.

This mirrors `run_3b_repair_training_rudder_benchmark.py` but calls
OpenAI-compatible chat-completions endpoints, e.g. snacksack ports 8082 (9B) and
8081 (27B).  It intentionally reuses the same Pure-TRM split, prompt builders,
arms, and summary shape so results can fill the Skills paper scale table.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes Skills")
LOCAL_RUNNER = ROOT / "research" / "scripts" / "run_3b_repair_training_rudder_benchmark.py"
DEFAULT_SPLIT_DIR = ROOT / "research" / "generated" / "near_miss_repair_curriculum" / "splits"
DEFAULT_OUT_ROOT = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
)
DEFAULT_HOST = "snacksack-ms-7d32.tail3156cd.ts.net"
MODEL_CONFIGS = {
    "9b": {
        "base_url": f"http://{DEFAULT_HOST}:8082/v1",
        "model_name": "Qwen_Qwen3.5-9B-Q4_K_M.gguf",
    },
    "27b": {
        "base_url": f"http://{DEFAULT_HOST}:8081/v1",
        "model_name": "Qwen3.5-27B.Q4_K_M.gguf",
    },
}


def load_local_runner():
    spec = importlib.util.spec_from_file_location("local_repair_rudder", LOCAL_RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {LOCAL_RUNNER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LOCAL = load_local_runner()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def chat_completion(
    *,
    base_url: str,
    model_name: str,
    messages: list[dict[str, str]],
    max_tokens: int,
    temperature: float,
    top_p: float,
    request_timeout: int,
) -> tuple[str, dict[str, Any], float]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer EMPTY"},
        method="POST",
    )
    start = time.time()
    try:
        with urllib.request.urlopen(request, timeout=request_timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            elapsed = time.time() - start
            data = json.loads(raw)
    except urllib.error.HTTPError as exc:
        stderr = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise RuntimeError(f"HTTP {exc.code} from {url}: {stderr[-2000:]}") from exc
    except Exception as exc:
        raise RuntimeError(f"request failed for {url}: {exc}") from exc
    choices = data.get("choices") or []
    text = ""
    if choices:
        message = choices[0].get("message") or {}
        text = str(message.get("content") or choices[0].get("text") or "")
    diagnostics = {
        "mode": "openai_compatible_chat",
        "base_url": base_url,
        "model_name": model_name,
        "elapsed_sec": round(elapsed, 4),
        "usage": data.get("usage", {}),
    }
    return text, diagnostics, elapsed


def probe_endpoint(base_url: str, request_timeout: int) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/models"
    start = time.time()
    try:
        with urllib.request.urlopen(url, timeout=request_timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
            data = json.loads(raw)
        return {
            "ok": True,
            "url": url,
            "elapsed_sec": round(time.time() - start, 4),
            "model_count": len(data.get("data", [])) if isinstance(data, dict) else None,
            "raw_head": raw[:500],
        }
    except Exception as exc:
        return {
            "ok": False,
            "url": url,
            "elapsed_sec": round(time.time() - start, 4),
            "error": str(exc),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remote 9B/27B repair-training rudder benchmark.")
    parser.add_argument("--model-scale", action="append", choices=sorted(MODEL_CONFIGS), default=None)
    parser.add_argument("--base-url-9b", default=MODEL_CONFIGS["9b"]["base_url"])
    parser.add_argument("--base-url-27b", default=MODEL_CONFIGS["27b"]["base_url"])
    parser.add_argument("--model-name-9b", default=MODEL_CONFIGS["9b"]["model_name"])
    parser.add_argument("--model-name-27b", default=MODEL_CONFIGS["27b"]["model_name"])
    parser.add_argument("--split-dir", default=str(DEFAULT_SPLIT_DIR))
    parser.add_argument("--out-root", default=str(DEFAULT_OUT_ROOT))
    parser.add_argument("--run-id", default="")
    parser.add_argument("--eval-split", action="append", default=["val_seen", "holdout_seen", "holdout_unseen_family"])
    parser.add_argument("--max-cases", type=int, default=12, help="Total eval rows to run per model. Use 0 for all.")
    parser.add_argument("--shots", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--request-timeout", type=int, default=180)
    parser.add_argument("--endpoint-probe-timeout", type=int, default=8)
    parser.add_argument("--max-runtime-minutes", type=float, default=0.0)
    parser.add_argument("--arm", action="append", default=None)
    parser.add_argument("--probe-only", action="store_true")
    parser.add_argument("--skip-endpoint-check", action="store_true")
    return parser.parse_args()


def endpoint_config(args: argparse.Namespace, scale: str) -> dict[str, str]:
    if scale == "9b":
        return {"base_url": args.base_url_9b, "model_name": args.model_name_9b}
    return {"base_url": args.base_url_27b, "model_name": args.model_name_27b}


def run_one_model(args: argparse.Namespace, scale: str) -> Path:
    cfg = endpoint_config(args, scale)
    split_dir = Path(args.split_dir).resolve()
    run_stamp = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out_root).resolve() / f"remote_{scale}_repair_training_rudder_{run_stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    train_rows = LOCAL.load_jsonl(split_dir / "train.pure_trm.jsonl")
    eval_rows = LOCAL.select_eval_rows(split_dir, args.eval_split, args.max_cases)
    allowed_actions = sorted({str(row.get("action") or "") for row in train_rows if str(row.get("action") or "")})
    arms = args.arm or ["raw_3b_rudder", "repair_training_rudder", "metta_action_space_rudder", "metta_static_gate_rudder"]
    results: list[dict[str, Any]] = []
    start = time.time()

    for row in eval_rows:
        if args.max_runtime_minutes and (time.time() - start) > args.max_runtime_minutes * 60:
            break
        target_repair = str(row.get("action") or "")
        target_action = str(row.get("target_action") or "")
        for arm in arms:
            examples = LOCAL.retrieve_examples(train_rows, row, args.shots) if arm in {
                "repair_training_rudder",
                "metta_action_space_training_rudder",
            } else []
            if arm == "metta_validator_gate":
                raw = "metta_validator_gate"
                diagnostics = {"mode": "deterministic"}
                elapsed = 0.0
                parsed = {
                    "repair_action": LOCAL.metta_repair_action(row),
                    "target_action": LOCAL.metta_validator_target_action(row),
                }
            elif arm == "metta_static_gate_rudder":
                fixed_repair = LOCAL.metta_repair_action(row)
                static_target = LOCAL.metta_static_target_action(row)
                if static_target is not None:
                    raw = "metta_static_gate"
                    diagnostics = {"mode": "deterministic_static_gate"}
                    elapsed = 0.0
                    parsed = {"repair_action": fixed_repair, "target_action": static_target}
                else:
                    raw, diagnostics, elapsed = chat_completion(
                        base_url=cfg["base_url"],
                        model_name=cfg["model_name"],
                        messages=LOCAL.make_fixed_repair_prompt(arm, row, examples, fixed_repair),
                        max_tokens=args.max_tokens,
                        temperature=args.temperature,
                        top_p=args.top_p,
                        request_timeout=args.request_timeout,
                    )
                    model_parsed = LOCAL.parse_model_json(raw)
                    parsed = {"repair_action": fixed_repair, "target_action": model_parsed["target_action"]}
            elif arm in {"metta_action_space_rudder", "metta_action_space_training_rudder"}:
                fixed_repair = LOCAL.metta_repair_action(row)
                raw, diagnostics, elapsed = chat_completion(
                    base_url=cfg["base_url"],
                    model_name=cfg["model_name"],
                    messages=LOCAL.make_fixed_repair_prompt(arm, row, examples, fixed_repair),
                    max_tokens=args.max_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    request_timeout=args.request_timeout,
                )
                model_parsed = LOCAL.parse_model_json(raw)
                parsed = {"repair_action": fixed_repair, "target_action": model_parsed["target_action"]}
            else:
                raw, diagnostics, elapsed = chat_completion(
                    base_url=cfg["base_url"],
                    model_name=cfg["model_name"],
                    messages=LOCAL.make_prompt(arm, row, examples, allowed_actions),
                    max_tokens=args.max_tokens,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    request_timeout=args.request_timeout,
                )
                parsed = LOCAL.parse_model_json(raw)

            repair_correct = parsed["repair_action"] == target_repair
            action_correct = parsed["target_action"] == target_action
            results.append(
                {
                    "generated_at_utc": utc_now(),
                    "model_scale": scale,
                    "model_name": cfg["model_name"],
                    "base_url": cfg["base_url"],
                    "arm": arm,
                    "eval_split": row.get("eval_split"),
                    "case_id": (row.get("state") or {}).get("case_id"),
                    "trm_role": (row.get("state") or {}).get("trm_role"),
                    "failure_label": (row.get("state") or {}).get("failure_label"),
                    "bucket": row.get("bucket"),
                    "target_repair_action": target_repair,
                    "target_action": target_action,
                    "predicted_repair_action": parsed["repair_action"],
                    "predicted_target_action": parsed["target_action"],
                    "repair_action_correct": int(repair_correct),
                    "target_action_correct": int(action_correct),
                    "joint_correct": int(repair_correct and action_correct),
                    "json_parse_ok": int(bool(parsed["repair_action"] or parsed["target_action"])),
                    "raw_output": raw,
                    "retrieved_case_ids": [(example.get("state") or {}).get("case_id") for example in examples],
                    "diagnostics": diagnostics,
                    "elapsed_sec": round(elapsed, 4),
                }
            )
            print(
                f"{scale} {arm} {row.get('eval_split')} {(row.get('state') or {}).get('case_id')} "
                f"target={target_repair}/{target_action} pred={parsed['repair_action']}/{parsed['target_action']}"
            )

    payload = {
        "generated_at_utc": utc_now(),
        "schema": "remote_repair_training_rudder_benchmark_v1",
        "model_scale": scale,
        "model_name": cfg["model_name"],
        "base_url": cfg["base_url"],
        "split_dir": str(split_dir),
        "eval_splits": args.eval_split,
        "max_cases": args.max_cases,
        "shots": args.shots,
        "arms": arms,
        "summary_by_arm": LOCAL.summarize(results),
        "request_profile": {
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "request_timeout": args.request_timeout,
        },
    }
    LOCAL.write_jsonl(out_dir / "remote_repair_training_rudder.rows.jsonl", results)
    LOCAL.write_json(out_dir / "remote_repair_training_rudder.results.json", payload)
    (out_dir / "remote_repair_training_rudder.results.md").write_text(LOCAL.render_markdown(payload), encoding="utf-8")
    return out_dir / "remote_repair_training_rudder.results.json"


def main() -> int:
    args = parse_args()
    scales = args.model_scale or ["9b", "27b"]
    probes = {scale: probe_endpoint(endpoint_config(args, scale)["base_url"], args.endpoint_probe_timeout) for scale in scales}
    if args.probe_only:
        print(json.dumps({"schema": "remote_repair_rudder_endpoint_probe_v1", "probes": probes}, indent=2))
        return 0 if all(item["ok"] for item in probes.values()) else 1
    if not args.skip_endpoint_check:
        failed = {scale: probe for scale, probe in probes.items() if not probe["ok"]}
        if failed:
            print(json.dumps({"schema": "remote_repair_rudder_endpoint_probe_v1", "probes": probes}, indent=2))
            return 2
    outputs = {}
    for scale in scales:
        outputs[scale] = str(run_one_model(args, scale))
    print(json.dumps({"schema": "remote_repair_rudder_outputs_v1", "outputs": outputs}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
