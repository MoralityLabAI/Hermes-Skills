from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ATOM_RE = re.compile(r"^\((?P<body>.*)\)$")
TOKEN_RE = re.compile(r'"(?:[^"\\]|\\.)*"|[^\s()]+')


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def quote(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def atom(head: str, *args: Any) -> str:
    return "(" + " ".join([head, *[quote(arg) for arg in args]]) + ")"


def strip_quotes(token: str) -> str:
    token = token.strip()
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return str(json.loads(token))
    return token


def parse_atom(value: str) -> tuple[str, list[str]]:
    raw = value.strip()
    if not raw.startswith("("):
        raw = "(" + raw
    if not raw.endswith(")"):
        raw = raw + ")"
    match = ATOM_RE.match(raw)
    if not match:
        return "", []
    tokens = [strip_quotes(token) for token in TOKEN_RE.findall(match.group("body"))]
    if not tokens:
        return "", []
    return str(tokens[0]), [str(token) for token in tokens[1:]]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def json_from_message_content(content: str) -> dict[str, Any]:
    payload = json.loads(content)
    if not isinstance(payload, dict):
        raise ValueError("message content must decode to an object")
    return payload


def prompt_payload(row: dict[str, Any]) -> dict[str, Any]:
    messages = row.get("messages") or []
    if len(messages) < 2:
        return {}
    return json_from_message_content(str(messages[1].get("content") or "{}"))


def expected_action(row: dict[str, Any]) -> dict[str, Any]:
    messages = row.get("messages") or []
    if not messages:
        return {}
    return json_from_message_content(str(messages[-1].get("content") or "{}"))


def score_delta(raw_scores: dict[str, Any], repaired_scores: dict[str, Any]) -> dict[str, float]:
    keys = sorted(set(raw_scores) | set(repaired_scores))
    return {key: round(float(repaired_scores.get(key, 0.0)) - float(raw_scores.get(key, 0.0)), 4) for key in keys}


def unsupported_projection_head(raw_head: str, learned: dict[str, str]) -> str:
    if raw_head in learned:
        return learned[raw_head]
    if "validator" in raw_head:
        return "validator-note"
    if "repair" in raw_head:
        return "repair-hint"
    return "trace-label"


def predict_repair_action(state: dict[str, Any], controller: dict[str, Any]) -> dict[str, Any]:
    repair_type = str(state.get("repair_type") or "")
    raw_atom = str(state.get("raw_atom") or "")
    target_envs = [str(env) for env in state.get("target_envs") or []]
    target_env = target_envs[0] if target_envs else "general"
    raw_head, args = parse_atom(raw_atom)
    if repair_type == "env_arg_inserted":
        repaired_atom = atom(raw_head, target_env, " ".join(args))
    elif repair_type == "env_arg_reordered":
        payload_args = [arg for arg in args if arg != target_env]
        repaired_atom = atom(raw_head, target_env, " ".join(payload_args))
    elif repair_type == "env_wrapper_projected":
        nested_head = args[1] if len(args) > 1 else "trace-label"
        values = args[2:] if len(args) > 2 else []
        repaired_atom = atom(nested_head, target_env, " ".join(values))
    elif repair_type == "unsupported_head_projected":
        projection_map = controller.get("unsupported_projection_heads") or {}
        repaired_head = unsupported_projection_head(raw_head, projection_map)
        values = args[1:] if args and args[0] == target_env else args
        repaired_atom = atom(repaired_head, target_env, f"{raw_head}: {' '.join(values)}")
    elif repair_type == "wrapped_single_atom":
        repaired_atom = atom(raw_head, target_env, " ".join(args[1:] if args and args[0] == target_env else args))
    else:
        repaired_atom = raw_atom
    return {"accept_repair": True, "repair": repair_type, "repaired_atom": repaired_atom}


def predict_verifier_action(state: dict[str, Any]) -> dict[str, Any]:
    raw_scores = dict(state.get("raw_scores") or {})
    repaired_scores = dict(state.get("repaired_scores") or {})
    delta = score_delta(raw_scores, repaired_scores)
    failing_after = [key for key, value in repaired_scores.items() if key != "overall" and float(value) < 0.85]
    verdict = "runtime_ready" if not failing_after and float(repaired_scores.get("overall", 0.0)) >= 0.85 else "needs_more_repair"
    return {"verdict": verdict, "score_delta": delta, "failing_components_after_repair": failing_after}


def predict_commit_action(state: dict[str, Any]) -> dict[str, Any]:
    ready = bool(state.get("repaired_ready_for_runtime"))
    return {
        "decision": "commit_repaired_package" if ready else "veto_or_collect_more_data",
        "reason": "repaired_runtime_ready" if ready else "repair_not_runtime_ready",
    }


def predict_action(row: dict[str, Any], controller: dict[str, Any]) -> dict[str, Any]:
    payload = prompt_payload(row)
    role = str(payload.get("role") or "")
    state = dict(payload.get("state") or {})
    if role == "metta_syntax_repair":
        return predict_repair_action(state, controller)
    if role == "semantic_contract_verifier":
        return predict_verifier_action(state)
    if role == "commit_veto":
        return predict_commit_action(state)
    return {}


def score_prediction(expected: dict[str, Any], predicted: dict[str, Any]) -> dict[str, Any]:
    keys = sorted(set(expected))
    key_hits = {key: predicted.get(key) == expected.get(key) for key in keys}
    return {
        "exact_action": predicted == expected,
        "key_accuracy": round(sum(1 for hit in key_hits.values() if hit) / len(key_hits), 4) if key_hits else 0.0,
        "key_hits": key_hits,
    }


def train_controller(train_rows: list[dict[str, Any]]) -> dict[str, Any]:
    repair_types = Counter()
    roles = Counter()
    unsupported_projection_counts: dict[str, Counter[str]] = {}
    for row in train_rows:
        payload = prompt_payload(row)
        action = expected_action(row)
        role = str(payload.get("role") or "")
        roles[role] += 1
        if role != "metta_syntax_repair":
            continue
        state = dict(payload.get("state") or {})
        repair_type = str(action.get("repair") or state.get("repair_type") or "")
        repair_types[repair_type] += 1
        if repair_type == "unsupported_head_projected":
            raw_head, _args = parse_atom(str(state.get("raw_atom") or ""))
            repaired_head, _repaired_args = parse_atom(str(action.get("repaired_atom") or ""))
            unsupported_projection_counts.setdefault(raw_head, Counter())[repaired_head] += 1
    unsupported_projection_heads = {
        raw_head: counts.most_common(1)[0][0]
        for raw_head, counts in unsupported_projection_counts.items()
        if counts
    }
    return {
        "trained_at_utc": utc_now(),
        "controller_type": "metta_repair_template_controller_v1",
        "train_rows": len(train_rows),
        "role_counts": dict(roles),
        "repair_type_counts": dict(repair_types),
        "unsupported_projection_heads": unsupported_projection_heads,
        "rules": [
            "env_arg_inserted: (head values...) -> (head env joined_values)",
            "env_arg_reordered: (head value env rest...) -> (head env joined_value_rest)",
            "env_wrapper_projected: (env env nested_head values...) -> (nested_head env joined_values)",
            "unsupported_head_projected: project unsupported head to learned supported head",
            "wrapped_single_atom: wrap bare atom and insert env",
        ],
    }


def evaluate_rows(rows: list[dict[str, Any]], controller: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    predictions = []
    role_counts: Counter[str] = Counter()
    role_exact: Counter[str] = Counter()
    for index, row in enumerate(rows):
        payload = prompt_payload(row)
        role = str(payload.get("role") or "")
        expected = expected_action(row)
        predicted = predict_action(row, controller)
        score = score_prediction(expected, predicted)
        role_counts[role] += 1
        if score["exact_action"]:
            role_exact[role] += 1
        predictions.append(
            {
                "index": index,
                "role": role,
                "expected": expected,
                "predicted": predicted,
                "score": score,
                "meta": row.get("meta") or {},
            }
        )
    count = len(predictions)
    summary = {
        "generated_at_utc": utc_now(),
        "count": count,
        "exact_action_rate": round(sum(1 for row in predictions if row["score"]["exact_action"]) / count, 4) if count else 0.0,
        "mean_key_accuracy": round(sum(float(row["score"]["key_accuracy"]) for row in predictions) / count, 4) if count else 0.0,
        "role_counts": dict(role_counts),
        "role_exact_rates": {
            role: round(role_exact.get(role, 0) / role_counts[role], 4)
            for role in sorted(role_counts)
        },
    }
    return predictions, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train and evaluate a compact MeTTa repair template controller.")
    parser.add_argument("--train-messages", required=True)
    parser.add_argument("--val-messages", required=True)
    parser.add_argument("--out-dir", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_rows = read_jsonl(Path(args.train_messages))
    val_rows = read_jsonl(Path(args.val_messages))
    controller = train_controller(train_rows)
    predictions, summary = evaluate_rows(val_rows, controller)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "repair_controller.json").write_text(json.dumps(controller, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_jsonl(out_dir / "predictions.jsonl", predictions)
    summary.update(
        {
            "train_messages": str(Path(args.train_messages)),
            "val_messages": str(Path(args.val_messages)),
            "controller": str(out_dir / "repair_controller.json"),
        }
    )
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(out_dir)
    print(json.dumps({key: summary[key] for key in ("exact_action_rate", "mean_key_accuracy")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

