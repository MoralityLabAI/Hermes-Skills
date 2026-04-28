from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_DIR = ROOT / "research"
GENERATED_DIR = RESEARCH_DIR / "generated"
SKIP_DIRS = {"data", "scripts", "research", "__pycache__"}


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata


def classify(name: str) -> tuple[str, str, str]:
    if name == "metta-composition-hermes":
        return ("meta-skill", "metta-trm", "trm-aware-skill-composition")
    if name == "metta-eval-optimizer-hermes":
        return ("meta-skill", "metta-trm", "gate-circuit-eval-optimizer")
    if name == "trm-observability-workflow":
        return ("trm-operations", "trm", "teacher-trace-to-training-loop")
    if name == "trm-mcp":
        return ("trm-overlay", "trm", "retrieval-routing-layer")
    if name == "trm-public-rationale-chain":
        return ("trm-overlay", "trm", "bounded-public-trace-layer")
    if name.startswith("trm-"):
        return ("trm-overlay", "trm", "specialized-trm-layer")
    if name.startswith("primehub-"):
        return ("task-skill", "primehub", "candidate-for-trm-observability")
    if name.startswith("intellect3-"):
        return ("task-skill", "intellect3", "candidate-for-routing-or-observability")
    if "mechinterp" in name:
        return ("domain-research", "mechinterp", "domain-probe-surface")
    if "bluebeam" in name:
        return ("domain-research", "bluebeam", "domain-probe-surface")
    if "hermes" in name:
        return ("domain-research", "hermes", "general-hermes-research")
    return ("misc", "misc", "unclassified")


def recommended_pairings(name: str, track: str) -> list[str]:
    pairings: list[str] = []
    if name == "metta-composition-hermes":
        return ["metta-eval-optimizer-hermes", "trm-observability-workflow", "trm-mcp"]
    if name == "metta-eval-optimizer-hermes":
        return ["trm-observability-workflow", "trm-mcp"]
    if track in {"task-skill", "domain-research"}:
        pairings.append("trm-observability-workflow")
        if any(token in name for token in ("map", "lookup", "router", "tool", "mcp")):
            pairings.append("trm-mcp")
    if any(token in name for token in ("logic", "math")):
        pairings.append("trm-public-rationale-chain")
    return pairings


def primary_question(name: str, track: str, infusion_role: str) -> str:
    if name == "metta-composition-hermes":
        return "Can TRM-infused Hermes skills be safely composed into MeTTa circuits without confusing critic, formatter, verifier, and action roles?"
    if name == "metta-eval-optimizer-hermes":
        return "Can MeTTa gate circuits turn task-skill forks into better eval, curation, and TRM-training pipelines?"
    if name == "trm-mcp":
        return "Does TRM routing improve first useful MCP hit quality at lower token and call cost?"
    if name == "trm-public-rationale-chain":
        return "Does a bounded public rationale help small-model quality without violating the task contract?"
    if name == "trm-observability-workflow":
        return "Are the collected traces and row families strong enough to support training and benchmarking?"
    if name.startswith("primehub-"):
        return "Does the Hermes contract improve exactness or stability on the named Primehub slice?"
    if name.startswith("intellect3-"):
        return "Does the Hermes contract or TRM routing beat the plain path on held Intellect-3 evidence?"
    if "mechinterp" in name:
        return "What observable structure can this skill surface before a stronger benchmark contract exists?"
    if "bluebeam" in name:
        return "What domain-specific contract is stable enough to benchmark and later infuse with TRM?"
    return f"What measurable gain justifies the current {infusion_role} design?"


def next_artifact(name: str, track: str, family: str) -> tuple[str, str]:
    if name == "metta-composition-hermes":
        return (
            "TRM-aware MeTTa composition plan",
            "This skill maps existing Hermes task skills and TRM role cards into safe gate circuits with explicit claim boundaries.",
        )
    if name == "metta-eval-optimizer-hermes":
        return (
            "meta-skill fork plan plus paper addendum",
            "This layer decides which MeTTa gates, TRM exports, and PrimeLab env artifacts each new skill fork should produce.",
        )
    if track == "task-skill":
        if family == "intellect3":
            return (
                "baseline brief plus public-trace ablation",
                "The logic and math contracts are stable enough to test whether visible bounded traces help or hurt held performance.",
            )
        if name == "primehub-structured-map-hermes":
            return (
                "baseline brief plus retrieval ablation",
                "This contract is the strongest candidate for testing TRM retrieval and routing on top of observability.",
            )
        if "logic" in name:
            return (
                "baseline brief plus observability and public-trace comparison",
                "The logic slice can evaluate both teacher-trace collection and bounded rationale exposure on exact-answer tasks.",
            )
        return (
            "baseline brief plus observability pack",
            "Primehub task skills should first prove row quality, benchmark stability, and reproducible receipts before extra overlays are stacked.",
        )
    if track == "domain-research":
        return (
            "contract stabilization brief",
            "Exploratory surfaces need a fixed answer contract and benchmark slice before TRM infusion results will be comparable.",
        )
    if name == "trm-mcp":
        return (
            "overlay benchmark with lookup-heavy skills",
            "Measure first useful hit quality, tool-call count, and token cost against a plain retrieval path.",
        )
    if name == "trm-public-rationale-chain":
        return (
            "overlay benchmark with logic and math skills",
            "This layer should be justified only where public traces help without weakening the base exact-answer contract.",
        )
    if name == "trm-observability-workflow":
        return (
            "shared corpus audit",
            "The workflow itself should be evaluated as infrastructure by checking row quality, benchmark coverage, and promotion reproducibility.",
        )
    return (
        "manual review",
        "This surface does not yet match a stronger heuristic, so it needs a direct research decision.",
    )


