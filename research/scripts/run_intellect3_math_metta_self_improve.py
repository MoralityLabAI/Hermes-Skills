"""Run a bounded Intellect-3-Math MeTTa self-improvement smoke.

This experiment asks a live 27B model to draft a MeTTa-style skill revision
from prior training receipts, then evaluates the revised skill prompt on held
out rows.  The held-out prompts never include target answers; answers are used
only for scoring after generation.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = Path(r"C:\projects\Tesseract\Tesseract\data\normalized_trajectories\intellect_3_math.jsonl")
DEFAULT_RECEIPTS = Path(r"C:\projects\trm_observability_harness\data\qwen27b_intellect3_math_hybrid_200\predictions.jsonl")
DEFAULT_OUT = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "intellect3_math_metta_self_improve_27b_20260502"
)
DEFAULT_BASE_URL = "http://snacksack-ms-7d32.tail3156cd.ts.net:8081/v1"
MODEL_NAME = "Qwen3.5-27B.Q4_K_M.gguf"


BASELINE_TASK = (
    "Solve the math problem. Return only the final integer answer. "
    "Do not include prose, equations, commas, units, or markdown."
)

CURRENT_SKILL_TASK = (
    "Hermes/Intellect-3-Math-v1. Parse the givens, solve with a short candidate path, "
    "verify arithmetic consistency, and commit only the final integer answer. "
    "No prose, no tags, no markdown."
)

FALLBACK_METTA_TASK = (
    "Hermes/Intellect-3-Math-Metta-Auditor-v2. Use this internal MeTTa control plane: "
    "(1) classify the problem family before calculating; (2) track the requested final quantity, "
    "not an intermediate; (3) reject retrieved or memorized-looking answers unless dimensional, "
    "parity, sign, and magnitude checks fit; (4) for combinatorics/counting, derive the invariant "
    "or recurrence before emitting; (5) for geometry, solve symbolically enough to verify the final "
    "integer expression. Return only the final integer answer."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Intellect-3-Math MeTTa self-improvement smoke.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), type=Path)
    parser.add_argument("--receipts", default=str(DEFAULT_RECEIPTS), type=Path)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), type=Path)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--holdout-rows", default=20, type=int)
    parser.add_argument("--train-examples", default=18, type=int)
    parser.add_argument("--request-timeout", default=240, type=int)
    parser.add_argument("--max-tokens", default=32, type=int)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def parse_int(value: Any) -> int | None:
    match = re.search(r"[-+]?\d+", str(value or ""))
    if not match:
        return None
    return int(match.group(0))


def normalize_int_text(value: Any) -> str:
    parsed = parse_int(value)
    return "" if parsed is None else str(parsed)


def integer_grammar(max_digits: int = 12) -> str:
    optional_digits = "".join(" digit?" for _ in range(max(0, max_digits - 1)))
    return (
        "root ::= ws sign? number ws\n"
        "sign ::= \"-\"\n"
        f"number ::= digit{optional_digits}\n"
        "digit ::= [0-9]\n"
        "ws ::= [ \\t\\n\\r]*\n"
    )


def render_chatml_user_prompt(content: str) -> str:
    return (
        "<|im_start|>user\n"
        f"{content}<|im_end|>\n"
        "<|im_start|>assistant\n"
        "<think>\n\n</think>\n\n"
    )


def strip_no_think_prefix(text: str) -> str:
    text = str(text or "")
    if text.startswith("<think>\n\n</think>"):
        return text.split("</think>", 1)[1].lstrip()
    return text


def call_completion(
    base_url: str,
    prompt: str,
    *,
    n_predict: int,
    timeout: int,
    grammar: str | None = None,
) -> dict[str, Any]:
    rendered_prompt = render_chatml_user_prompt(prompt)
    raw_payload: dict[str, Any] = {
        "prompt": rendered_prompt,
        "n_predict": n_predict,
        "temperature": 0.0,
        "top_p": 1.0,
        "stop": ["<|im_end|>"],
    }
    if grammar:
        raw_payload["grammar"] = grammar
    url = base_url.rstrip("/")
    started = time.perf_counter()
    raw_url = url[:-3] if url.endswith("/v1") else url
    try:
        req = urllib.request.Request(
            f"{raw_url}/completion",
            data=json.dumps(raw_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))
        raw["content"] = strip_no_think_prefix(str(raw.get("content") or ""))
        raw["latency_seconds"] = round(time.perf_counter() - started, 4)
        return raw
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        if exc.code != 404:
            raise RuntimeError(f"HTTP {exc.code} from raw completion endpoint: {body[-1000:]}") from exc

    v1_url = url if url.endswith("/v1") else f"{url}/v1"
    v1_payload: dict[str, Any] = {
        "model": MODEL_NAME,
        "prompt": rendered_prompt,
        "max_tokens": n_predict,
        "temperature": 0.0,
        "top_p": 1.0,
        "stop": ["<|im_end|>"],
    }
    if grammar:
        v1_payload["grammar"] = grammar
    req = urllib.request.Request(
        f"{v1_url}/completions",
        data=json.dumps(v1_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        raise RuntimeError(f"HTTP {exc.code} from v1 completions endpoint: {body[-1000:]}") from exc
    choice = (data.get("choices") or [{}])[0]
    usage = data.get("usage") or {}
    return {
        "content": strip_no_think_prefix(str(choice.get("text") or "")),
        "latency_seconds": round(time.perf_counter() - started, 4),
        "tokens_evaluated": usage.get("prompt_tokens"),
        "tokens_predicted": usage.get("completion_tokens"),
        "model": data.get("model") or MODEL_NAME,
        "raw_openai_response": data,
    }


def load_math_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in load_jsonl(path):
        expected = normalize_int_text(raw.get("action"))
        if not expected:
            continue
        rows.append(
            {
                "row_id": str(raw.get("trajectory_id")),
                "observation": str(raw.get("state_prompt") or ""),
                "expected": expected,
            }
        )
    return rows


def receipt_rows(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    if not path.exists():
        return grouped
    for row in load_jsonl(path):
        grouped.setdefault(str(row.get("row_id")), {})[str(row.get("arm"))] = row
    return grouped


def receipt_action(row: dict[str, Any] | None, key: str = "final") -> str:
    if not row:
        return ""
    block = row.get(key) or {}
    return normalize_int_text(block.get("action") or block.get("raw_action") or block.get("raw_text"))


def trm_action(row: dict[str, Any] | None, key: str) -> str:
    if not row:
        return ""
    return normalize_int_text((row.get("trm") or {}).get(key))


def build_training_examples(
    source_rows: list[dict[str, Any]],
    receipts: dict[str, dict[str, dict[str, Any]]],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for idx, row in enumerate(source_rows):
        if idx % 2 != 0:
            continue
        group = receipts.get(row["row_id"], {})
        math_trm = group.get("math_skill_trm")
        vanilla = group.get("vanilla")
        expected = row["expected"]
        item = {
            "row_id": row["row_id"],
            "expected": expected,
            "vanilla": receipt_action(vanilla),
            "math_skill_final": receipt_action(math_trm),
            "math_skill_candidate": trm_action(math_trm, "math_skill_action"),
            "trm_candidate": trm_action(math_trm, "trm_skill_action"),
            "retrieved": trm_action(math_trm, "retrieved_action"),
            "route_source": (math_trm.get("trm") or {}).get("route_source") if math_trm else None,
            "prompt_excerpt": row["observation"][:420].replace("\n", " "),
        }
        if any(item[key] and item[key] == expected for key in ("vanilla", "math_skill_final", "math_skill_candidate", "trm_candidate")):
            examples.append(item)
        elif len(examples) < limit // 2:
            examples.append(item)
        if len(examples) >= limit:
            break
    return examples


def build_patch_prompt(examples: list[dict[str, Any]]) -> str:
    compact_examples = json.dumps(examples, indent=2)[:4200]
    return f"""You are improving a Hermes skill for Intellect-3-Math.

