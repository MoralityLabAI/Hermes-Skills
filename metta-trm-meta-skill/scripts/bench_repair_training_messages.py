from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(?P<body>\{.*?\})\s*```", re.DOTALL)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def extract_json_object(text: str) -> tuple[dict[str, Any] | None, str]:
    stripped = text.strip()
    candidates = [stripped]
    for match in JSON_BLOCK_RE.finditer(stripped):
        candidates.append(match.group("body").strip())
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first >= 0 and last > first:
        candidates.append(stripped[first : last + 1])
    for candidate in candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload, ""
    return None, "json_parse_failed"


def expected_action(row: dict[str, Any]) -> dict[str, Any]:
    messages = row.get("messages") or []
    if not messages:
        return {}
    content = str(messages[-1].get("content") or "")
    payload, _error = extract_json_object(content)
    return payload or {}


def prompt_messages(row: dict[str, Any]) -> list[dict[str, str]]:
    messages = row.get("messages") or []
    if len(messages) < 2:
        return []
    return [
        {"role": str(item.get("role") or ""), "content": str(item.get("content") or "")}
        for item in messages[:-1]
    ]


def primary_keys_for_role(role: str) -> list[str]:
    if role == "metta_syntax_repair":
        return ["repair", "repaired_atom", "accept_repair"]
    if role == "semantic_contract_verifier":
        return ["verdict"]
    if role == "commit_veto":
        return ["decision", "reason"]
    return []


def score_prediction(expected: dict[str, Any], predicted: dict[str, Any] | None, role: str) -> dict[str, Any]:
    predicted = predicted or {}
    expected_keys = sorted(expected)
    key_hits = {key: predicted.get(key) == expected.get(key) for key in expected_keys}
    primary_keys = primary_keys_for_role(role)
    primary_hits = {key: predicted.get(key) == expected.get(key) for key in primary_keys if key in expected}
    return {
        "json_valid": bool(predicted),
        "exact_action": predicted == expected,
        "key_accuracy": round(sum(1 for hit in key_hits.values() if hit) / len(key_hits), 4) if key_hits else 0.0,
        "primary_accuracy": round(sum(1 for hit in primary_hits.values() if hit) / len(primary_hits), 4) if primary_hits else 0.0,
        "key_hits": key_hits,
        "primary_hits": primary_hits,
    }


def post_chat(endpoint: str, model: str, messages: list[dict[str, str]], max_tokens: int, temperature: float, timeout: float) -> dict[str, Any]:
    url = endpoint.rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
    decoded = json.loads(raw)
    decoded["_elapsed_seconds"] = time.time() - started
    return decoded


def extract_content(response: dict[str, Any]) -> str:
    choices = response.get("choices") or []
    if not choices:
        return ""
    first = choices[0]
    message = first.get("message") or {}
    if isinstance(message, dict) and message.get("content"):
        return str(message["content"])
    if first.get("text"):
        return str(first["text"])
    return ""


def summarize(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    role_counts: dict[str, int] = {}
    role_exact: dict[str, int] = {}
    for row in predictions:
        role = str(row.get("role") or "")
        role_counts[role] = role_counts.get(role, 0) + 1
        if row.get("score", {}).get("exact_action"):
            role_exact[role] = role_exact.get(role, 0) + 1
    count = len(predictions)
    return {
        "generated_at_utc": utc_now(),
        "count": count,
        "json_valid_rate": round(sum(1 for row in predictions if row.get("score", {}).get("json_valid")) / count, 4) if count else 0.0,
        "exact_action_rate": round(sum(1 for row in predictions if row.get("score", {}).get("exact_action")) / count, 4) if count else 0.0,
        "mean_key_accuracy": round(sum(float(row.get("score", {}).get("key_accuracy", 0.0)) for row in predictions) / count, 4) if count else 0.0,
        "mean_primary_accuracy": round(sum(float(row.get("score", {}).get("primary_accuracy", 0.0)) for row in predictions) / count, 4) if count else 0.0,
        "role_counts": role_counts,
        "role_exact_rates": {
            role: round(role_exact.get(role, 0) / role_counts[role], 4)
            for role in sorted(role_counts)
        },
    }


def evaluate(args: argparse.Namespace) -> int:
    rows = list(read_jsonl(Path(args.messages)))
    if args.max_records:
        rows = rows[: args.max_records]
    predictions: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        meta = row.get("meta") or {}
        role = str(meta.get("role") or "")
        expected = expected_action(row)
        messages = prompt_messages(row)
        raw_text = ""
        error = ""
        response_meta: dict[str, Any] = {}
        predicted: dict[str, Any] | None = None
        if not messages:
            error = "missing_prompt_messages"
        else:
            try:
                response_meta = post_chat(args.endpoint, args.model, messages, args.max_tokens, args.temperature, args.timeout)
                raw_text = extract_content(response_meta)
                predicted, parse_error = extract_json_object(raw_text)
                error = parse_error
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                error = f"{type(exc).__name__}: {exc}"
        predictions.append(
            {
                "index": index,
                "role": role,
                "task_id": meta.get("task_id", ""),
                "package_id": meta.get("package_id", ""),
                "expected": expected,
                "predicted": predicted,
                "raw_text": raw_text,
                "error": error,
                "elapsed_seconds": response_meta.get("_elapsed_seconds", 0.0),
                "score": score_prediction(expected, predicted, role),
            }
        )
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = out_dir / "predictions.jsonl"
    write_jsonl(predictions_path, predictions)
    summary = summarize(predictions)
    summary.update(
        {
            "messages": str(Path(args.messages)),
            "predictions": str(predictions_path),
            "endpoint": args.endpoint,
            "model": args.model,
            "temperature": args.temperature,
            "max_tokens": args.max_tokens,
        }
    )
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_dir)
    print(json.dumps({key: summary[key] for key in ("json_valid_rate", "exact_action_rate", "mean_key_accuracy", "mean_primary_accuracy")}, indent=2))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Baseline a small model on MeTTa repair-training messages.")
    parser.add_argument("--messages", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8084")
    parser.add_argument("--model", default="Qwen3.5-4B.Q4_K_M.gguf")
    parser.add_argument("--max-records", type=int, default=0)
    parser.add_argument("--max-tokens", type=int, default=180)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout", type=float, default=120.0)
    return parser.parse_args()


def main() -> int:
    return evaluate(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())

