from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
META_CLI = SCRIPT_DIR / "metta_trm_meta_skill.py"
SKILL_DIR = SCRIPT_DIR.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
CONTRACT_MD = SKILL_DIR / "references" / "meta_skill_contract.md"

DEFAULT_TASKS = [
    {
        "task_id": "storyworld_nav_diary_bootstrap",
        "base_skill": "storyworld-player",
        "target_env": "storyworld_nav",
        "task": (
            "Bootstrap a MeTTa package for storyworld player improvement. The package should help a small model "
            "use N-play diary memory, exact legal action constraints, character/theme retrieval cues, and commit/veto "
            "gates to find secret endings without inventing actions."
        ),
    },
    {
        "task_id": "tool_contract_router_bootstrap",
        "base_skill": "real-tool-contract-router",
        "target_env": "tool_contract_router",
        "task": (
            "Bootstrap a MeTTa package for a tool-call contract router benchmark with repo search, file lookup, "
            "shell-safe planning, scheduling, weather-like lookup, and JSON argument traps. The package should "
            "separate route, retrieve, validate, repair, and commit gates."
        ),
    },
    {
        "task_id": "intellect3_logic_signature_bootstrap",
        "base_skill": "intellect3-logic-hermes",
        "target_env": "intellect3_logic",
        "task": (
            "Bootstrap a MeTTa package for Intellect-3 Logic style symbolic amplification. The package should define "
            "grid or candidate signature validation, contradiction detection, min-edit projection, repair hints, and "
            "clear claim boundaries."
        ),
    },
]

ALLOWED_FILES = [
    "package.manifest.json",
    "package.metta",
    "contracts.metta",
    "retrieval_policy.metta",
    "failure_modes.metta",
    "examples/minimal_valid.json",
]

BLOCK_RE = re.compile(r"```(?P<label>[^\n`]*)\n(?P<body>.*?)```", re.DOTALL)
TAG_RE = re.compile(r"<(?P<file>package\.manifest\.json|package\.metta|contracts\.metta|retrieval_policy\.metta|failure_modes\.metta|examples/minimal_valid\.json)>\s*(?P<body>.*?)\s*</(?P=file)>", re.DOTALL)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def read_base_prompt(mode: str) -> str:
    skill = SKILL_MD.read_text(encoding="utf-8")
    contract = CONTRACT_MD.read_text(encoding="utf-8")
    if mode == "full":
        return f"{skill}\n\n--- CONTRACT ---\n\n{contract}"
    if mode != "compact":
        raise SystemExit(f"unknown prompt mode: {mode}")
    return """MeTTa-TRM meta-skill compact base:
- Flow: AUTHOR -> REPAIR -> VERIFY -> EXPORT_ROWS -> BENCH_ARMS -> EVOLVE_SKILL.
- Use MeTTa for contracts, constraints, validation paths, retrieval cues, failure modes, repair hints, and trace labels.
- Do not use MeTTa for long prose.
- Keep one top-level atom per line.
- Use only supported atom heads from the package compiler.
- Required files: package.manifest.json, package.metta, contracts.metta, retrieval_policy.metta, failure_modes.metta, examples/minimal_valid.json.
- TRM roles: author_router, metta_syntax_repair, semantic_contract_verifier, retrieval_policy_router, skill_patch_controller, commit_veto.
- Verifier scores syntax, manifest, contract, retrieval, repair, and trainer_export readiness.
- Claim labels: live_model_run, deterministic_replay, post_hoc_projection, control_plane_threshold_eval, environment_design, training_corpus_plan.
- Patch categories: runtime_packet_injection, retrieval_policy_update, repair_gate_update, validator_update, commit_veto_update, training_corpus_expansion, no_patch_more_data.
Supported atom heads:
package-id, base-skill, overlay, owner, env, goal, answer-shape, constraint, forbid, minimal-example, example-status, summary, query-cue, retrieval-priority, validation-path, validator-note, verifier-caveat, failure-mode, repair-hint, trace-label, profile-summary, profile-query-cue, profile-constraint, profile-forbid, profile-minimal-example, profile-repair-hint, profile-trace-label.
"""


