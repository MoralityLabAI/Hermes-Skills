from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _parse_mc_report(text: str) -> Dict[str, Any]:
    endings: Dict[str, float] = {}
    secrets: Dict[str, float] = {}
    dead_end_rate = 0.0
    section = ""
    unreachable: List[str] = []
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
        elif section == "--- Secret Reachability ---" and line.startswith("page_secret_"):
            match = re.match(r"^(page_secret_[^\s]+)\s+\d+\s+\(\s*([0-9.]+)%\)", line)
            if match:
                secrets[match.group(1)] = float(match.group(2))
        elif section == "--- Unreachable Endings ---" and line.startswith("page_"):
            unreachable.append(line)
        elif line.startswith("Dead-end rate:"):
            try:
                dead_end_rate = float(line.split("(")[1].split("%")[0])
            except Exception:
                dead_end_rate = 0.0
    return {
        "ending_pct": endings,
        "secret_pct": secrets,
        "dead_end_rate_pct": dead_end_rate,
        "unreachable_endings": unreachable,
    }


def _load_quality(path: Path | None) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _classify_endings(mc: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    ending_pct = dict(mc.get("ending_pct", {}))
    if not ending_pct:
        return [], []
    target_share = 100.0 / max(1, len(ending_pct))
    boost: List[Dict[str, Any]] = []
    suppress: List[Dict[str, Any]] = []
    for ending_id, pct in sorted(ending_pct.items()):
        gap = round(target_share - float(pct), 3)
        row = {
            "ending_id": ending_id,
            "actual_share_pct": round(float(pct), 3),
            "target_share_pct": round(target_share, 3),
            "gap_pct": gap,
            "kind": "secret" if ending_id.startswith("page_secret_") else "ending",
        }
        if gap > 1.5:
            boost.append(row)
        elif gap < -1.5:
            suppress.append(row)
    boost.sort(key=lambda row: (-row["gap_pct"], row["ending_id"]))
    suppress.sort(key=lambda row: (row["gap_pct"], row["ending_id"]))
    return boost, suppress


def _quality_check_map(quality: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in quality.get("checks", []):
        if isinstance(row, dict) and "name" in row:
            out[str(row["name"])] = row
    return out


def _build_priority_fixes(mc: Dict[str, Any], quality: Dict[str, Any], boost: List[Dict[str, Any]]) -> List[str]:
    fixes: List[str] = []
    dead_end = float(mc.get("dead_end_rate_pct", 0.0))
    if dead_end > 0.0:
        fixes.append(f"Reduce dead-end rate from {dead_end:.2f}% by adding safe continuation routes and loosening brittle visibility gates.")
    if mc.get("unreachable_endings"):
        fixes.append("Restore reachability for currently unreachable endings before any text-only polish.")
    for row in boost[:3]:
        fixes.append(f"Increase reachability for {row['ending_id']} by about {row['gap_pct']:.2f} percentage points without collapsing neighboring routes.")
    failures = [str(name) for name in quality.get("failures", [])]
    check_map = _quality_check_map(quality)
    if "super_secret_reachability" in failures:
        fixes.append("Raise super-secret route viability and avoid edits that make hidden endings rarer.")
    if "ending_reachability_balance" in failures:
        fixes.append("Rebalance ending exposure to reduce share skew across terminal routes.")
    if "secret_reachability_balance" in failures:
        fixes.append("Even out secret-route access instead of concentrating all hidden traffic in one route.")
    if "option_visibility_complexity" in failures:
        fixes.append("Increase visibility-script complexity in the affected encounters instead of relying on flat always-on options.")
    if "desirability_operator_dominance" in failures or "effect_operator_dominance" in failures:
        fixes.append("Diversify dominant operators to reduce monoculture in desirability/effect scripts.")
    super_secret = check_map.get("super_secret_reachability")
    if super_secret and not bool(super_secret.get("pass", True)):
        fixes.append(
            f"Push super-secret reachability above {float(super_secret.get('target', 0.0)):.2f}; current value is {float(super_secret.get('actual', 0.0)):.2f}."
        )
    return fixes


def _build_focus_metrics(mc: Dict[str, Any], quality: Dict[str, Any], boost: List[Dict[str, Any]], suppress: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    focus: List[Dict[str, Any]] = [
        {
            "name": "dead_end_rate_pct",
            "actual": round(float(mc.get("dead_end_rate_pct", 0.0)), 3),
            "target_max": 0.0,
            "direction": "decrease",
        }
    ]
    for row in boost[:3]:
        focus.append(
            {
                "name": f"reachability_boost::{row['ending_id']}",
                "actual": row["actual_share_pct"],
                "target_min": row["target_share_pct"],
                "direction": "increase",
            }
        )
    for row in suppress[:2]:
        focus.append(
            {
                "name": f"reachability_trim::{row['ending_id']}",
                "actual": row["actual_share_pct"],
                "target_max": row["target_share_pct"],
                "direction": "decrease",
            }
        )
    for row in quality.get("checks", []):
        if not isinstance(row, dict) or bool(row.get("pass", True)):
            continue
        focus.append(
            {
                "name": str(row.get("name", "unknown")),
                "actual": row.get("actual"),
                "target": row.get("target"),
                "direction": "fix",
            }
        )
    return focus


def _build_recommendations(mc: Dict[str, Any], quality: Dict[str, Any], boost: List[Dict[str, Any]], suppress: List[Dict[str, Any]]) -> List[str]:
    recs: List[str] = []
    if boost:
        recs.append("Prioritize underrepresented endings first; do not spend context on already overrepresented routes.")
    if suppress:
        trimmed = ", ".join(row["ending_id"] for row in suppress[:3])
        recs.append(f"Reduce accidental funneling into overrepresented routes: {trimmed}.")
    if quality.get("failures"):
        recs.append("Treat failing quality checks as hard rebalance constraints during planning and audit phases.")
    if float(mc.get("dead_end_rate_pct", 0.0)) > 0.0:
        recs.append("Favor edits that preserve continuation safety over stylistic flourishes.")
    recs.append("Use reasoning phases to identify route and stat adjustments; keep final world edits localized and validator-safe.")
    return recs


def _build_phase_guidance(priority_fixes: List[str], boost: List[Dict[str, Any]], suppress: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    boost_ids = [row["ending_id"] for row in boost[:3]]
    suppress_ids = [row["ending_id"] for row in suppress[:2]]
    return {
        "plan": [
            "Translate Monte Carlo skew into concrete local edit targets.",
            f"Boost these endings where possible: {', '.join(boost_ids) if boost_ids else 'none'}.",
            f"Avoid further strengthening these routes: {', '.join(suppress_ids) if suppress_ids else 'none'}.",
        ],
        "characterize": [
            "Call out route bottlenecks, gating pressure, and stat funnels that explain the observed Monte Carlo skew.",
            "Identify which voices or choices are collapsing distinct routes into the same outcome.",
        ],
        "act_complete": [
            "Audit whether current act transitions create route funnels, dead ends, or runaway variable dynamics.",
            "Surface continuity risks that would make rebalance edits unstable.",
        ],
        "recharacterize": [
            "Re-express character and option tension so the targeted routes become narratively legible without breaking invariants.",
            "Keep rebalance fixes compatible with the world's causal logic.",
        ],
        "encounter_build": [
            "When authoring is enabled, make only local edits that support the priority fixes and preserve stable ORX ids.",
        ],
        "late_stage_holistic": [
            "Use end-state polish only to reinforce validated rebalance moves, not to invent new route structure.",
        ],
        "priority_fixes": priority_fixes[:6],
    }


def build_advice(mc_path: Path, quality_path: Path | None, storyworld_label: str) -> Dict[str, Any]:
    mc = _parse_mc_report(mc_path.read_text(encoding="utf-8"))
    quality = _load_quality(quality_path)
    boost, suppress = _classify_endings(mc)
    priority_fixes = _build_priority_fixes(mc, quality, boost)
    focus_metrics = _build_focus_metrics(mc, quality, boost, suppress)
    recommendations = _build_recommendations(mc, quality, boost, suppress)
    phase_guidance = _build_phase_guidance(priority_fixes, boost, suppress)
    notes = [
        f"Monte Carlo source: {mc_path}",
        f"Quality gate source: {quality_path}" if quality_path else "Quality gate source: none",
        f"Dead-end rate: {float(mc.get('dead_end_rate_pct', 0.0)):.2f}%",
    ]
    if mc.get("unreachable_endings"):
        notes.append(f"Unreachable endings: {', '.join(mc['unreachable_endings'])}")
    return {
        "storyworld": {
            "label": storyworld_label,
            "mc_report": str(mc_path),
            "quality_report": str(quality_path) if quality_path else "",
            "mode": "monte_carlo_rebalance",
        },
        "focus_metrics": focus_metrics,
        "target_endings": {
            "boost": boost,
            "suppress": suppress,
            "unreachable": list(mc.get("unreachable_endings", [])),
        },
        "priority_fixes": priority_fixes,
        "recommendations": recommendations,
        "phase_guidance": phase_guidance,
        "quality_failures": [str(x) for x in quality.get("failures", [])],
        "recommended_overrides": {
            "repair_build_output": True,
            "reasoning_preferred_phases": ["plan", "characterize", "act_complete", "recharacterize"],
            "authoring_guarded_phases": ["encounter_build", "late_stage_holistic"],
        },
        "notes": notes,
        "raw_metrics": {
            "dead_end_rate_pct": round(float(mc.get("dead_end_rate_pct", 0.0)), 3),
            "ending_pct": mc.get("ending_pct", {}),
            "secret_pct": mc.get("secret_pct", {}),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a TRM advice packet from Monte Carlo and quality-gate artifacts.")
    parser.add_argument("--mc-report", required=True)
    parser.add_argument("--quality-report", default="")
    parser.add_argument("--storyworld-label", default="storyworld")
    parser.add_argument("--out-advice", required=True)
    args = parser.parse_args()

    mc_path = Path(args.mc_report).resolve()
    quality_path = Path(args.quality_report).resolve() if args.quality_report else None
    payload = build_advice(mc_path, quality_path, args.storyworld_label)
    out_path = Path(args.out_advice).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
