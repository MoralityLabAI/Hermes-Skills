#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Sequence


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = json.loads(json.dumps(base))
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def resolve_path(base_dir: Path, raw: str) -> str:
    path = Path(raw)
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return str(path)


def maybe_resolve_config_paths(config_dir: Path, cfg: Dict[str, Any]) -> Dict[str, Any]:
    for key in (
        "artifact_root",
        "template_root",
        "trainer_script",
        "base_trainer_config",
        "output_dir",
        "corpus_spec",
        "scorecard_path",
        "evaluator_script",
    ):
        raw = str(cfg.get(key, "") or "")
        if raw:
            cfg[key] = resolve_path(config_dir, raw)
    return cfg


def score_value(scorecard: Dict[str, Any], primary: str, fallback: str = "") -> float:
    for key in (primary, fallback):
        if key and key in scorecard:
            try:
                return float(scorecard[key])
            except (TypeError, ValueError):
                continue
    return 0.0


def load_scorecard(path: Path | None) -> Dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return read_json(path)


def format_duration(seconds: float | None) -> str:
    if seconds is None or seconds < 0:
        return "estimating"
    total = int(round(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_progress_bar(completed: int, total: int, width: int = 18) -> str:
    if total <= 0:
        return "[" + ("-" * width) + "]"
    filled = max(0, min(width, int(round((completed / total) * width))))
    return "[" + ("#" * filled) + ("-" * (width - filled)) + "]"


def normalize_ram_budget(raw: Any) -> str:
    if raw in (None, "", 0, 0.0):
        return "auto"
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return str(raw)
    if value.is_integer():
        return f"{int(value)} GB"
    return f"{value:.1f} GB"


def clip_text(value: Any, limit: int) -> str:
    text = str(value)
    if len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3] + "..."


def render_status_card(snapshot: Dict[str, Any]) -> str:
    width = 76
    border = "+" + "-" * (width - 2) + "+"
    current_metrics = clip_text(
        f"anchor={snapshot['current_anchor']:.4f} train={snapshot['current_train']:.4f} gap={snapshot['current_gap']:.4f}",
        56,
    )
    best_metrics = clip_text(
        f"anchor={snapshot['best_anchor']:.4f} train={snapshot['best_train']:.4f} gap={snapshot['best_gap']:.4f}",
        56,
    )
    lines = [
        border,
        f"| Hermes TRM Run: {clip_text(snapshot['run_id'], 56):<56}|",
        f"| phase   : {clip_text(snapshot['phase'], 56):<56}|",
        f"| step    : {clip_text(snapshot['step'], 56):<56}|",
        f"| source  : {clip_text(snapshot['data_source'], 56):<56}|",
        f"| RAM     : {clip_text(snapshot['ram_budget'], 56):<56}|",
        f"| ETA     : {clip_text(snapshot['eta'], 56):<56}|",
        f"| done    : {snapshot['progress_bar']} {snapshot['percent_complete']:>6.1f}%{'':<34}|",
        f"| current : {current_metrics:<56}|",
        f"| best    : {best_metrics:<56}|",
        border,
    ]
    return "\n".join(lines)


def write_progress_snapshot(path: Path, snapshot: Dict[str, Any]) -> None:
    dump_json(path, snapshot)


def write_default_scorecard(path: Path, trainer_run_dir: Path, summary_path: Path | None = None) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    if summary_path is not None and summary_path.exists():
        summary = read_json(summary_path)
    payload = {
        "train_score": float(summary.get("train_score", summary.get("env_score", 0.0)) or 0.0),
        "anchor_score": float(summary.get("anchor_score", summary.get("judge_score", 0.0)) or 0.0),
        "failure_rate": float(summary.get("failure_rate", 0.0) or 0.0),
        "recovery_rate": float(summary.get("recovery_rate", 0.0) or 0.0),
        "generalization_gap": float(summary.get("generalization_gap", 0.0) or 0.0),
        "source": "summary_fallback",
        "trainer_run_dir": str(trainer_run_dir),
        "summary_path": str(summary_path) if summary_path is not None else "",
    }
    if payload["generalization_gap"] <= 0.0:
        payload["generalization_gap"] = max(0.0, payload["train_score"] - payload["anchor_score"])
    dump_json(path, payload)
    return payload


def run_command(command: Sequence[str], workdir: Path, stdout_path: Path, stderr_path: Path) -> int:
    with stdout_path.open("w", encoding="utf-8", newline="\n") as out_handle, stderr_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as err_handle:
        proc = subprocess.run(list(command), cwd=str(workdir), stdout=out_handle, stderr=err_handle, text=True, check=False)
    return int(proc.returncode)


def build_candidate_config(
    base_config: Dict[str, Any],
    candidate: Dict[str, Any],
    candidate_dir: Path,
    source_config_path: Path,
) -> Dict[str, Any]:
    cfg = json.loads(json.dumps(base_config))
    cfg["run_id"] = str(candidate["run_id"])
    cfg["artifact_root"] = str(candidate_dir.parent)
    cfg["output_dir"] = str(candidate_dir / "trainer_outputs")
    cfg["corpus_spec"] = str(source_config_path)
    trainer_overrides = merge_dict(dict(cfg.get("trainer_overrides", {})), dict(candidate.get("trainer_overrides", {})))
    cfg["trainer_overrides"] = trainer_overrides
    cfg["search_meta"] = {
        "rung": candidate["rung"],
        "candidate_index": candidate["candidate_index"],
        "generalization_level": candidate["generalization_level"],
        "mutation": candidate.get("mutation", {}),
        "anchor_set": candidate.get("anchor_set", {}),
    }
    return cfg


def render_command(template: Sequence[str], values: Dict[str, str]) -> List[str]:
    rendered: List[str] = []
    for item in template:
        for key, val in values.items():
            item = item.replace("{" + key + "}", val)
        rendered.append(item)
    return rendered


def default_ladder() -> List[Dict[str, Any]]:
    return [
        {"generalization_level": 0, "label": "in_domain"},
        {"generalization_level": 1, "label": "light_generalization"},
        {"generalization_level": 2, "label": "cross_run"},
        {"generalization_level": 3, "label": "cross_env_family"},
        {"generalization_level": 4, "label": "broad_generalization"},
        {"generalization_level": 5, "label": "hardest_setting"},
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a TRM hill-climb loop over generalization levels.")
    parser.add_argument("--config", required=True, help="JSON search spec path.")
    parser.add_argument("--run-id", default="", help="Optional run id override.")
    parser.add_argument("--dry-run", action="store_true", help="Write candidate manifests but do not launch trainer or evaluator.")
    return parser.parse_args()


def build_status_snapshot(
    *,
    run_id: str,
    phase: str,
    step: str,
    data_source: str,
    ram_budget: Any,
    completed_count: int,
    total_candidates: int,
    start_time: float,
    completed_durations: List[float],
    current_result: Dict[str, Any] | None,
    best: Dict[str, Any] | None,
) -> Dict[str, Any]:
    elapsed = time.time() - start_time
    eta_seconds = None
    if completed_durations and total_candidates > completed_count:
        avg = sum(completed_durations) / len(completed_durations)
        eta_seconds = avg * (total_candidates - completed_count)
    current_anchor = score_value(current_result or {}, "anchor_score", "judge_score")
    current_train = score_value(current_result or {}, "train_score", "env_score")
    current_gap = score_value(current_result or {}, "generalization_gap")
    if not current_gap and current_result:
        current_gap = max(0.0, current_train - current_anchor)
    best_anchor = score_value(best or {}, "anchor_score", "judge_score")
    best_train = score_value(best or {}, "train_score", "env_score")
    best_gap = score_value(best or {}, "generalization_gap")
    if not best_gap and best:
        best_gap = max(0.0, best_train - best_anchor)
    return {
        "run_id": run_id,
        "phase": phase,
        "step": step,
        "data_source": data_source,
        "ram_budget": normalize_ram_budget(ram_budget),
        "elapsed": format_duration(elapsed),
        "eta": format_duration(eta_seconds),
        "percent_complete": (completed_count / total_candidates * 100.0) if total_candidates else 0.0,
        "progress_bar": format_progress_bar(completed_count, total_candidates),
        "current_anchor": current_anchor,
        "current_train": current_train,
        "current_gap": current_gap,
        "best_anchor": best_anchor,
        "best_train": best_train,
        "best_gap": best_gap,
        "completed_count": completed_count,
        "total_candidates": total_candidates,
    }


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config_dir = config_path.parent
    config = maybe_resolve_config_paths(config_dir, read_json(config_path))

    run_id = str(args.run_id or config.get("run_id") or f"trm_hillclimb_{int(time.time())}")
    artifact_root = ensure_dir(Path(config["artifact_root"]).resolve())
    run_dir = ensure_dir(artifact_root / run_id)
    ledger_path = run_dir / "hillclimb_ledger.jsonl"
    dump_json(run_dir / "run_config.snapshot.json", config)

    corpus_spec = Path(config["corpus_spec"]).resolve()
    ladder = list(config.get("generalization_ladder") or default_ladder())
    mutation_templates = list(config.get("mutations") or [{}])
    anchor_set = dict(config.get("anchor_set", {}))
    evaluation_command = list(config.get("evaluation_command") or [])
    evaluator_script = Path(config.get("evaluator_script") or "").resolve() if config.get("evaluator_script") else None
    scorecard_relpath = str(config.get("scorecard_relpath") or "scorecard.json")
    plateau_patience = int(config.get("plateau_patience", 2) or 2)
    maximize_key = str(config.get("maximize_key") or "anchor_score")
    min_gap = float(config.get("max_generalization_gap", 0.0) or 0.0)
    data_source = str(config.get("data_source") or Path(corpus_spec).name)
    total_candidates = len(ladder) * max(1, len(mutation_templates))
    run_started = time.time()
    completed_durations: List[float] = []
    progress_path = run_dir / "progress.snapshot.json"

    if args.dry_run:
        template_root = Path(config.get("template_root") or config_dir).resolve()
        trainer_script = Path(config.get("trainer_script") or (template_root / "run_trainer.ps1")).resolve()
        base_cfg: Dict[str, Any] = {}
    else:
        template_root = Path(config["template_root"]).resolve()
        trainer_script = Path(config.get("trainer_script") or (template_root / "run_trainer.ps1")).resolve()
        base_trainer_config = Path(config.get("base_trainer_config") or (template_root / "trainer_config_safe.json")).resolve()
        base_cfg = read_json(base_trainer_config)

    search_base = merge_dict(base_cfg, dict(config.get("trainer_overrides", {})))
    memory_budget = (
        config.get("memory_budget_gb")
        or os.environ.get("TRM_MEMORY_GB")
        or search_base.get("train", {}).get("memory_gb")
        or search_base.get("runtime", {}).get("memory_gb")
    )

    best: Dict[str, Any] | None = None
    plateau = 0
    candidate_index = 0
    initial_status = build_status_snapshot(
        run_id=run_id,
        phase="planning",
        step="queued",
        data_source=data_source,
        ram_budget=memory_budget,
        completed_count=0,
        total_candidates=total_candidates,
        start_time=run_started,
        completed_durations=completed_durations,
        current_result=None,
        best=None,
    )
    write_progress_snapshot(progress_path, initial_status)
    print(render_status_card(initial_status), flush=True)
    for rung_index, rung in enumerate(ladder):
        for mutation in mutation_templates:
            candidate_index += 1
            candidate = {
                "candidate_index": candidate_index,
                "rung": rung.get("label", f"rung_{rung_index}"),
                "generalization_level": int(rung.get("generalization_level", rung_index)),
                "mutation": mutation,
                "anchor_set": anchor_set,
                "run_id": f"{run_id}_r{rung_index:02d}_{candidate_index:03d}",
                "trainer_overrides": {
                    "train": {
                        "max_examples": int(mutation.get("max_examples", 0) or 0),
                        "batch_size": int(mutation.get("batch_size", search_base.get("train", {}).get("batch_size", 8)) or 8),
                        "epochs": int(mutation.get("epochs", search_base.get("train", {}).get("epochs", 1)) or 1),
                        "lr": float(mutation.get("lr", search_base.get("train", {}).get("lr", 0.0002)) or 0.0002),
                    }
                },
            }
            candidate_dir = ensure_dir(run_dir / "candidates" / f"{rung_index:02d}_{candidate_index:03d}")
            candidate_config = build_candidate_config(search_base, candidate, candidate_dir, corpus_spec)
            candidate_config["trainer_overrides"]["search"] = {
                "generalization_level": candidate["generalization_level"],
                "rung": candidate["rung"],
                "anchor_set": anchor_set,
            }
            candidate_config_path = candidate_dir / "search_config.json"
            dump_json(candidate_config_path, candidate_config)

            hermes_cmd = [
                sys.executable,
                str(Path(__file__).resolve().parent / "run_trm_trainer_hermes.py"),
                "--config",
                str(candidate_config_path),
                "--run-id",
                candidate["run_id"],
            ]
            command_record = {
                "candidate": candidate,
                "hermes_command": hermes_cmd,
                "evaluation_command": evaluation_command,
                "created_at": now_iso(),
            }
            dump_json(candidate_dir / "command.json", command_record)
            append_jsonl(ledger_path, {"event": "candidate_planned", **command_record})
            planned_status = build_status_snapshot(
                run_id=run_id,
                phase="launching",
                step=f"candidate {candidate_index}/{total_candidates}",
                data_source=data_source,
                ram_budget=memory_budget,
                completed_count=candidate_index - 1,
                total_candidates=total_candidates,
                start_time=run_started,
                completed_durations=completed_durations,
                current_result=None,
                best=best,
            )
            write_progress_snapshot(progress_path, planned_status)
            print(render_status_card(planned_status), flush=True)

            if args.dry_run:
                continue

            candidate_started_at = time.time()
            hermes_stdout = candidate_dir / "hermes.stdout.log"
            hermes_stderr = candidate_dir / "hermes.stderr.log"
            hermes_rc = run_command(hermes_cmd, template_root, hermes_stdout, hermes_stderr)
            hermes_status = "completed" if hermes_rc == 0 else "failed"
            dump_json(candidate_dir / "hermes.status.json", {"status": hermes_status, "returncode": hermes_rc, "at": now_iso()})
            append_jsonl(ledger_path, {"event": "candidate_hermes_finished", "status": hermes_status, "returncode": hermes_rc, "candidate_index": candidate_index})
            hermes_finished_status = build_status_snapshot(
                run_id=run_id,
                phase="hermes_finished",
                step=f"candidate {candidate_index}/{total_candidates}",
                data_source=data_source,
                ram_budget=memory_budget,
                completed_count=candidate_index - 1,
                total_candidates=total_candidates,
                start_time=run_started,
                completed_durations=completed_durations,
                current_result=None,
                best=best,
            )
            write_progress_snapshot(progress_path, hermes_finished_status)
            print(render_status_card(hermes_finished_status), flush=True)
            if hermes_rc != 0:
                continue

            trainer_run_dir = Path(candidate_config["output_dir"]).resolve() / candidate["run_id"]
            scorecard_path = trainer_run_dir / scorecard_relpath
            if evaluation_command:
                eval_cmd = render_command(
                    evaluation_command,
                    {
                        "run_dir": str(run_dir),
                        "candidate_dir": str(candidate_dir),
                        "trainer_run_dir": str(trainer_run_dir),
                        "trainer_summary": str(trainer_run_dir / "summary.json"),
                        "candidate_config": str(candidate_config_path),
                        "run_id": candidate["run_id"],
                        "rung": candidate["rung"],
                        "candidate_index": str(candidate_index),
                        "scorecard": str(scorecard_path),
                        "python": sys.executable,
                    },
                )
                eval_stdout = candidate_dir / "evaluation.stdout.log"
                eval_stderr = candidate_dir / "evaluation.stderr.log"
                eval_rc = run_command(eval_cmd, template_root, eval_stdout, eval_stderr)
                dump_json(candidate_dir / "evaluation.status.json", {"status": "completed" if eval_rc == 0 else "failed", "returncode": eval_rc, "at": now_iso()})
                append_jsonl(ledger_path, {"event": "candidate_evaluated", "returncode": eval_rc, "candidate_index": candidate_index})
            elif evaluator_script is not None:
                eval_cmd = [
                    sys.executable,
                    str(evaluator_script),
                    "--trainer-run-dir",
                    str(trainer_run_dir),
                    "--scorecard-path",
                    str(scorecard_path),
                ]
                eval_stdout = candidate_dir / "evaluation.stdout.log"
                eval_stderr = candidate_dir / "evaluation.stderr.log"
                eval_rc = run_command(eval_cmd, template_root, eval_stdout, eval_stderr)
                dump_json(candidate_dir / "evaluation.status.json", {"status": "completed" if eval_rc == 0 else "failed", "returncode": eval_rc, "at": now_iso()})
                append_jsonl(ledger_path, {"event": "candidate_evaluated", "returncode": eval_rc, "candidate_index": candidate_index, "mode": "evaluator_script"})

            scorecard = load_scorecard(scorecard_path)
            if not scorecard:
                scorecard = load_scorecard(candidate_dir / scorecard_relpath)
            if not scorecard:
                scorecard = write_default_scorecard(scorecard_path, trainer_run_dir, trainer_run_dir / "summary.json")

            train_score = score_value(scorecard, "train_score", "env_score")
            anchor_score = score_value(scorecard, "anchor_score", "judge_score")
            failure_rate = score_value(scorecard, "failure_rate")
            recovery_rate = score_value(scorecard, "recovery_rate")
            generalization_gap = score_value(scorecard, "generalization_gap")
            if not generalization_gap:
                generalization_gap = max(0.0, train_score - anchor_score)

            result = {
                "candidate_index": candidate_index,
                "run_id": candidate["run_id"],
                "rung": candidate["rung"],
                "generalization_level": candidate["generalization_level"],
                "train_score": train_score,
                "anchor_score": anchor_score,
                "failure_rate": failure_rate,
                "recovery_rate": recovery_rate,
                "generalization_gap": generalization_gap,
                "scorecard": scorecard,
                "trainer_run_dir": str(trainer_run_dir),
            }
            completed_durations.append(time.time() - candidate_started_at)
            dump_json(candidate_dir / "result.json", result)
            append_jsonl(ledger_path, {"event": "candidate_scored", **result})
            scored_status = build_status_snapshot(
                run_id=run_id,
                phase="scored",
                step=f"candidate {candidate_index}/{total_candidates}",
                data_source=data_source,
                ram_budget=memory_budget,
                completed_count=candidate_index,
                total_candidates=total_candidates,
                start_time=run_started,
                completed_durations=completed_durations,
                current_result=result,
                best=best or result,
            )
            write_progress_snapshot(progress_path, scored_status)
            print(render_status_card(scored_status), flush=True)

            if best is None:
                best = result
                plateau = 0
            else:
                current = float(result.get(maximize_key, 0.0) or 0.0)
                best_value = float(best.get(maximize_key, 0.0) or 0.0)
                better = current > best_value or (current == best_value and float(result["generalization_gap"]) <= float(best.get("generalization_gap", 0.0)))
                if current >= best_value - min_gap and better:
                    best = result
                    plateau = 0
                else:
                    plateau += 1
            if plateau >= plateau_patience:
                append_jsonl(ledger_path, {"event": "search_stopped", "reason": "plateau", "plateau": plateau, "at": now_iso()})
                break
        if plateau >= plateau_patience:
            break

    final = {
        "run_id": run_id,
        "run_dir": str(run_dir),
        "artifact_root": str(artifact_root),
        "best": best or {},
        "ledger": str(ledger_path),
        "evaluation_command": evaluation_command,
        "plateau_patience": plateau_patience,
        "maximize_key": maximize_key,
        "memory_budget_gb": memory_budget,
        "data_source": data_source,
    }
    dump_json(run_dir / "summary.json", final)
    final_status = build_status_snapshot(
        run_id=run_id,
        phase="complete",
        step=f"candidate {candidate_index}/{total_candidates}",
        data_source=data_source,
        ram_budget=memory_budget,
        completed_count=min(candidate_index, total_candidates),
        total_candidates=total_candidates,
        start_time=run_started,
        completed_durations=completed_durations,
        current_result=best,
        best=best,
    )
    write_progress_snapshot(progress_path, final_status)
    print(render_status_card(final_status), flush=True)
    print(str(run_dir))
    print(str(run_dir / "summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