def build_prompt(task: dict[str, str], base_prompt: str) -> list[dict[str, str]]:
    file_list = "\n".join(f"- {name}" for name in ALLOWED_FILES)
    system = (
        "You are a small local model being tested without Codex corrections. "
        "Use only the provided MeTTa-TRM meta-skill base. "
        "Return files exactly in XML-style file tags. Do not add commentary outside file tags."
    )
    user = f"""FROZEN BASE SKILL:
{base_prompt}

TASK CARD:
- task_id: {task['task_id']}
- base_skill: {task['base_skill']}
- target_env: {task['target_env']}
- task: {task['task']}

Write a tiny complete MeTTa package using only these files:
{file_list}

Strict output format:
<package.manifest.json>
{{valid JSON object}}
</package.manifest.json>
<package.metta>
(one supported atom per line)
</package.metta>
<contracts.metta>
(one supported atom per line)
</contracts.metta>
<retrieval_policy.metta>
(one supported atom per line)
</retrieval_policy.metta>
<failure_modes.metta>
(one supported atom per line)
</failure_modes.metta>
<examples/minimal_valid.json>
{{valid JSON object}}
</examples/minimal_valid.json>

Important:
- Keep MeTTa for contracts, retrieval cues, failure modes, repair hints, and trace labels, not prose.
- Use one top-level atom per line.
- Use target env "{task['target_env']}" consistently.
- Make this useful for TRM controller row export.
- Close every file tag.
- Do not repeat the full package in every file.
- Use exactly these manifest keys with underscores: package_id, title, base_skill, trm_overlay, infusion_type, target_envs, bundle_outputs, notes.
- Keep each .metta file to 4-8 atoms.
- Every .metta line must look like: (head "env_or_id" "short value")
"""
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def post_chat(endpoint: str, model: str, messages: list[dict[str, str]], max_tokens: int, temperature: float, timeout: float) -> dict[str, Any]:
    url = endpoint.rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    started = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read().decode("utf-8", errors="replace")
    elapsed = time.time() - started
    parsed = json.loads(raw)
    parsed["_elapsed_seconds"] = elapsed
    return parsed


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


def parse_tagged_files(text: str) -> dict[str, str]:
    files: dict[str, str] = {}
    for match in TAG_RE.finditer(text):
        name = match.group("file")
        files[name] = match.group("body").strip()
    if files:
        return files

    # Fallback for models that use fenced blocks with filenames as labels.
    for match in BLOCK_RE.finditer(text):
        label = match.group("label").strip()
        body = match.group("body").strip()
        for allowed in ALLOWED_FILES:
            if allowed in label:
                files[allowed] = body
                break
    return files


def write_raw_package(out_dir: Path, files: dict[str, str], raw_text: str, response: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "raw_model_output.txt").write_text(raw_text, encoding="utf-8")
    (out_dir / "response_meta.json").write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
    for rel, body in files.items():
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body.rstrip() + "\n", encoding="utf-8")


def run_cli(*args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(META_CLI), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def safe_load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"load_error": f"{type(exc).__name__}: {exc}"}


