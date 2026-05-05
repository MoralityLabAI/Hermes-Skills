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


def repair_line(line: str) -> tuple[str, dict[str, Any] | None]:
    stripped = line.strip()
    if not stripped or stripped.startswith(";"):
        return line, None
    parsed = parse_atom_line(stripped)
    if parsed and parsed.get("ok"):
        return stripped, None
    candidate = stripped
    if not candidate.startswith("("):
        candidate = "(" + candidate
    if not candidate.endswith(")"):
        candidate = candidate + ")"
    repaired = parse_atom_line(candidate)
    if repaired and repaired.get("ok"):
        return candidate, {"from": stripped, "to": candidate, "repair": "wrapped_single_atom"}
    return stripped, {"from": stripped, "to": stripped, "repair": "unrepaired", "error": (parsed or repaired or {}).get("error")}


def cmd_repair_packet(args: argparse.Namespace) -> int:
    package_dir = Path(args.package_dir)
    out_dir = Path(args.out_dir)
    if not package_dir.exists():
        raise SystemExit(f"missing package dir: {package_dir}")
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
            repaired, report = repair_line(line)
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
    envs = [str(env) for env in manifest.get("target_envs", [])] or [row["args"][0] for row in heads.get("env", []) if row["args"]]

    total_lines = len(atoms) + len(errors)
    syntax = 1.0 if total_lines and not errors else (len(atoms) / total_lines if total_lines else 0.0)
    manifest_score = 1.0 if not manifest_missing else max(0.0, 1.0 - (len(manifest_missing) / len(REQUIRED_MANIFEST_FIELDS)))

    contract_checks = [
        bool(heads.get("goal")),
        bool(heads.get("answer-shape")),
        bool(heads.get("summary")),
        bool(heads.get("constraint")),
        bool(heads.get("forbid")),
        bool(heads.get("minimal-example")),
        bool(heads.get("validation-path")),
    ]
    retrieval_checks = [bool(heads.get("query-cue")), bool(heads.get("retrieval-priority"))]
    repair_checks = [bool(heads.get("failure-mode")), bool(heads.get("repair-hint")), bool(heads.get("trace-label"))]
    trainer_checks = [
        syntax >= 0.95,
        manifest_score >= 0.85,
        all(contract_checks[:4]),
        all(retrieval_checks),
        all(repair_checks),
        bool(envs),
    ]

    scores = {
        "syntax": round(syntax, 4),
        "manifest": round(manifest_score, 4),
        "contract": round(sum(contract_checks) / len(contract_checks), 4),
        "retrieval": round(sum(retrieval_checks) / len(retrieval_checks), 4),
        "repair": round(sum(repair_checks) / len(repair_checks), 4),
        "trainer_export": round(sum(1 for ok in trainer_checks if ok) / len(trainer_checks), 4),
    }
    overall = sum(scores[key] for key in ["syntax", "contract", "retrieval", "repair", "trainer_export"]) / 5
    return {
        "generated_at_utc": utc_now(),
        "package_dir": str(package_dir),
        "package_id": manifest.get("package_id", ""),
        "target_envs": envs,
        "scores": {**scores, "overall": round(overall, 4)},
        "manifest_missing": manifest_missing,
        "atom_count": len(atoms),
        "error_count": len(errors),
        "errors": errors[:50],
        "ready_for_training_rows": overall >= 0.7,
        "ready_for_runtime_without_review": overall >= 0.85 and not errors,
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
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
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

