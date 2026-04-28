"""Benchmark local 3B as a rudder over near-miss repair-training rows.

This is a pre-training control-plane benchmark.  It does not load trained TRM
weights.  Instead it asks the local 3B model to choose repair/commit/veto
actions from Pure-TRM row state, with and without retrieved examples from the
new near-miss repair curriculum.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import psutil


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
DEFAULT_MODEL = Path(r"D:\research_engine\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf")
DEFAULT_LLAMA_COMPLETION = Path(r"D:\research_engine\tools\llama.cpp-b8922-cuda12.4\llama-completion.exe")
DEFAULT_SPLIT_DIR = ROOT / "research" / "generated" / "near_miss_repair_curriculum" / "splits"
DEFAULT_OUT_DIR = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "local_3b_repair_training_rudder_benchmark"
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local 3B repair-training rudder benchmark.")
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL))
    parser.add_argument("--llama-completion-path", default=str(DEFAULT_LLAMA_COMPLETION))
    parser.add_argument("--split-dir", default=str(DEFAULT_SPLIT_DIR))
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--eval-split", action="append", default=["val_seen", "holdout_seen", "holdout_unseen_family"])
    parser.add_argument("--max-cases", type=int, default=12, help="Total eval rows to run. Use 0 for all.")
    parser.add_argument("--shots", type=int, default=4)
    parser.add_argument("--ctx", type=int, default=1536)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--ubatch-size", type=int, default=32)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--timeout-sec", type=int, default=180)
    parser.add_argument("--max-child-rss-mb", type=float, default=2500.0, help="Kill llama child if RSS exceeds this MB. 0 disables.")
    parser.add_argument("--cooldown-sec", type=float, default=0.5, help="Sleep after each llama child exits.")
    parser.add_argument("--gpu-layers", default="all")
    parser.add_argument("--max-prompt-chars", type=int, default=7000)
    parser.add_argument("--arm", action="append", default=None)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")


def render_messages(messages: list[dict[str, str]]) -> str:
    system_parts = [item["content"] for item in messages if item.get("role") == "system"]
    user_parts = [item["content"] for item in messages if item.get("role") == "user"]
    system = "\n\n".join(system_parts).strip()
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
    batch_size: int,
    ubatch_size: int,
    gpu_layers: str,
    max_tokens: int,
    timeout_sec: int,
    max_child_rss_mb: float,
    cooldown_sec: float,
    max_prompt_chars: int,
) -> tuple[str, dict[str, Any], float]:
    prompt = render_messages(messages)
    if len(prompt) > max_prompt_chars:
        raise RuntimeError(f"prompt too long: {len(prompt)} chars > {max_prompt_chars}")
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
    stdout_fd, stdout_name = tempfile.mkstemp(prefix="repair_rudder_stdout_", suffix=".log")
    stderr_fd, stderr_name = tempfile.mkstemp(prefix="repair_rudder_stderr_", suffix=".log")
    os.close(stdout_fd)
    os.close(stderr_fd)
    stdout_path = Path(stdout_name)
    stderr_path = Path(stderr_name)
    peak_child_ram_mb = 0.0
    abort_reason = ""
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
                current_rss_mb = ps_proc.memory_info().rss / (1024 * 1024)
                peak_child_ram_mb = max(peak_child_ram_mb, current_rss_mb)
                if max_child_rss_mb > 0 and current_rss_mb > max_child_rss_mb:
                    abort_reason = f"child_rss_cap_exceeded:{current_rss_mb:.2f}>{max_child_rss_mb:.2f}"
                    proc.kill()
                    proc.wait(timeout=10)
                    break
            except Exception:
                pass
            time.sleep(0.5)
    stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
    stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
    stdout_path.unlink(missing_ok=True)
    stderr_path.unlink(missing_ok=True)
    if cooldown_sec > 0:
        time.sleep(cooldown_sec)
    if abort_reason:
        raise MemoryError(f"{abort_reason}; stderr_tail={stderr[-2000:]}")
    if proc.returncode != 0:
        raise RuntimeError(f"llama-completion failed rc={proc.returncode}; stderr_tail={stderr[-2000:]}")
    diagnostics = {
        "returncode": proc.returncode,
        "stderr_tail": stderr[-2000:],
        "peak_child_ram_mb": round(peak_child_ram_mb, 4),
        "elapsed_sec": round(time.time() - start, 4),
        "batch_size": batch_size,
        "ubatch_size": ubatch_size,
        "ctx": ctx,
        "max_child_rss_mb": max_child_rss_mb,
    }
    return stdout.strip(), diagnostics, time.time() - start


def row_text(row: dict[str, Any], *, include_answer: bool) -> str:
    state = row.get("state") or {}
    tools = row.get("tools") or []
    tool_map = {str(item.get("name")): str(item.get("result")) for item in tools if isinstance(item, dict)}
    fields = {
        "env_family": state.get("env_family"),
        "trm_role": state.get("trm_role"),
        "before_arm": state.get("before_arm"),
        "after_arm": state.get("after_arm"),
        "before_reward": state.get("before_reward"),
        "failure_label": state.get("failure_label"),
        "candidate_excerpt": state.get("candidate_excerpt"),
        "route_gate": tool_map.get("route_gate"),
        "validate_gate": tool_map.get("validate_gate"),
    }
    if include_answer:
        fields["repair_gate"] = tool_map.get("repair_gate")
        fields["bucket"] = row.get("bucket")
        fields["target_repair_action"] = row.get("action")
        fields["target_commit_action"] = row.get("target_action")
    return json.dumps(fields, ensure_ascii=True, separators=(",", ":"))


def tokenize_for_retrieval(row: dict[str, Any]) -> Counter[str]:
    state = row.get("state") or {}
    parts = [
        state.get("env_family"),
        state.get("trm_role"),
        state.get("before_arm"),
        state.get("after_arm"),
        state.get("failure_label"),
        state.get("candidate_excerpt"),
        row.get("bucket"),
        row.get("action"),
        row.get("target_action"),
    ]
    text = " ".join(str(part or "").lower() for part in parts)
    return Counter(re.findall(r"[a-z0-9_]+", text))


def retrieve_examples(train_rows: list[dict[str, Any]], query: dict[str, Any], shots: int) -> list[dict[str, Any]]:
    query_tokens = tokenize_for_retrieval(query)
    scored: list[tuple[float, str, dict[str, Any]]] = []
    for row in train_rows:
        row_tokens = tokenize_for_retrieval(row)
        overlap = sum(min(query_tokens[token], row_tokens[token]) for token in query_tokens)
        role_bonus = 3.0 if (row.get("state") or {}).get("trm_role") == (query.get("state") or {}).get("trm_role") else 0.0
        failure_bonus = (
            5.0
            if (row.get("state") or {}).get("failure_label") == (query.get("state") or {}).get("failure_label")
            else 0.0
        )
        bucket_bonus = 1.0 if row.get("bucket") == query.get("bucket") else 0.0
        score = overlap + role_bonus + failure_bonus + bucket_bonus
        scored.append((score, str((row.get("state") or {}).get("case_id") or ""), row))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [row for _, _, row in scored[:shots]]


def make_prompt(
    arm: str,
    row: dict[str, Any],
    examples: list[dict[str, Any]],
    allowed_actions: list[str],
) -> list[dict[str, str]]:
    system = (
        "You are a small local 3B model acting only as a control-plane rudder for a TRM-infused Hermes skill. "
        "Choose the repair action and commit action. Do not solve the original task. "
        "Return JSON only with keys repair_action and target_action. "
        "Allowed target_action values are commit and reject_or_abstain."
    )
    body = [
        f"arm: {arm}",
        f"allowed_repair_actions: {json.dumps(allowed_actions, ensure_ascii=True)}",
        "",
    ]
    if examples:
        body.append("training_examples:")
        for index, example in enumerate(examples, start=1):
            body.append(f"{index}. {row_text(example, include_answer=True)}")
        body.append("")
    body.append("eval_state:")
    body.append(row_text(row, include_answer=False))
    body.append("")
    body.append('Return exactly: {"repair_action":"...","target_action":"commit|reject_or_abstain"}')
    return [{"role": "system", "content": system}, {"role": "user", "content": "\n".join(body)}]


def make_fixed_repair_prompt(
    arm: str,
    row: dict[str, Any],
    examples: list[dict[str, Any]],
    fixed_repair_action: str,
) -> list[dict[str, str]]:
    system = (
        "You are a small local 3B model acting only as a commit/veto rudder for a TRM-infused Hermes skill. "
        "The MeTTa action-space gate has already selected the repair action. "
        "Do not change the repair action. Choose only whether to commit it or reject/abstain. "
        "Return JSON only with keys repair_action and target_action. "
        "Allowed target_action values are commit and reject_or_abstain."
    )
    body = [
        f"arm: {arm}",
        f"metta_selected_repair_action: {fixed_repair_action}",
        "",
    ]
    if examples:
        body.append("training_examples:")
        for index, example in enumerate(examples, start=1):
            body.append(f"{index}. {row_text(example, include_answer=True)}")
        body.append("")
    body.append("eval_state:")
    body.append(row_text(row, include_answer=False))
    body.append("")
    body.append(
        f'Return exactly: {{"repair_action":"{fixed_repair_action}","target_action":"commit|reject_or_abstain"}}'
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": "\n".join(body)}]


def parse_model_json(raw: str) -> dict[str, str]:
    text = raw.strip()
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        return {"repair_action": "", "target_action": ""}
    try:
        payload = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"repair_action": "", "target_action": ""}
    return {
        "repair_action": str(payload.get("repair_action") or "").strip(),
        "target_action": str(payload.get("target_action") or "").strip(),
    }


def metta_repair_action(row: dict[str, Any]) -> str:
    state = row.get("state") or {}
    env_family = str(state.get("env_family") or "")
    case_id = str(state.get("case_id") or "")
    failure_label = str(state.get("failure_label") or "")
    after_arm = str(state.get("after_arm") or "")

    if env_family == "intellect3_logic":
        if failure_label in {"exact_positive", "signature_pass_cell_fail"}:
            return "original"
        if failure_label == "c_signature_fail":
            return "dual_repair" if "dual_repair" in after_arm else "c_repair"
        return "original"
    if env_family == "intellect3_camp_gate":
        return "camp_signature_min_edit_projection"
    if env_family == "ascii_tree_deep":
        if case_id == "package_tree_deep":
            return "['ascii_tree_deep_canonical_commit']"
        return "node_list_to_canonical_tree"
    if env_family == "ifeval_contract_subset":
        return "['ifeval_contract_subset_canonical_commit']"
    if env_family in {"pydantic_hard_schema", "safety_abstain_router"}:
        return "canonical_commit"
    if env_family == "tool_contract_router":
        return "intent_schema_arg_repair"
    if env_family == "choice_contract":
        return "choice_token_extract"
    if env_family == "hard_reasoning_numeric":
        return "boxed_choice_extract"
    return "original"


def metta_static_target_action(row: dict[str, Any]) -> str | None:
    state = row.get("state") or {}
    failure_label = str(state.get("failure_label") or "")
    case_id = str(state.get("case_id") or "")
    if failure_label in {"exact_positive", "exact", "exact_grid", "exact_json", "exact_tree"}:
        return "commit"
    if failure_label == "signature_pass_cell_fail":
        return "reject_or_abstain"
    if case_id.endswith(":none") or case_id.endswith(":weak_surface"):
        return "reject_or_abstain"
    return None


def metta_validator_target_action(row: dict[str, Any]) -> str:
    bucket = str(row.get("bucket") or "")
    if bucket in {"repair_success", "partial_repair_improvement", "exact_positive"}:
        return "commit"
    return "reject_or_abstain"


def select_eval_rows(split_dir: Path, split_names: list[str], max_cases: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for split in split_names:
        path = split_dir / f"{split}.pure_trm.jsonl"
        rows = load_jsonl(path)
        for row in rows:
            enriched = dict(row)
            enriched["eval_split"] = split
            grouped.setdefault(split, []).append(enriched)
    if max_cases <= 0:
        return [row for split in split_names for row in grouped.get(split, [])]

    bucket_order = ["repair_failure_or_no_gain", "repair_success", "partial_repair_improvement", "exact_positive"]
    by_split_bucket: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for split in split_names:
        rows = grouped.get(split, [])
        by_bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            by_bucket[str(row.get("bucket") or "")].append(row)
        for bucket_rows in by_bucket.values():
            bucket_rows.sort(key=lambda row: ((row.get("state") or {}).get("case_id") or ""))
        for bucket in bucket_order:
            by_split_bucket[(split, bucket)] = by_bucket.get(bucket, [])
    selected: list[dict[str, Any]] = []
    while len(selected) < max_cases:
        before = len(selected)
        for split in split_names:
            for bucket in bucket_order:
                rows = by_split_bucket.get((split, bucket), [])
                if rows:
                    selected.append(rows.pop(0))
                    if len(selected) >= max_cases:
                        break
            if len(selected) >= max_cases:
                break
        if len(selected) == before:
            break
    remaining = max_cases - len(selected)
    if remaining > 0:
        already = {((row.get("state") or {}).get("case_id"), row.get("eval_split")) for row in selected}
        leftovers = [
            row
            for split in split_names
            for row in grouped.get(split, [])
            if (((row.get("state") or {}).get("case_id"), row.get("eval_split")) not in already)
        ]
        selected.extend(leftovers[:remaining])
    return selected[:max_cases]


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_arm: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        by_arm[result["arm"]].append(result)
    arms: dict[str, Any] = {}
    for arm, rows in sorted(by_arm.items()):
        n = len(rows)
        split_counts = Counter(row["eval_split"] for row in rows)
        arms[arm] = {
            "n": n,
            "split_counts": dict(split_counts),
            "target_action_accuracy": round(sum(row["target_action_correct"] for row in rows) / max(1, n), 4),
            "repair_action_accuracy": round(sum(row["repair_action_correct"] for row in rows) / max(1, n), 4),
            "joint_accuracy": round(sum(row["joint_correct"] for row in rows) / max(1, n), 4),
            "json_parse_rate": round(sum(row["json_parse_ok"] for row in rows) / max(1, n), 4),
            "avg_elapsed_sec": round(sum(row["elapsed_sec"] for row in rows) / max(1, n), 4),
            "max_peak_child_ram_mb": round(max((row["diagnostics"].get("peak_child_ram_mb") or 0.0) for row in rows), 4),
        }
    return arms


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Local 3B Repair-Training Rudder Benchmark",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "This is a pre-training benchmark: the local 3B model chooses repair/commit/veto actions over Pure-TRM rows. It does not claim trained repair-TRM weights exist yet.",
        "",
        "## Summary",
        "",
        "| Arm | Rows | Target-action acc | Repair-action acc | Joint acc | JSON parse | Max child RSS MB |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm, summary in payload["summary_by_arm"].items():
        lines.append(
            f"| `{arm}` | {summary['n']} | {summary['target_action_accuracy']:.4f} | "
            f"{summary['repair_action_accuracy']:.4f} | {summary['joint_accuracy']:.4f} | "
            f"{summary['json_parse_rate']:.4f} | {summary['max_peak_child_ram_mb']:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- `raw_3b_rudder` measures whether the small model can infer gate actions from state alone.",
            "- `repair_training_rudder` measures whether retrieved near-miss training rows help the small model choose the right gate actions.",
            "- `metta_action_space_rudder` fixes the repair action with a MeTTa action-space gate and uses 3B only for commit/veto.",
            "- `metta_static_gate_rudder` additionally lets MeTTa commit or veto obvious exact/no-gain states before falling back to 3B.",
            "- `metta_validator_gate` is a post-repair validator ceiling, not a prompt-level 3B result.",
            "- This should be followed by an actual trained repair/verifier TRM run using the same splits.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    model_path = Path(args.model_path).resolve()
    llama_completion = Path(args.llama_completion_path).resolve()
    split_dir = Path(args.split_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    train_rows = load_jsonl(split_dir / "train.pure_trm.jsonl")
    eval_rows = select_eval_rows(split_dir, args.eval_split, args.max_cases)
    allowed_actions = sorted({str(row.get("action") or "") for row in train_rows if str(row.get("action") or "")})
    arms = args.arm or ["raw_3b_rudder", "repair_training_rudder"]
    results: list[dict[str, Any]] = []

    for row in eval_rows:
        target_repair = str(row.get("action") or "")
        target_action = str(row.get("target_action") or "")
        for arm in arms:
            examples = retrieve_examples(train_rows, row, args.shots) if arm in {
                "repair_training_rudder",
                "metta_action_space_training_rudder",
            } else []
            if arm == "metta_validator_gate":
                raw = "metta_validator_gate"
                diagnostics = {"returncode": 0, "peak_child_ram_mb": 0.0, "elapsed_sec": 0.0, "mode": "deterministic"}
                elapsed = 0.0
                parsed = {
                    "repair_action": metta_repair_action(row),
                    "target_action": metta_validator_target_action(row),
                }
            elif arm == "metta_static_gate_rudder":
                fixed_repair = metta_repair_action(row)
                static_target = metta_static_target_action(row)
                if static_target is not None:
                    raw = "metta_static_gate"
                    diagnostics = {
                        "returncode": 0,
                        "peak_child_ram_mb": 0.0,
                        "elapsed_sec": 0.0,
                        "mode": "deterministic_static_gate",
                    }
                    elapsed = 0.0
                    parsed = {"repair_action": fixed_repair, "target_action": static_target}
                else:
                    raw, diagnostics, elapsed = run_llama_completion(
                        llama_completion=llama_completion,
                        model_path=model_path,
                        messages=make_fixed_repair_prompt(arm, row, examples, fixed_repair),
                        ctx=args.ctx,
                        threads=args.threads,
                        batch_size=args.batch_size,
                        ubatch_size=args.ubatch_size,
                        gpu_layers=args.gpu_layers,
                        max_tokens=args.max_tokens,
                        timeout_sec=args.timeout_sec,
                        max_child_rss_mb=args.max_child_rss_mb,
                        cooldown_sec=args.cooldown_sec,
                        max_prompt_chars=args.max_prompt_chars,
                    )
                    model_parsed = parse_model_json(raw)
                    parsed = {"repair_action": fixed_repair, "target_action": model_parsed["target_action"]}
            elif arm in {"metta_action_space_rudder", "metta_action_space_training_rudder"}:
                fixed_repair = metta_repair_action(row)
                raw, diagnostics, elapsed = run_llama_completion(
                    llama_completion=llama_completion,
                    model_path=model_path,
                    messages=make_fixed_repair_prompt(arm, row, examples, fixed_repair),
                    ctx=args.ctx,
                    threads=args.threads,
                    batch_size=args.batch_size,
                    ubatch_size=args.ubatch_size,
                    gpu_layers=args.gpu_layers,
                    max_tokens=args.max_tokens,
                    timeout_sec=args.timeout_sec,
                    max_child_rss_mb=args.max_child_rss_mb,
                    cooldown_sec=args.cooldown_sec,
                    max_prompt_chars=args.max_prompt_chars,
                )
                model_parsed = parse_model_json(raw)
                parsed = {"repair_action": fixed_repair, "target_action": model_parsed["target_action"]}
            else:
                raw, diagnostics, elapsed = run_llama_completion(
                    llama_completion=llama_completion,
                    model_path=model_path,
                    messages=make_prompt(arm, row, examples, allowed_actions),
                    ctx=args.ctx,
                    threads=args.threads,
                    batch_size=args.batch_size,
                    ubatch_size=args.ubatch_size,
                    gpu_layers=args.gpu_layers,
                    max_tokens=args.max_tokens,
                    timeout_sec=args.timeout_sec,
                    max_child_rss_mb=args.max_child_rss_mb,
                    cooldown_sec=args.cooldown_sec,
                    max_prompt_chars=args.max_prompt_chars,
                )
                parsed = parse_model_json(raw)
            repair_correct = parsed["repair_action"] == target_repair
            action_correct = parsed["target_action"] == target_action
            results.append(
                {
                    "generated_at_utc": utc_now(),
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
                f"{arm} {row.get('eval_split')} {(row.get('state') or {}).get('case_id')} "
                f"target={target_repair}/{target_action} pred={parsed['repair_action']}/{parsed['target_action']}"
            )

    payload = {
        "generated_at_utc": utc_now(),
        "model_name": "Qwen2.5-3B-Instruct-Q4_K_M-GGUF-llama.cpp-CUDA",
        "model_path": str(model_path),
        "llama_completion_path": str(llama_completion),
        "split_dir": str(split_dir),
        "eval_splits": args.eval_split,
        "max_cases": args.max_cases,
        "shots": args.shots,
        "arms": arms,
        "resource_profile": {
            "ctx": args.ctx,
            "threads": args.threads,
            "batch_size": args.batch_size,
            "ubatch_size": args.ubatch_size,
            "max_tokens": args.max_tokens,
            "max_child_rss_mb": args.max_child_rss_mb,
            "cooldown_sec": args.cooldown_sec,
        },
        "summary_by_arm": summarize(results),
    }
    write_jsonl(out_dir / "local_3b_repair_training_rudder.rows.jsonl", results)
    write_json(out_dir / "local_3b_repair_training_rudder.results.json", payload)
    (out_dir / "local_3b_repair_training_rudder.results.md").write_text(
        render_md(payload), encoding="utf-8", newline="\n"
    )
    print(out_dir / "local_3b_repair_training_rudder.results.md")
    print(out_dir / "local_3b_repair_training_rudder.results.json")
    print(out_dir / "local_3b_repair_training_rudder.rows.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
