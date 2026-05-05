from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SUPPORTED_HEADS = {
    "package-id",
    "base-skill",
    "overlay",
    "owner",
    "env",
    "goal",
    "answer-shape",
    "constraint",
    "forbid",
    "minimal-example",
    "example-status",
    "summary",
    "query-cue",
    "retrieval-priority",
    "validation-path",
    "validator-note",
    "verifier-caveat",
    "failure-mode",
    "repair-hint",
    "trace-label",
    "profile-summary",
    "profile-query-cue",
    "profile-constraint",
    "profile-forbid",
    "profile-minimal-example",
    "profile-repair-hint",
    "profile-trace-label",
}

ENV_VALUE_HEADS = {
    "goal",
    "answer-shape",
    "constraint",
    "forbid",
    "minimal-example",
    "example-status",
    "summary",
    "query-cue",
    "retrieval-priority",
    "validation-path",
    "validator-note",
    "verifier-caveat",
    "failure-mode",
    "repair-hint",
    "trace-label",
}

REQUIRED_MANIFEST_FIELDS = {
    "package_id",
    "title",
    "base_skill",
    "trm_overlay",
    "infusion_type",
    "target_envs",
    "bundle_outputs",
    "notes",
}

REQUIRED_PACKAGE_FILES = [
    "package.manifest.json",
    "package.metta",
    "contracts.metta",
    "retrieval_policy.metta",
    "failure_modes.metta",
    "examples/minimal_valid.json",
]

TRM_ROLES = [
    "author_router",
    "metta_syntax_repair",
    "semantic_contract_verifier",
    "retrieval_policy_router",
    "skill_patch_controller",
    "commit_veto",
]

ATOM_RE = re.compile(r"^\((?P<body>.*)\)$")
TOKEN_RE = re.compile(r'"(?:[^"\\]|\\.)*"|[^\s()]+')


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str, default: str = "metta_task") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return slug[:80] or default


def read_text_arg(value: str | None, path: str | None) -> str:
    parts: list[str] = []
    if value:
        parts.append(value.strip())
    if path:
        parts.append(Path(path).read_text(encoding="utf-8").strip())
    text = "\n\n".join(part for part in parts if part)
    if not text:
        raise SystemExit("expected --task or --task-file")
    return text