We have a MeTTa/TRM skill architecture.  The current finding is that raw math solving is scale sensitive, but routing and candidate auditing can still improve a 27B model.  Use the labeled TRAIN examples below to design a revised skill contract.  The revised contract will be tested on held-out prompts without target answers.

Constraints:
- Do not memorize row IDs or exact answers.
- Prefer general math control logic, verifier checks, and candidate rejection rules.
- The live evaluator can only ask the model once per held-out problem and requires an integer-only answer.
- Return strict JSON with these fields:
  skill_name: string
  task_prefix: string, 1200 chars max, written as instructions for the live model
  metta_rules: list of strings
  expected_failure_modes: list of strings
  route_policy: string
  paper_read: string

TRAIN examples:
{compact_examples}
"""


def extract_json_object(text: str) -> dict[str, Any] | None:
    cleaned = str(text or "").strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        cleaned = cleaned[start : end + 1]
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def extract_json_string_field(text: str, field: str) -> str:
    match = re.search(rf'"{re.escape(field)}"\s*:\s*"((?:\\.|[^"])*)"', text, flags=re.DOTALL)
    if not match:
        return ""
    try:
        return json.loads(f'"{match.group(1)}"')
    except json.JSONDecodeError:
        return match.group(1).replace(r"\n", "\n").replace(r"\"", '"')


def extract_json_string_list_field(text: str, field: str) -> list[str]:
    match = re.search(rf'"{re.escape(field)}"\s*:\s*\[(.*?)\]', text, flags=re.DOTALL)
    if not match:
        return []
    try:
        value = json.loads(f"[{match.group(1)}]")
    except json.JSONDecodeError:
        return []
    return [str(item) for item in value if isinstance(item, str)]


def draft_skill_patch(args: argparse.Namespace, examples: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    prompt = build_patch_prompt(examples)
    raw = call_completion(args.base_url, prompt, n_predict=700, timeout=args.request_timeout, grammar=None)
    content = str(raw.get("content") or "")
    patch = extract_json_object(content) or {}
    if not patch:
        patch = {
            "skill_name": extract_json_string_field(content, "skill_name"),
            "task_prefix": extract_json_string_field(content, "task_prefix"),
            "metta_rules": extract_json_string_list_field(content, "metta_rules"),
            "expected_failure_modes": extract_json_string_list_field(content, "expected_failure_modes"),
            "route_policy": extract_json_string_field(content, "route_policy"),
            "paper_read": extract_json_string_field(content, "paper_read")
            or "Recovered usable fields from a truncated 27B JSON patch.",
        }
    task_prefix = str(patch.get("task_prefix") or "").strip()
    if len(task_prefix) < 80:
        patch["task_prefix"] = FALLBACK_METTA_TASK
        patch.setdefault("skill_name", "Hermes/Intellect-3-Math-Metta-Auditor-v2-fallback")
        patch.setdefault("paper_read", "Fallback used because the live model did not emit parseable JSON.")
    return patch, content


def heldout_rows(source_rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    rows = [row for idx, row in enumerate(source_rows) if idx % 2 == 1]
    return rows[:limit]


def run_arm(
    args: argparse.Namespace,
    row: dict[str, Any],
    *,
    arm: str,
    task_prefix: str,
) -> dict[str, Any]:
    prompt = f"{task_prefix}\n\n{row['observation']}\n\nFinal answer:"
    raw = call_completion(
        args.base_url,
        prompt,
        n_predict=args.max_tokens,
        timeout=args.request_timeout,
        grammar=integer_grammar(12),
    )
    action = normalize_int_text(raw.get("content"))
    return {
        "row_id": row["row_id"],
        "arm": arm,
        "expected": row["expected"],
        "action": action,
        "exact": action == row["expected"],
        "raw_text": str(raw.get("content") or ""),
        "latency_seconds": raw.get("latency_seconds"),
        "tokens_evaluated": raw.get("tokens_evaluated"),
        "tokens_predicted": raw.get("tokens_predicted"),
        "model_name": raw.get("model") or MODEL_NAME,
    }


def error_row(row: dict[str, Any], *, arm: str, error: str) -> dict[str, Any]:
    return {
        "row_id": row["row_id"],
        "arm": arm,
        "expected": row["expected"],
        "action": "",
        "exact": False,
        "raw_text": "",
        "error": error[-1000:],
        "latency_seconds": 0.0,
        "tokens_evaluated": None,
        "tokens_predicted": None,
        "model_name": MODEL_NAME,
    }


def summarize(evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    arms = sorted({row["arm"] for row in evaluated})
    by_arm: dict[str, Any] = {}
    for arm in arms:
        rows = [row for row in evaluated if row["arm"] == arm]
        by_arm[arm] = {
            "rows": len(rows),
            "exact": sum(1 for row in rows if row["exact"]),
            "exact_rate": round(sum(1 for row in rows if row["exact"]) / max(1, len(rows)), 6),
            "avg_latency_seconds": round(sum(float(row.get("latency_seconds") or 0.0) for row in rows) / max(1, len(rows)), 4),
            "common_actions": dict(Counter(str(row.get("action")) for row in rows).most_common(8)),
        }
    by_row: dict[str, dict[str, Any]] = {}
    for row in evaluated:
        by_row.setdefault(row["row_id"], {})[row["arm"]] = row
    transitions = Counter()
    for group in by_row.values():
        current = group.get("current_skill")
        metta = group.get("metta_self_improved")
        if not current or not metta:
            continue
        if not current["exact"] and metta["exact"]:
            transitions["fixed_by_metta"] += 1
        elif current["exact"] and not metta["exact"]:
            transitions["regressed_by_metta"] += 1
        elif current["action"] != metta["action"]:
            transitions["changed_wrong_answer"] += 1
        else:
            transitions["same_outcome"] += 1
    current = by_arm.get("current_skill", {})
    metta = by_arm.get("metta_self_improved", {})
    fixes = transitions.get("fixed_by_metta", 0)
    regressions = transitions.get("regressed_by_metta", 0)
    if metta.get("exact", 0) > current.get("exact", 0) and fixes >= regressions:
        decision = "adopt_patch_for_larger_rerun"
    else:
        decision = "reject_patch_keep_current_skill"
    return {
        "arms": by_arm,
        "transitions_vs_current_skill": dict(transitions),
        "metta_adoption_gate": {
            "decision": decision,
            "current_exact": current.get("exact", 0),
            "metta_exact": metta.get("exact", 0),
            "fixed_by_metta": fixes,
            "regressed_by_metta": regressions,
            "rule": "Adopt only when held-out exact improves and fixes are at least regressions.",
        },
    }


def render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Intellect-3-Math MeTTa Self-Improvement Smoke",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        f"Model endpoint: `{payload['base_url']}`",
        f"Held-out rows: `{payload['heldout_rows']}`",
        "",
        "## Live Result",
        "",
        "| Arm | Exact | Exact Rate | Avg Latency | Common Actions |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for arm, metrics in summary["arms"].items():
        actions = ", ".join(f"{key}:{value}" for key, value in metrics["common_actions"].items())
        lines.append(
            f"| `{arm}` | {metrics['exact']}/{metrics['rows']} | {metrics['exact_rate']:.4f} | "
            f"{metrics['avg_latency_seconds']:.2f}s | {actions or '-'} |"
        )
    lines.extend(
        [
            "",
            "## MeTTa Patch",
            "",
            f"Skill: `{payload['patch'].get('skill_name', 'unknown')}`",
            "",
            str(payload["patch"].get("paper_read") or ""),
            "",
            "Rules:",
        ]
    )
    for rule in payload["patch"].get("metta_rules") or []:
        lines.append(f"- {rule}")
    lines.extend(
        [
            "",
            "## Transition Read",
            "",
            json.dumps(summary["transitions_vs_current_skill"], indent=2),
            "",
            "## Commit Gate",
            "",
            json.dumps(summary["metta_adoption_gate"], indent=2),
            "",
            "This is a bounded live smoke.  It tests whether a model-drafted skill contract changes held-out behavior; it is not a full benchmark column until rerun over the frozen 200-row slice.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_metta(patch: dict[str, Any], summary: dict[str, Any]) -> str:
    lines = [
        ";; 27B-drafted MeTTa self-improvement contract for Intellect-3-Math.",
        "(= env_id intellect3_math_metta_self_improve_27b)",
        f"(= skill_name {json.dumps(str(patch.get('skill_name') or 'Hermes/Intellect-3-Math-Metta-Auditor-v2'))})",
    ]
    for idx, rule in enumerate(patch.get("metta_rules") or [], 1):
        lines.append(f"(= (metta_rule {idx}) {json.dumps(str(rule))})")
    for arm, metrics in summary["arms"].items():
        lines.append(f"(= (heldout_exact {arm}) {metrics['exact']}/{metrics['rows']})")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    source_rows = load_math_rows(args.source)
    receipts = receipt_rows(args.receipts)
    examples = build_training_examples(source_rows, receipts, limit=args.train_examples)
    patch, raw_patch = draft_skill_patch(args, examples)
    metta_task = str(patch.get("task_prefix") or FALLBACK_METTA_TASK)[:1200]
    rows = heldout_rows(source_rows, args.holdout_rows)

    evaluated: list[dict[str, Any]] = []
    rows_path = args.out_dir / "intellect3_math_metta_self_improve.rows.jsonl"
    if rows_path.exists():
        rows_path.unlink()
    for row in rows:
        for arm, task_prefix in (
            ("baseline", BASELINE_TASK),
            ("current_skill", CURRENT_SKILL_TASK),
            ("metta_self_improved", metta_task),
        ):
            try:
                result = run_arm(args, row, arm=arm, task_prefix=task_prefix)
            except Exception as exc:  # Preserve partial-run data instead of losing the smoke.
                result = error_row(row, arm=arm, error=repr(exc))
            evaluated.append(result)
            with rows_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(result, ensure_ascii=True) + "\n")

    summary = summarize(evaluated)
    payload = {
        "generated_at_utc": utc_now(),
        "source": str(args.source),
        "receipts": str(args.receipts),
        "base_url": args.base_url,
        "heldout_rows": len(rows),
        "train_examples": len(examples),
        "patch": patch,
        "summary": summary,
    }
    (args.out_dir / "metta_self_improvement_patch.raw.txt").write_text(raw_patch, encoding="utf-8", newline="\n")
    (args.out_dir / "metta_self_improvement_patch.json").write_text(json.dumps(patch, indent=2), encoding="utf-8", newline="\n")
    (args.out_dir / "intellect3_math_metta_self_improve.results.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8", newline="\n"
    )
    (args.out_dir / "intellect3_math_metta_self_improve.results.md").write_text(
        render_md(payload), encoding="utf-8", newline="\n"
    )
    (args.out_dir / "intellect3_math_metta_self_improve_contract.metta").write_text(
        render_metta(patch, summary), encoding="utf-8", newline="\n"
    )
    print(args.out_dir / "intellect3_math_metta_self_improve.results.md")
    print(json.dumps(summary["arms"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
