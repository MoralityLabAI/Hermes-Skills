#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def parse_mc_report(text: str) -> Dict[str, Any]:
    endings: Dict[str, float] = {}
    secrets: Dict[str, float] = {}
    dead_end_rate = None
    section = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("---"):
            section = line
            continue
        if section == "--- Ending Distribution ---" and line.startswith("page_"):
            match = re.match(r"^(page_[^\s]+)\s+\d+\s+\(\s*([0-9.]+)%\)", line)
            if match:
                endings[match.group(1)] = float(match.group(2))
        elif line.startswith("Dead-end rate:"):
            dead_end_rate = line
        elif section == "--- Secret Reachability ---" and line.startswith("page_secret_"):
            match = re.match(r"^(page_secret_[^\s]+)\s+\d+\s+\(\s*([0-9.]+)%\)", line)
            if match:
                secrets[match.group(1)] = float(match.group(2))
    return {"ending_pct": endings, "secret_pct": secrets, "dead_end_rate": dead_end_rate}


def summarize_deltas(baseline_quality: Dict[str, Any], candidate_quality: Dict[str, Any], baseline_mc: Dict[str, Any], candidate_mc: Dict[str, Any]) -> Dict[str, Any]:
    metric_names = [
        "options_per_encounter",
        "reactions_per_option",
        "effects_per_reaction",
        "desirability_vars_per_reaction",
        "visibility_gated_options_pct",
    ]
    baseline_checks = {c["name"]: c for c in baseline_quality.get("checks", [])}
    candidate_checks = {c["name"]: c for c in candidate_quality.get("checks", [])}
    metric_delta: Dict[str, float] = {}
    for name in metric_names:
        if name in baseline_checks and name in candidate_checks:
            metric_delta[name] = round(float(candidate_checks[name]["actual"]) - float(baseline_checks[name]["actual"]), 4)

    all_endings = set(baseline_mc["ending_pct"]) | set(candidate_mc["ending_pct"])
    ending_delta = {
        eid: round(candidate_mc["ending_pct"].get(eid, 0.0) - baseline_mc["ending_pct"].get(eid, 0.0), 3)
        for eid in sorted(all_endings)
    }
    all_secrets = set(baseline_mc["secret_pct"]) | set(candidate_mc["secret_pct"])
    secret_delta = {
        eid: round(candidate_mc["secret_pct"].get(eid, 0.0) - baseline_mc["secret_pct"].get(eid, 0.0), 3)
        for eid in sorted(all_secrets)
    }

    no_op = (
        candidate_quality.get("failures", []) == baseline_quality.get("failures", [])
        and all(abs(v) < 0.0001 for v in metric_delta.values())
        and all(abs(v) < 0.0001 for v in ending_delta.values())
        and all(abs(v) < 0.0001 for v in secret_delta.values())
    )

    actions: List[str] = []
    if no_op:
        actions.append("No-op loop detected: candidate metrics and ending distribution match baseline.")
        actions.append("Do not reread AGENTS or reports at length; make a concrete file edit before rerunning.")
    if candidate_quality.get("failures"):
        actions.append("Quality gate still fails; patch the topology or balance scripts before another loop.")
    if candidate_mc["ending_pct"].get("page_end_fallback", 0.0) > 0:
        actions.append("Fallback still present; inspect terminal acceptability and late-stage balance rewrites.")
    if candidate_mc["secret_pct"].get("page_secret_0299", 0.0) <= 0:
        actions.append("Super-secret route is not reachable; inspect the super-secret option gate and late-stage balance target.")
    if not actions:
        actions.append("Candidate differs from baseline; focus next edits on super-secret flavor or stronger metric-distance effects.")

    return {
        "no_op": no_op,
        "metric_delta": metric_delta,
        "ending_delta_pct": ending_delta,
        "secret_delta_pct": secret_delta,
        "baseline_failures": baseline_quality.get("failures", []),
        "candidate_failures": candidate_quality.get("failures", []),
        "actions": actions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a Macbeth loop against a baseline run.")
    parser.add_argument("--baseline-run", required=True)
    parser.add_argument("--candidate-run", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-txt", required=True)
    args = parser.parse_args()

    baseline = Path(args.baseline_run)
    candidate = Path(args.candidate_run)

    baseline_quality = load_json(baseline / "reports" / "quality_gate_overnight.json")
    candidate_quality = load_json(candidate / "reports" / "quality_gate_overnight.json")
    baseline_mc = parse_mc_report(load_text(baseline / "reports" / "monte_carlo_overnight.txt"))
    candidate_mc = parse_mc_report(load_text(candidate / "reports" / "monte_carlo_overnight.txt"))

    summary = summarize_deltas(baseline_quality, candidate_quality, baseline_mc, candidate_mc)
    summary["baseline_run"] = str(baseline)
    summary["candidate_run"] = str(candidate)

    out_json = Path(args.out_json)
    out_txt = Path(args.out_txt)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")

    lines = [
        f"baseline_run: {baseline}",
        f"candidate_run: {candidate}",
        f"no_op: {summary['no_op']}",
        "metric_delta:",
    ]
    for key, value in summary["metric_delta"].items():
        lines.append(f"  {key}: {value:+.4f}")
    lines.append("ending_delta_pct:")
    for key, value in summary["ending_delta_pct"].items():
        lines.append(f"  {key}: {value:+.3f}")
    lines.append("secret_delta_pct:")
    for key, value in summary["secret_delta_pct"].items():
        lines.append(f"  {key}: {value:+.3f}")
    lines.append("actions:")
    for action in summary["actions"]:
        lines.append(f"  - {action}")
    out_txt.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    print(out_json)
    print(out_txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