def quote(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def atom(head: str, *args: Any) -> str:
    return "(" + " ".join([head, *[quote(arg) for arg in args]]) + ")"


def strip_quotes(token: str) -> str:
    token = token.strip()
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return str(json.loads(token))
    return token


def parse_atom_line(line: str) -> dict[str, Any] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith(";"):
        return None
    match = ATOM_RE.match(stripped)
    if not match:
        return {"ok": False, "head": "", "args": [], "error": "not_single_parenthesized_atom", "line": stripped}
    tokens = [strip_quotes(token) for token in TOKEN_RE.findall(match.group("body"))]
    if not tokens:
        return {"ok": False, "head": "", "args": [], "error": "empty_atom", "line": stripped}
    head = str(tokens[0])
    if head not in SUPPORTED_HEADS:
        return {"ok": False, "head": head, "args": tokens[1:], "error": "unsupported_head", "line": stripped}
    return {"ok": True, "head": head, "args": [str(token) for token in tokens[1:]], "line": stripped}


def looks_like_env(value: str) -> bool:
    compact = value.strip().lower()
    if not compact or re.search(r"\s", compact):
        return False
    return bool(
        re.search(r"(?:^|_)(env|nav|logic|router|storyworld|intellect|tool|contract)(?:_|$)", compact)
        or compact.endswith("_bench")
        or compact.endswith("_bootstrap")
    )


def normalize_env_first_atom(parsed: dict[str, Any], default_env: str | None = None) -> tuple[str | None, dict[str, Any] | None]:
    if not parsed.get("ok"):
        return None, None
    head = str(parsed.get("head") or "")
    args = [str(arg) for arg in parsed.get("args") or []]
    if head not in ENV_VALUE_HEADS or len(args) < 1:
        return None, None
    if len(args) >= 2 and looks_like_env(args[1]) and not looks_like_env(args[0]):
        normalized = atom(head, args[1], " ".join([args[0], *args[2:]]))
        return normalized, {"from": parsed["line"], "to": normalized, "repair": "env_arg_reordered"}
    if default_env and not looks_like_env(args[0]):
        normalized = atom(head, default_env, " ".join(args))
        return normalized, {"from": parsed["line"], "to": normalized, "repair": "env_arg_inserted"}
    return None, None


def normalize_env_wrapper_atom(parsed: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    if not parsed.get("ok") or parsed.get("head") != "env":
        return None, None
    args = [str(arg) for arg in parsed.get("args") or []]
    if len(args) < 3:
        return None, None
    env_name = args[0]
    nested_head = args[1]
    if nested_head not in ENV_VALUE_HEADS:
        return None, None
    value_args = args[2:]
    if len(value_args) >= 2 and looks_like_env(value_args[0]):
        value_args = value_args[1:]
    value = " ".join(value_args)
    normalized = atom(nested_head, env_name, value)
    return normalized, {"from": parsed["line"], "to": normalized, "repair": "env_wrapper_projected"}


def iter_metta_lines(package_dir: Path) -> Iterable[tuple[Path, int, str]]:
    for path in sorted(package_dir.glob("*.metta")):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            yield path, line_no, line


def load_manifest(package_dir: Path) -> dict[str, Any]:
    manifest_path = package_dir / "package.manifest.json"
    if not manifest_path.exists():
        return {}
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("package.manifest.json must decode to an object")
    return payload


def load_atoms(package_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    atoms: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for path, line_no, line in iter_metta_lines(package_dir):
        parsed = parse_atom_line(line)
        if parsed is None:
            continue
        row = {**parsed, "source_file": path.name, "line_no": line_no}
        if parsed["ok"]:
            atoms.append(row)
        else:
            errors.append(row)
    return atoms, errors


def atoms_by_head(atoms: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in atoms:
        grouped.setdefault(row["head"], []).append(row)
    return grouped


def has_env_value(heads: dict[str, list[dict[str, Any]]], head: str, envs: list[str]) -> bool:
    rows = heads.get(head) or []
    if not envs:
        return bool(rows)
    env_set = set(envs)
    return any((row.get("args") or []) and row["args"][0] in env_set for row in rows)


def infer_short_summary(task: str) -> str:
    collapsed = " ".join(task.split())
    return collapsed[:220] or "MeTTa/TRM meta-skill task."


def default_constraints(base_skill: str) -> list[str]:
    return [
        "keep one top-level MeTTa atom per line",
        "emit only supported compiler atom heads",
        "separate routing, validation, repair, and commit decisions",
        f"preserve the observable contract of {base_skill}",
    ]


def default_failure_modes() -> list[str]:
    return [
        "unsupported_atom_head",
        "missing_validation_path",
        "retrieval_cue_too_broad",
        "repair_hint_not_actionable",
        "benchmark_gain_without_claim_label",
    ]


def default_repair_hints() -> list[str]:
    return [
        "wrap bare MeTTa lines in a single parenthesized atom",
        "replace unsupported heads with summary, constraint, query-cue, failure-mode, repair-hint, or trace-label",
        "add validation-path before exporting runtime packets",
        "route ambiguous skill changes to no_patch_more_data",
    ]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def cmd_author_packet(args: argparse.Namespace) -> int:
    task = read_text_arg(args.task, args.task_file)
    base_skill = args.base_skill
    envs = args.target_env or [slugify(base_skill)]
    package_id = args.package_id or f"{slugify(base_skill)}_{slugify(envs[0])}_metta_trm_meta"
    out_dir = Path(args.out_dir)

    manifest = {
        "package_id": package_id,
        "title": args.title or f"MeTTa TRM Meta Package for {base_skill}",
        "base_skill": base_skill,
        "trm_overlay": "metta-trm-meta-skill",
        "infusion_type": "metta_trm_meta_control_plane",
        "target_envs": envs,
        "bundle_outputs": [
            "retrieval_packet",
            "critic_hints",
            "trace_labels",
            "runtime_packet",
            "metta_trm_rows",
            "meta_skill_scorecard",
        ],
        "notes": {
            "generated_at_utc": utc_now(),
            "source": "metta-trm-meta-skill author-packet",
            "task_summary": infer_short_summary(task),
            "claim_label": args.claim_label,
        },
    }
    write_json(out_dir / "package.manifest.json", manifest)

    package_lines = [
        atom("package-id", package_id),
        atom("base-skill", base_skill),
        atom("overlay", "metta-trm-meta-skill"),
        atom("owner", "metta-trm-meta-skill"),
    ]
    for env in envs:
        package_lines.append(atom("env", env))
        package_lines.append(atom("goal", env, infer_short_summary(task)))
    write_text(out_dir / "package.metta", "\n".join(package_lines))

    contract_lines: list[str] = []
    for env in envs:
        contract_lines.extend(
            [
                atom("answer-shape", env, "bounded_metta_package_plus_trm_rows"),
                atom("summary", env, infer_short_summary(task)),
                atom("validation-path", env, "repair_packet -> verify_packet -> export_trm_rows -> bench_arms"),
                atom("minimal-example", env, json.dumps({"role": "commit_veto", "action": "commit_when_verified"}, ensure_ascii=False)),
                atom("example-status", env, "minimal_valid"),
            ]
        )
        for constraint in default_constraints(base_skill):
            contract_lines.append(atom("constraint", env, constraint))
        for forbid in [
            "do not use MeTTa for long prose generation",
            "do not claim live benchmark gain without receipts",
            "do not merge controller rows with decorative chain-of-thought",
        ]:
            contract_lines.append(atom("forbid", env, forbid))
    write_text(out_dir / "contracts.metta", "\n".join(contract_lines))

    retrieval_lines: list[str] = []
    for env in envs:
        for cue in [
            base_skill,
            env,
            "benchmark failure traces",
            "MCP lookup receipts",
            "near-miss repair examples",
            "fixed anchor scorecards",
        ]:
            retrieval_lines.append(atom("query-cue", env, cue))
        for priority in [
            "load current skill contract before task traces",
            "load fixed anchor scorecard before mutating skill flow",
            "prefer compact prior rows over raw long context",
        ]:
            retrieval_lines.append(atom("retrieval-priority", env, priority))
    write_text(out_dir / "retrieval_policy.metta", "\n".join(retrieval_lines))

    failure_lines: list[str] = []
    for env in envs:
        for failure in default_failure_modes():
            failure_lines.append(atom("failure-mode", env, failure))
            failure_lines.append(atom("trace-label", env, failure))
        for hint in default_repair_hints():
            failure_lines.append(atom("repair-hint", env, hint))
    write_text(out_dir / "failure_modes.metta", "\n".join(failure_lines))

    write_json(
        out_dir / "examples" / "minimal_valid.json",
        {
            "package_id": package_id,
            "role": "commit_veto",
            "state": {"env": envs[0], "scorecard_overall": 0.9},
            "action": {"decision": "commit", "claim_label": args.claim_label},
        },
    )
    print(out_dir)
    return 0


def repair_line(line: str, default_env: str | None = None) -> tuple[str, dict[str, Any] | None]:
    stripped = line.strip()
    if not stripped or stripped.startswith(";"):
        return line, None
    parsed = parse_atom_line(stripped)
    if parsed and parsed.get("ok"):
        normalized, report = normalize_env_wrapper_atom(parsed)
        if normalized:
            return normalized, report
        normalized, report = normalize_env_first_atom(parsed, default_env=default_env)
        if normalized:
            return normalized, report
        return stripped, None
    candidate = stripped
    if not candidate.startswith("("):
        candidate = "(" + candidate
    if not candidate.endswith(")"):
        candidate = candidate + ")"
    repaired = parse_atom_line(candidate)
    if repaired and repaired.get("ok"):
        return candidate, {"from": stripped, "to": candidate, "repair": "wrapped_single_atom"}
    if repaired and repaired.get("error") == "unsupported_head":
        head = str(repaired.get("head") or "")
        args = [str(arg) for arg in repaired.get("args") or []]
        env = next((arg for arg in args if re.search(r"(env|nav|logic|router|storyworld|intellect|tool)", arg, re.I)), "general")
        detail = f"{head}: " + " ".join(args)
        replacement_head = "trace-label"
        if "repair" in head:
            replacement_head = "repair-hint"
        elif "valid" in head or "validator" in head or "verify" in head:
            replacement_head = "validator-note"
        elif "retriev" in head or "query" in head:
            replacement_head = "query-cue"
        elif "commit" in head or "veto" in head:
            replacement_head = "trace-label"
        candidate = atom(replacement_head, env, detail)
        return candidate, {"from": stripped, "to": candidate, "repair": "unsupported_head_projected"}
    return stripped, {"from": stripped, "to": stripped, "repair": "unrepaired", "error": (parsed or repaired or {}).get("error")}


def cmd_repair_packet(args: argparse.Namespace) -> int:
    package_dir = Path(args.package_dir)
    out_dir = Path(args.out_dir)
    if not package_dir.exists():
        raise SystemExit(f"missing package dir: {package_dir}")
    manifest = load_manifest(package_dir)
    target_envs = [str(env) for env in manifest.get("target_envs", []) if str(env).strip()]
    default_env = target_envs[0] if target_envs else None
    repairs: list[dict[str, Any]] = []
    for src in sorted(package_dir.iterdir()):
        dst = out_dir / src.name
        if src.is_dir():
            continue
        if src.suffix != ".metta":
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
            continue
        out_lines: list[str] = []
        for line_no, line in enumerate(src.read_text(encoding="utf-8").splitlines(), start=1):
            repaired, report = repair_line(line, default_env=default_env)
            out_lines.append(repaired)
            if report:
                repairs.append({"source_file": src.name, "line_no": line_no, **report})
        write_text(dst, "\n".join(out_lines))
    examples = package_dir / "examples"
    if examples.exists():
        for item in examples.rglob("*"):
            if item.is_file():
                target = out_dir / "examples" / item.relative_to(examples)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(item.read_bytes())
    write_json(out_dir / "repair_report.json", {"generated_at_utc": utc_now(), "repairs": repairs})
    print(out_dir)
    return 0


def score_package(package_dir: Path) -> dict[str, Any]:
    manifest = load_manifest(package_dir)
    atoms, errors = load_atoms(package_dir)
    heads = atoms_by_head(atoms)
    manifest_missing = sorted(REQUIRED_MANIFEST_FIELDS - set(manifest))
    missing_files = [rel for rel in REQUIRED_PACKAGE_FILES if not (package_dir / rel).exists()]
    file_score = (len(REQUIRED_PACKAGE_FILES) - len(missing_files)) / len(REQUIRED_PACKAGE_FILES)
    envs = [str(env) for env in manifest.get("target_envs", [])] or [row["args"][0] for row in heads.get("env", []) if row["args"]]

    total_lines = len(atoms) + len(errors)
    syntax = 1.0 if total_lines and not errors else (len(atoms) / total_lines if total_lines else 0.0)
    manifest_score = 1.0 if not manifest_missing else max(0.0, 1.0 - (len(manifest_missing) / len(REQUIRED_MANIFEST_FIELDS)))

    contract_checks = [
        has_env_value(heads, "goal", envs),
        has_env_value(heads, "answer-shape", envs),
        has_env_value(heads, "summary", envs),
        has_env_value(heads, "constraint", envs),
        has_env_value(heads, "forbid", envs),
        has_env_value(heads, "minimal-example", envs),
        has_env_value(heads, "validation-path", envs),
    ]
    retrieval_checks = [has_env_value(heads, "query-cue", envs), has_env_value(heads, "retrieval-priority", envs)]
    repair_checks = [has_env_value(heads, "failure-mode", envs), has_env_value(heads, "repair-hint", envs), has_env_value(heads, "trace-label", envs)]
    trainer_checks = [
        syntax >= 0.95,
        manifest_score >= 0.85,
        file_score >= 0.85,
        all(contract_checks[:4]),
        all(retrieval_checks),
        all(repair_checks),
        bool(envs),
    ]

    scores = {
        "files": round(file_score, 4),
        "syntax": round(syntax, 4),
        "manifest": round(manifest_score, 4),
        "contract": round(sum(contract_checks) / len(contract_checks), 4),
        "retrieval": round(sum(retrieval_checks) / len(retrieval_checks), 4),
        "repair": round(sum(repair_checks) / len(repair_checks), 4),
        "trainer_export": round(sum(1 for ok in trainer_checks if ok) / len(trainer_checks), 4),
    }
    overall = sum(scores[key] for key in ["files", "syntax", "manifest", "contract", "retrieval", "repair", "trainer_export"]) / 7
    return {
        "generated_at_utc": utc_now(),
        "package_dir": str(package_dir),
        "package_id": manifest.get("package_id", ""),
        "target_envs": envs,
        "scores": {**scores, "overall": round(overall, 4)},
        "manifest_missing": manifest_missing,
        "missing_files": missing_files,
        "atom_count": len(atoms),
        "error_count": len(errors),
        "errors": errors[:50],
        "ready_for_training_rows": overall >= 0.7 and manifest_score >= 0.85,
        "ready_for_runtime_without_review": overall >= 0.85 and file_score >= 1.0 and manifest_score >= 0.85 and not errors,
    }


def cmd_verify_packet(args: argparse.Namespace) -> int:
    report = score_package(Path(args.package_dir))
    if args.out:
        write_json(Path(args.out), report)
    print(json.dumps(report["scores"], indent=2))
    return 0 if report["scores"]["overall"] >= args.min_score else 2


def package_context(package_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, list[dict[str, Any]]], dict[str, Any]]:
    manifest = load_manifest(package_dir)
    atoms, _errors = load_atoms(package_dir)
    return manifest, atoms, atoms_by_head(atoms), score_package(package_dir)


def values(heads: dict[str, list[dict[str, Any]]], head: str, env: str | None = None) -> list[str]:
    found: list[str] = []
    for row in heads.get(head, []):
        args = row.get("args", [])
        if env is not None:
            if len(args) >= 2 and args[0] == env:
                found.append(args[1])
        elif args:
            found.append(args[-1])
    return found


def build_trm_rows(package_dir: Path) -> list[dict[str, Any]]:
    manifest, _atoms, heads, scorecard = package_context(package_dir)
    package_id = manifest.get("package_id", package_dir.name)
    base_skill = manifest.get("base_skill", "")
    envs = [str(env) for env in manifest.get("target_envs", [])] or scorecard.get("target_envs") or ["general"]
    rows: list[dict[str, Any]] = []
    for env in envs:
        common_meta = {
            "package_id": package_id,
            "base_skill": base_skill,
            "env": env,
            "source": "metta-trm-meta-skill",
            "generated_at_utc": utc_now(),
        }
        rows.extend(
            [
                {
                    "role": "author_router",
                    "state": {
                        "task_summary": values(heads, "summary", env)[:3],
                        "available_roles": TRM_ROLES,
                        "target_env": env,
                    },
                    "tools": ["author-packet", "repair-packet", "verify-packet"],
                    "action": {"route": "metta_package_authoring", "base_skill": base_skill, "target_env": env},
                    "meta": common_meta,
                },
                {
                    "role": "metta_syntax_repair",
                    "state": {
                        "allowed_heads": sorted(SUPPORTED_HEADS),
                        "constraints": values(heads, "constraint", env)[:6],
                    },
                    "tools": ["repair-packet", "verify-packet"],
                    "action": {"repair_policy": "one_top_level_supported_atom_per_line"},
                    "meta": common_meta,
                },
                {
                    "role": "semantic_contract_verifier",
                    "state": {
                        "constraints": values(heads, "constraint", env),
                        "forbids": values(heads, "forbid", env),
                        "validation_paths": values(heads, "validation-path", env),
                    },
                    "tools": ["verify-packet", "bench-arms"],
                    "action": {"verify": "contract_retrieval_repair_coverage", "min_runtime_score": 0.85},
                    "meta": common_meta,
                },
                {
                    "role": "retrieval_policy_router",
                    "state": {
                        "query_cues": values(heads, "query-cue", env),
                        "retrieval_priorities": values(heads, "retrieval-priority", env),
                    },
                    "tools": ["trm-mcp", "verify-packet"],
                    "action": {"route": "first_useful_compact_context", "optimize": "hit_quality_per_token"},
                    "meta": common_meta,
                },
                {
                    "role": "skill_patch_controller",
                    "state": {
                        "scores": scorecard["scores"],
                        "failure_modes": values(heads, "failure-mode", env),
                        "repair_hints": values(heads, "repair-hint", env),
                    },
                    "tools": ["evolve-skill", "bench-arms"],
                    "action": {"patch_category": choose_patch_category(scorecard), "require_benchmark_receipt": True},
                    "meta": common_meta,
                },
                {
                    "role": "commit_veto",
                    "state": {
                        "scores": scorecard["scores"],
                        "claim_labels": [
                            "live_model_run",
                            "deterministic_replay",
                            "post_hoc_projection",
                            "control_plane_threshold_eval",
                            "environment_design",
                            "training_corpus_plan",
                        ],
                    },
                    "tools": ["bench-arms", "evolve-skill"],
                    "action": {
                        "decision": "commit" if scorecard["scores"]["overall"] >= 0.85 else "veto_or_more_data",
                        "reason": "runtime_ready" if scorecard["scores"]["overall"] >= 0.85 else "score_below_runtime_threshold",
                    },
                    "meta": common_meta,
                },
            ]
        )
    return rows


def cmd_export_trm_rows(args: argparse.Namespace) -> int:
    rows = build_trm_rows(Path(args.package_dir))
    out = Path(args.out)
    write_jsonl(out, rows)
    print(f"{out} ({len(rows)} rows)")
    return 0


def choose_patch_category(scorecard: dict[str, Any]) -> str:
    scores = scorecard["scores"]
    if scores["syntax"] < 0.95:
        return "repair_gate_update"
    if scores["contract"] < 0.85:
        return "validator_update"
    if scores["retrieval"] < 0.85:
        return "retrieval_policy_update"
    if scores["repair"] < 0.85:
        return "repair_gate_update"
    if scores["trainer_export"] < 0.85:
        return "training_corpus_expansion"
    return "runtime_packet_injection"


def load_optional_json(path: str | None) -> Any:
    if not path:
        return None
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_json_if_exists(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def score_delta(before: dict[str, Any] | None, after: dict[str, Any] | None) -> dict[str, float]:
    before_scores = (before or {}).get("scores") or {}
    after_scores = (after or {}).get("scores") or {}
    keys = sorted(set(before_scores) | set(after_scores))
    return {key: round(float(after_scores.get(key, 0.0)) - float(before_scores.get(key, 0.0)), 4) for key in keys}


def failing_components(report: dict[str, Any] | None, threshold: float = 0.85) -> list[str]:
    scores = (report or {}).get("scores") or {}
    return [key for key, value in scores.items() if key != "overall" and float(value) < threshold]


def report_context(report_path: Path) -> dict[str, Any]:
    package_dir = report_path.parent
    task_dir = package_dir.parent
    manifest = load_json_if_exists(package_dir / "package.manifest.json") or {}
    raw_verify = load_json_if_exists(task_dir / "raw_verify.json")
    repaired_verify = load_json_if_exists(task_dir / "repaired_verify.json")
    if repaired_verify is None:
        repaired_verify = score_package(package_dir)
    package_id = (
        (repaired_verify or {}).get("package_id")
        or manifest.get("package_id")
        or task_dir.name
    )
    target_envs = (
        (repaired_verify or {}).get("target_envs")
        or manifest.get("target_envs")
        or []
    )
    return {
        "task_id": task_dir.name,
        "task_dir": str(task_dir),
        "package_dir": str(package_dir),
        "package_id": package_id,
        "base_skill": manifest.get("base_skill", ""),
        "target_envs": [str(env) for env in target_envs],
        "raw_verify": raw_verify,
        "repaired_verify": repaired_verify,
    }


def build_rows_from_repair_report(report_path: Path) -> list[dict[str, Any]]:
    report = load_json_if_exists(report_path) or {}
    repairs = report.get("repairs") or []
    context = report_context(report_path)
    raw_verify = context["raw_verify"]
    repaired_verify = context["repaired_verify"]
    delta = score_delta(raw_verify, repaired_verify)
    rows: list[dict[str, Any]] = []
    for index, repair in enumerate(repairs):
        rows.append(
            {
                "role": "metta_syntax_repair",
                "state": {
                    "raw_atom": repair.get("from", ""),
                    "source_file": repair.get("source_file", ""),
                    "line_no": repair.get("line_no"),
                    "repair_type": repair.get("repair", ""),
                    "target_envs": context["target_envs"],
                    "pre_scores": (raw_verify or {}).get("scores", {}),
                    "failing_components": failing_components(raw_verify),
                },
                "tools": ["repair-packet", "verify-packet"],
                "action": {
                    "repaired_atom": repair.get("to", ""),
                    "repair": repair.get("repair", ""),
                    "accept_repair": True,
                },
                "meta": {
                    "source": "repair_report",
                    "report_path": str(report_path),
                    "repair_index": index,
                    "package_id": context["package_id"],
                    "task_id": context["task_id"],
                    "base_skill": context["base_skill"],
                    "score_delta": delta,
                    "generated_at_utc": utc_now(),
                },
            }
        )
    rows.append(
        {
            "role": "semantic_contract_verifier",
            "state": {
                "raw_scores": (raw_verify or {}).get("scores", {}),
                "repaired_scores": (repaired_verify or {}).get("scores", {}),
                "raw_missing_files": (raw_verify or {}).get("missing_files", []),
                "raw_manifest_missing": (raw_verify or {}).get("manifest_missing", []),
                "raw_error_count": (raw_verify or {}).get("error_count", 0),
                "repair_count": len(repairs),
            },
            "tools": ["verify-packet", "repair-packet"],
            "action": {
                "verdict": "runtime_ready" if (repaired_verify or {}).get("ready_for_runtime_without_review") else "needs_more_repair",
                "score_delta": delta,
                "failing_components_after_repair": failing_components(repaired_verify),
            },
            "meta": {
                "source": "raw_repaired_verify_pair",
                "report_path": str(report_path),
                "package_id": context["package_id"],
                "task_id": context["task_id"],
                "base_skill": context["base_skill"],
                "generated_at_utc": utc_now(),
            },
        }
    )
    rows.append(
        {
            "role": "commit_veto",
            "state": {
                "raw_ready_for_runtime": bool((raw_verify or {}).get("ready_for_runtime_without_review")),
                "repaired_ready_for_runtime": bool((repaired_verify or {}).get("ready_for_runtime_without_review")),
                "raw_overall": ((raw_verify or {}).get("scores") or {}).get("overall", 0.0),
                "repaired_overall": ((repaired_verify or {}).get("scores") or {}).get("overall", 0.0),
                "repair_count": len(repairs),
            },
            "tools": ["verify-packet", "export-trm-rows"],
            "action": {
                "decision": "commit_repaired_package" if (repaired_verify or {}).get("ready_for_runtime_without_review") else "veto_or_collect_more_data",
                "reason": "repaired_runtime_ready" if (repaired_verify or {}).get("ready_for_runtime_without_review") else "repair_not_runtime_ready",
            },
            "meta": {
                "source": "raw_repaired_commit_veto_pair",
                "report_path": str(report_path),
                "package_id": context["package_id"],
                "task_id": context["task_id"],
                "base_skill": context["base_skill"],
                "score_delta": delta,
                "generated_at_utc": utc_now(),
            },
        }
    )
    return rows


def trm_row_to_messages(row: dict[str, Any], system_prompt: str) -> dict[str, Any]:
    action = dict(row.get("action") or {})
    prompt_payload = {
        "role": row.get("role", ""),
        "state": row.get("state", {}),
        "tools": row.get("tools", []),
        "output_contract": {
            "format": "direct_json_action_object",
            "required_keys": sorted(action),
            "forbid": ["tool_call_wrapper", "action_params_wrapper", "hidden_reasoning"],
        },
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(prompt_payload, ensure_ascii=False, sort_keys=True)},
        {"role": "assistant", "content": json.dumps(action, ensure_ascii=False, sort_keys=True)},
    ]
    meta = dict(row.get("meta") or {})
    meta.update(
        {
            "source_format": "metta_trm_meta_repair_row",
            "role": row.get("role", ""),
        }
    )
    return {"messages": messages, "meta": meta}


def build_messages_rows(rows: list[dict[str, Any]], system_prompt: str) -> list[dict[str, Any]]:
    return [trm_row_to_messages(row, system_prompt) for row in rows]


def iter_repair_reports(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]
    if not input_path.exists():
        raise SystemExit(f"missing input path: {input_path}")
    reports = sorted(path for path in input_path.rglob("repair_report.json") if path.is_file())
    if not reports:
        raise SystemExit(f"no repair_report.json files found under: {input_path}")
    return reports


def cmd_export_repair_training_rows(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    reports = iter_repair_reports(input_path)
    rows: list[dict[str, Any]] = []
    for report_path in reports:
        rows.extend(build_rows_from_repair_report(report_path))
    out = Path(args.out)
    write_jsonl(out, rows)
    messages_count = 0
    if args.messages_out:
        messages = build_messages_rows(rows, args.system_prompt)
        messages_count = write_jsonl(Path(args.messages_out), messages)
    role_counts: dict[str, int] = {}
    repair_type_counts: dict[str, int] = {}
    for row in rows:
        role_counts[row["role"]] = role_counts.get(row["role"], 0) + 1
        if row["role"] == "metta_syntax_repair":
            repair_type = str(row["action"].get("repair", ""))
            repair_type_counts[repair_type] = repair_type_counts.get(repair_type, 0) + 1
    manifest = {
        "generated_at_utc": utc_now(),
        "input": str(input_path),
        "out": str(out),
        "report_count": len(reports),
        "row_count": len(rows),
        "messages_out": str(Path(args.messages_out)) if args.messages_out else "",
        "messages_count": messages_count,
        "system_prompt": args.system_prompt if args.messages_out else "",
        "role_counts": role_counts,
        "repair_type_counts": repair_type_counts,
        "reports": [str(path) for path in reports],
    }
    if args.manifest:
        write_json(Path(args.manifest), manifest)
    print(f"{out} ({len(rows)} rows from {len(reports)} reports)")
    return 0


def render_evolution_md(plan: dict[str, Any]) -> str:
    lines = [
        "# MeTTa TRM Meta-Skill Evolution Plan",
        "",
        f"- Package: `{plan['package_id']}`",
        f"- Patch category: `{plan['patch_category']}`",
        f"- Claim label: `{plan['claim_label']}`",
        f"- Overall score: `{plan['scores']['overall']}`",
        "",
        "## Actions",
        "",
    ]
    for action in plan["actions"]:
        lines.append(f"- {action}")
    lines.extend(["", "## Rollback", "", f"- {plan['rollback_condition']}"])
    return "\n".join(lines)


def cmd_evolve_skill(args: argparse.Namespace) -> int:
    package_dir = Path(args.package_dir)
    scorecard = load_optional_json(args.verify_report) or score_package(package_dir)
    bench = load_optional_json(args.bench_json)
    patch_category = choose_patch_category(scorecard)
    actions_by_category = {
        "repair_gate_update": [
            "add or tighten deterministic repair hints in failure_modes.metta",
            "export fresh metta_syntax_repair and commit_veto rows",
            "rerun verify-packet before runtime use",
        ],
        "validator_update": [
            "add explicit constraints, forbids, minimal examples, and validation paths",
            "export semantic_contract_verifier rows",
            "rerun fixed-anchor benchmark arms before patching the source skill",
        ],
        "retrieval_policy_update": [
            "add narrower query-cue atoms and ordered retrieval-priority atoms",
            "export retrieval_policy_router rows",
            "measure first-useful-hit token cost before and after the change",
        ],
        "training_corpus_expansion": [
            "collect failure and near-miss traces with source metadata",
            "split rows by TRM role and held-out env family",
            "run pure-trm-trainer with fixed anchors before updating runtime gates",
        ],
        "runtime_packet_injection": [
            "compile the package through metta-trm-hermes-pipeline",
            "inject only the compact runtime packet into the target skill",
            "record benchmark arm receipts and claim label with the skill patch",
        ],
    }
    plan = {
        "generated_at_utc": utc_now(),
        "package_dir": str(package_dir),
        "package_id": scorecard.get("package_id", package_dir.name),
        "scores": scorecard["scores"],
        "patch_category": patch_category,
        "actions": actions_by_category.get(patch_category, ["collect more data before patching"]),
        "benchmark_input": bench,
        "claim_label": args.claim_label,
        "expected_metric_movement": "improve control-plane exactness, token efficiency, or no-harm commit/veto rate",
        "rollback_condition": "revert the skill patch if fixed-anchor score, first-useful-hit rate, or commit/veto no-harm rate regresses",
    }
    out_dir = Path(args.out_dir)
    write_json(out_dir / "skill_evolution_plan.json", plan)
    write_text(out_dir / "skill_evolution_plan.md", render_evolution_md(plan))
    print(out_dir)
    return 0


def cmd_bench_arms(args: argparse.Namespace) -> int:
    package_dir = Path(args.package_dir)
    scorecard = score_package(package_dir)
    metrics = load_optional_json(args.metrics_json)
    arms = [
        {
            "arm": "baseline",
            "description": "target skill without TRM or MeTTa runtime packet",
            "required_receipt": "raw model or deterministic baseline scorecard",
        },
        {
            "arm": "pure_trm",
            "description": "role TRMs active without MeTTa runtime packet",
            "required_receipt": "Pure-TRM-Trainer summary or deterministic TRM replay",
        },
        {
            "arm": "metta_runtime",
            "description": "compiled MeTTa runtime packet active without repair gate",
            "required_receipt": "runtime packet manifest plus benchmark scorecard",
        },
        {
            "arm": "metta_runtime_repair",
            "description": "compiled MeTTa runtime packet plus repair and commit/veto gates",
            "required_receipt": "repair report plus fixed-anchor benchmark scorecard",
        },
    ]
    plan = {
        "generated_at_utc": utc_now(),
        "package_id": scorecard.get("package_id", package_dir.name),
        "scorecard": scorecard,
        "claim_boundary": args.claim_label,
        "metrics_input": metrics,
        "arms": arms,
        "acceptance_rule": "claim improvement only when metta_runtime_repair beats baseline and pure_trm on fixed anchors without a no-harm regression",
    }
    write_json(Path(args.out), plan)
    print(args.out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Orchestrate MeTTa authoring, repair, verification, TRM export, and skill evolution.")
    sub = parser.add_subparsers(dest="command", required=True)

    author = sub.add_parser("author-packet", help="Create a bounded MeTTa package from a task description.")
    author.add_argument("--task")
    author.add_argument("--task-file")
    author.add_argument("--base-skill", required=True)
    author.add_argument("--target-env", action="append")
    author.add_argument("--package-id")
    author.add_argument("--title")
    author.add_argument("--claim-label", default="training_corpus_plan")
    author.add_argument("--out-dir", required=True)
    author.set_defaults(func=cmd_author_packet)

    repair = sub.add_parser("repair-packet", help="Copy and syntax-repair a MeTTa package into a new directory.")
    repair.add_argument("--package-dir", required=True)
    repair.add_argument("--out-dir", required=True)
    repair.set_defaults(func=cmd_repair_packet)

    verify = sub.add_parser("verify-packet", help="Score a MeTTa package for runtime and TRM-row readiness.")
    verify.add_argument("--package-dir", required=True)
    verify.add_argument("--out")
    verify.add_argument("--min-score", type=float, default=0.0)
    verify.set_defaults(func=cmd_verify_packet)

    export = sub.add_parser("export-trm-rows", help="Export role-specific Pure-TRM-Trainer JSONL rows.")
    export.add_argument("--package-dir", required=True)
    export.add_argument("--out", required=True)
    export.set_defaults(func=cmd_export_trm_rows)

    repair_export = sub.add_parser("export-repair-training-rows", help="Export TRM rows from repair_report.json plus raw/repaired verifier scorecards.")
    repair_export.add_argument("--input", required=True, help="A repair_report.json, package directory, task directory, or run root.")
    repair_export.add_argument("--out", required=True)
    repair_export.add_argument("--manifest")
    repair_export.add_argument("--messages-out", help="Optional Pure-TRM/QLoRA messages JSONL built from the exported rows.")
    repair_export.add_argument(
        "--system-prompt",
        default="You are a MeTTa/TRM control-plane model. Emit the direct JSON action object only. Do not wrap it in action/params. Do not output hidden reasoning.",
    )
    repair_export.set_defaults(func=cmd_export_repair_training_rows)

    evolve = sub.add_parser("evolve-skill", help="Generate a bounded skill evolution plan from verification and benchmark evidence.")
    evolve.add_argument("--package-dir", required=True)
    evolve.add_argument("--verify-report")
    evolve.add_argument("--bench-json")
    evolve.add_argument("--claim-label", default="training_corpus_plan")
    evolve.add_argument("--out-dir", required=True)
    evolve.set_defaults(func=cmd_evolve_skill)

    bench = sub.add_parser("bench-arms", help="Emit the benchmark arm contract for a MeTTa/TRM meta-skill package.")
    bench.add_argument("--package-dir", required=True)
    bench.add_argument("--metrics-json")
    bench.add_argument("--claim-label", default="training_corpus_plan")
    bench.add_argument("--out", required=True)
    bench.set_defaults(func=cmd_bench_arms)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