def maturity_stage(track: str) -> str:
    if track == "meta-skill":
        return "meta-orchestration"
    if track == "task-skill":
        return "benchmarkable"
    if track == "domain-research":
        return "exploratory"
    if track == "trm-overlay":
        return "overlay"
    if track == "trm-operations":
        return "infrastructure"
    return "unclassified"


def build_entry(path: Path) -> dict[str, object] | None:
    skill_path = path / "SKILL.md"
    if not skill_path.exists():
        return None

    metadata = parse_frontmatter(skill_path)
    track, family, infusion_role = classify(path.name)
    artifact, rationale = next_artifact(path.name, track, family)
    refs_dir = path / "references"
    scripts_dir = path / "scripts"
    refs = sorted(p.name for p in refs_dir.iterdir()) if refs_dir.exists() else []
    scripts = sorted(p.name for p in scripts_dir.iterdir()) if scripts_dir.exists() else []

    return {
        "name": metadata.get("name", path.name),
        "slug": path.name,
        "description": metadata.get("description", ""),
        "track": track,
        "family": family,
        "maturity_stage": maturity_stage(track),
        "trm_infusion_role": infusion_role,
        "recommended_pairings": recommended_pairings(path.name, track),
        "primary_research_question": primary_question(path.name, track, infusion_role),
        "next_artifact": artifact,
        "next_artifact_rationale": rationale,
        "paths": {
            "root": str(path),
            "skill": str(skill_path),
            "references": str(refs_dir) if refs_dir.exists() else "",
            "scripts": str(scripts_dir) if scripts_dir.exists() else "",
        },
        "asset_counts": {
            "references": len(refs),
            "scripts": len(scripts),
        },
        "assets": {
            "references": refs,
            "scripts": scripts,
        },
    }


def build_registry() -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for child in sorted(ROOT.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir() or child.name in SKIP_DIRS:
            continue
        entry = build_entry(child)
        if entry is not None:
            entries.append(entry)
    return entries


def build_markdown(entries: list[dict[str, object]]) -> str:
    counts = Counter(entry["track"] for entry in entries)
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for entry in entries:
        grouped[str(entry["track"])].append(entry)

    lines: list[str] = []
    lines.append("# Hermes Skill Registry")
    lines.append("")
    lines.append(f"Generated from `{ROOT}`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total skills: {len(entries)}")
    for track, count in sorted(counts.items()):
        lines.append(f"- {track}: {count}")
    lines.append("")

    for track in sorted(grouped):
        lines.append(f"## {track.title()}")
        lines.append("")
        lines.append("| Skill | Family | TRM Role | Pairings | Refs | Scripts |")
        lines.append("| --- | --- | --- | --- | ---: | ---: |")
        for entry in grouped[track]:
            pairings = ", ".join(entry["recommended_pairings"]) or "-"
            lines.append(
                "| {name} | {family} | {role} | {pairings} | {refs} | {scripts} |".format(
                    name=entry["slug"],
                    family=entry["family"],
                    role=entry["trm_infusion_role"],
                    pairings=pairings,
                    refs=entry["asset_counts"]["references"],
                    scripts=entry["asset_counts"]["scripts"],
                )
            )
        lines.append("")

    lines.append("## Research Questions")
    lines.append("")
    for entry in entries:
        lines.append(f"- `{entry['slug']}`: {entry['primary_research_question']}")
    lines.append("")
    return "\n".join(lines)


def build_study_queue_markdown(entries: list[dict[str, object]]) -> str:
    track_priority = {
        "task-skill": 0,
        "domain-research": 1,
        "trm-overlay": 2,
        "trm-operations": 3,
    }
    ordered_entries = sorted(
        entries,
        key=lambda entry: (
            track_priority.get(str(entry["track"]), 99),
            str(entry["family"]),
            str(entry["slug"]),
        ),
    )

    lines: list[str] = []
    lines.append("# Hermes TRM Study Queue")
    lines.append("")
    lines.append(f"Generated from `{ROOT}`.")
    lines.append("")
    lines.append("Use this queue after the registry when deciding what to run next.")
    lines.append("")
    lines.append("| Skill | Track | Stage | Next Artifact | Pairings | Why Now |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for entry in ordered_entries:
        pairings = ", ".join(entry["recommended_pairings"]) or "-"
        lines.append(
            "| {skill} | {track} | {stage} | {artifact} | {pairings} | {why} |".format(
                skill=entry["slug"],
                track=entry["track"],
                stage=entry["maturity_stage"],
                artifact=entry["next_artifact"],
                pairings=pairings,
                why=entry["next_artifact_rationale"],
            )
        )

    lines.append("")
    lines.append("## Priorities")
    lines.append("")
    lines.append("- Start with task skills before stacking multiple TRM layers.")
    lines.append("- Use domain research surfaces to stabilize contracts, not to claim overlay wins yet.")
    lines.append("- Treat TRM overlays as experiments that need named target skills and held evidence.")
    lines.append("- Treat `trm-observability-workflow` as shared infrastructure and audit it separately from task quality.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    entries = build_registry()

    payload = {
        "workspace_root": str(ROOT),
        "skill_count": len(entries),
        "skills": entries,
    }

    json_path = GENERATED_DIR / "skill_registry.json"
    md_path = GENERATED_DIR / "skill_registry.md"
    queue_path = GENERATED_DIR / "study_queue.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(build_markdown(entries), encoding="utf-8")
    queue_path.write_text(build_study_queue_markdown(entries), encoding="utf-8")

    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {queue_path}")


if __name__ == "__main__":
    main()