def evaluate_task(task: dict[str, str], args: argparse.Namespace, base_prompt: str, out_root: Path) -> dict[str, Any]:
    task_dir = out_root / task["task_id"]
    raw_dir = task_dir / "raw_package"
    repaired_dir = task_dir / "repaired_package"
    raw_verify = task_dir / "raw_verify.json"
    repaired_verify = task_dir / "repaired_verify.json"
    rows_path = task_dir / "repaired_trm_rows.jsonl"
    bench_path = task_dir / "bench_arms.json"
    evolve_dir = task_dir / "evolve"

    messages = build_prompt(task, base_prompt)
    response: dict[str, Any]
    error: str | None = None
    try:
        response = post_chat(args.endpoint, args.model, messages, args.max_tokens, args.temperature, args.timeout)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        response = {}
        error = f"{type(exc).__name__}: {exc}"
    raw_text = extract_content(response) if response else ""
    files = parse_tagged_files(raw_text)
    write_raw_package(raw_dir, files, raw_text, response or {"error": error})

    extraction = {
        "expected_files": ALLOWED_FILES,
        "extracted_files": sorted(files),
        "missing_files": [name for name in ALLOWED_FILES if name not in files],
        "raw_chars": len(raw_text),
        "error": error,
    }
    (task_dir / "extraction.json").write_text(json.dumps(extraction, indent=2), encoding="utf-8")

    raw_proc = run_cli("verify-packet", "--package-dir", str(raw_dir), "--out", str(raw_verify))
    repair_proc = run_cli("repair-packet", "--package-dir", str(raw_dir), "--out-dir", str(repaired_dir))
    repaired_proc = run_cli("verify-packet", "--package-dir", str(repaired_dir), "--out", str(repaired_verify))
    repaired_report = safe_load_json(repaired_verify)
    if repaired_report.get("ready_for_training_rows"):
        export_proc = run_cli("export-trm-rows", "--package-dir", str(repaired_dir), "--out", str(rows_path))
    else:
        export_proc = subprocess.CompletedProcess(
            args=["export-trm-rows"],
            returncode=3,
            stdout="skipped: repaired package is not ready_for_training_rows\n",
            stderr="",
        )
    bench_proc = run_cli("bench-arms", "--package-dir", str(repaired_dir), "--out", str(bench_path))
    evolve_proc = run_cli("evolve-skill", "--package-dir", str(repaired_dir), "--verify-report", str(repaired_verify), "--out-dir", str(evolve_dir))

    procs = {
        "raw_verify": raw_proc,
        "repair": repair_proc,
        "repaired_verify": repaired_proc,
        "export_rows": export_proc,
        "bench_arms": bench_proc,
        "evolve_skill": evolve_proc,
    }
    process_report = {
        name: {
            "returncode": proc.returncode,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
        }
        for name, proc in procs.items()
    }
    (task_dir / "process_report.json").write_text(json.dumps(process_report, indent=2), encoding="utf-8")

    repaired_rows = 0
    if rows_path.exists():
        repaired_rows = len([line for line in rows_path.read_text(encoding="utf-8").splitlines() if line.strip()])

    return {
        "task_id": task["task_id"],
        "base_skill": task["base_skill"],
        "target_env": task["target_env"],
        "raw_package_dir": str(raw_dir),
        "repaired_package_dir": str(repaired_dir),
        "extraction": extraction,
        "raw_verify": safe_load_json(raw_verify),
        "repaired_verify": repaired_report,
        "repaired_trm_rows": repaired_rows,
        "process_returncodes": {name: proc.returncode for name, proc in procs.items()},
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for result in results:
        raw_scores = result.get("raw_verify", {}).get("scores", {})
        repaired_scores = result.get("repaired_verify", {}).get("scores", {})
        rows.append(
            {
                "task_id": result["task_id"],
                "files_extracted": len(result["extraction"]["extracted_files"]),
                "files_missing": len(result["extraction"]["missing_files"]),
                "raw_overall": raw_scores.get("overall", 0.0),
                "raw_syntax": raw_scores.get("syntax", 0.0),
                "repaired_overall": repaired_scores.get("overall", 0.0),
                "repaired_syntax": repaired_scores.get("syntax", 0.0),
                "ready_for_rows": result.get("repaired_verify", {}).get("ready_for_training_rows", False),
                "ready_for_runtime": result.get("repaired_verify", {}).get("ready_for_runtime_without_review", False),
                "trm_rows": result["repaired_trm_rows"],
            }
        )
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "task_count": len(results),
        "tasks": rows,
        "averages": {
            "raw_overall": round(sum(row["raw_overall"] for row in rows) / len(rows), 4) if rows else 0.0,
            "repaired_overall": round(sum(row["repaired_overall"] for row in rows) / len(rows), 4) if rows else 0.0,
            "ready_for_rows_rate": round(sum(1 for row in rows if row["ready_for_rows"]) / len(rows), 4) if rows else 0.0,
            "ready_for_runtime_rate": round(sum(1 for row in rows if row["ready_for_runtime"]) / len(rows), 4) if rows else 0.0,
        },
    }


def load_tasks(path: str | None) -> list[dict[str, str]]:
    if not path:
        return DEFAULT_TASKS
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit("--tasks-json must contain a list")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Strictly benchmark a small model bootstrapping MeTTa/TRM packages from the frozen meta-skill base.")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8084")
    parser.add_argument("--model", default="Qwen3.5-4B.Q4_K_M.gguf")
    parser.add_argument("--tasks-json")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-tokens", type=int, default=2200)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--timeout", type=float, default=240.0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--prompt-mode", choices=["compact", "full"], default="compact")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tasks = load_tasks(args.tasks_json)
    if args.limit:
        tasks = tasks[: args.limit]
    out_root = Path(args.out_dir) / f"small_model_bootstrap_{utc_stamp()}"
    out_root.mkdir(parents=True, exist_ok=True)
    base_prompt = read_base_prompt(args.prompt_mode)
    config = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": args.endpoint,
        "model": args.model,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "timeout": args.timeout,
        "prompt_mode": args.prompt_mode,
        "strict_rule": "Codex only provides frozen base prompt, extracts files, and runs deterministic validators/repair/export scripts. Rows export is skipped unless the repaired package passes ready_for_training_rows.",
        "tasks": tasks,
    }
    (out_root / "run_config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    results = [evaluate_task(task, args, base_prompt, out_root) for task in tasks]
    summary = summarize(results)
    (out_root / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out_root)
    print(json.dumps(summary["averages"], indent=2))
    for row in summary["tasks"]:
        print(
            f"{row['task_id']}: files={row['files_extracted']}/{len(ALLOWED_FILES)} "
            f"raw={row['raw_overall']} repaired={row['repaired_overall']} rows={row['trm_rows']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
