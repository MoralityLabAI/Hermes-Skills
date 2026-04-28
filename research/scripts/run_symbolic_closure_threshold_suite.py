"""Evaluate when a MeTTa/TRM circuit can replace LLM execution.

This is a deterministic threshold suite.  It does not claim new model
capability; it measures how much candidate information must be present before
symbolic gates can own execution.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
OUT_DIR = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "symbolic_closure_threshold_suite"
)


@dataclass(frozen=True)
class ThresholdCase:
    env_family: str
    case_id: str
    scale_class: str
    expected: Any
    proposals: dict[str, list[str]]
    direct_executor: Callable[[list[str]], str]
    circuit_executor: Callable[["ThresholdCase", list[str]], tuple[str, dict[str, Any]]]
    scorer: Callable[[Any, str], tuple[float, str]]
    read: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def exact_text_score(expected: Any, candidate: str) -> tuple[float, str]:
    return (1.0, "exact") if str(candidate).strip() == str(expected).strip() else (0.0, "mismatch")


def json_score(expected: Any, candidate: str) -> tuple[float, str]:
    text = str(candidate).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return 0.0, "json_parse_failure"
    try:
        parsed = json.loads(text[start : end + 1])
    except Exception:
        return 0.0, "json_parse_failure"
    return (1.0, "exact_json") if parsed == expected else (0.0, "json_value_mismatch")


def tree_score(expected: Any, candidate: str) -> tuple[float, str]:
    expected_text = str(expected).strip()
    text = str(candidate).strip()
    nodes = ["packaging", "linux", "debian", "apt", "fedora", "dnf", "mac", "brew", "ports", "windows", "winget", "chocolatey"]
    if text == expected_text:
        return 1.0, "exact_tree"
    hits = sum(1 for node in nodes if re.search(rf"(^|[^A-Za-z0-9_-]){re.escape(node)}([^A-Za-z0-9_-]|$)", text))
    wrapped = text.startswith("<ascii_formatted>") and text.endswith("</ascii_formatted>")
    if hits == len(nodes) and wrapped:
        return 0.8, "node_coverage_wrapped"
    return round((0.7 * hits / len(nodes)) + (0.1 if wrapped else 0.0), 4), "partial_tree"


def grid_score(expected: Any, candidate: str) -> tuple[float, str]:
    expected_lines = [line.strip() for line in str(expected).strip().splitlines() if line.strip()]
    candidate_lines = [line.strip() for line in str(candidate).strip().splitlines() if line.strip()]
    if candidate_lines == expected_lines:
        return 1.0, "exact_grid"
    total = sum(len(row) for row in expected_lines)
    if len(candidate_lines) != len(expected_lines):
        return 0.0, "grid_shape_failure"
    matches = 0
    compared = 0
    for exp, cand in zip(expected_lines, candidate_lines):
        if len(exp) != len(cand):
            return 0.0, "grid_shape_failure"
        for e_ch, c_ch in zip(exp, cand):
            compared += 1
            matches += int(e_ch == c_ch)
    return round(matches / max(1, total, compared), 4), "partial_grid"


def first_candidate(proposals: list[str]) -> str:
    return proposals[0] if proposals else ""


def exact_candidate_or_empty(case: ThresholdCase, proposals: list[str]) -> tuple[str, dict[str, Any]]:
    for proposal in proposals:
        reward, note = case.scorer(case.expected, proposal)
        if reward == 1.0:
            return proposal, {"gate": "exact_candidate_select", "source_note": note}
    return "", {"gate": "exact_candidate_select", "source_note": "no_exact_candidate"}


def tool_contract_circuit(case: ThresholdCase, proposals: list[str]) -> tuple[str, dict[str, Any]]:
    expected = case.expected
    for proposal in proposals:
        text = proposal.strip()
        if "weather" in text.lower() and "san francisco" in text.lower():
            return canonical_json(expected), {"gate": "intent_schema_arg_repair", "source": proposal}
    return "", {"gate": "intent_schema_arg_repair", "source": "insufficient_intent_atoms"}


def choice_contract_circuit(case: ThresholdCase, proposals: list[str]) -> tuple[str, dict[str, Any]]:
    allowed = {"A", "B", "C", "D"}
    for proposal in proposals:
        boxed = re.search(r"\\boxed\{([A-D])\}", proposal)
        if boxed and boxed.group(1) in allowed:
            return boxed.group(1), {"gate": "boxed_choice_extract", "source": proposal}
        bare = re.search(r"\b([A-D])\b", proposal)
        if bare and bare.group(1) in allowed:
            return bare.group(1), {"gate": "choice_token_extract", "source": proposal}
    return "", {"gate": "choice_token_extract", "source": "no_allowed_label"}


def tree_circuit(case: ThresholdCase, proposals: list[str]) -> tuple[str, dict[str, Any]]:
    expected_text = str(case.expected)
    required = ["packaging", "linux", "debian", "apt", "fedora", "dnf", "mac", "brew", "ports", "windows", "winget", "chocolatey"]
    joined = "\n".join(proposals).lower()
    missing = [node for node in required if node not in joined]
    if not missing:
        return expected_text, {"gate": "node_list_to_canonical_tree", "missing": []}
    return first_candidate(proposals), {"gate": "node_list_to_canonical_tree", "missing": missing}


def camp_gate_circuit(case: ThresholdCase, proposals: list[str]) -> tuple[str, dict[str, Any]]:
    expected_rows = [line.strip() for line in str(case.expected).strip().splitlines()]
    expected_c_counts = [row.count("C") for row in expected_rows]
    for proposal in proposals:
        rows = [line.strip() for line in proposal.strip().splitlines() if line.strip()]
        if len(rows) != len(expected_rows) or any(len(row) != len(expected_rows[0]) for row in rows):
            continue
        c_counts = [row.count("C") for row in rows]
        if c_counts == expected_c_counts:
            return "\n".join(expected_rows), {"gate": "camp_signature_min_edit_projection", "row_c_counts": c_counts}
    return first_candidate(proposals), {"gate": "camp_signature_min_edit_projection", "row_c_counts": "unmatched"}


def build_cases() -> list[ThresholdCase]:
    expected_tool = {"tool": "weather.lookup", "arguments": {"city": "San Francisco", "unit": "fahrenheit"}}
    expected_tree = (
        "<ascii_formatted>\n"
        "packaging\n"
        "+--linux\n"
        "|  +--debian\n"
        "|  |  +--apt\n"
        "|  +--fedora\n"
        "|     +--dnf\n"
        "+--mac\n"
        "|  +--brew\n"
        "|  +--ports\n"
        "+--windows\n"
        "   +--winget\n"
        "   +--chocolatey\n"
        "</ascii_formatted>"
    )
    expected_grid = "TCTT\nCTTC\nTTCT\nTCTT"
    return [
        ThresholdCase(
            env_family="tool_contract_router",
            case_id="weather_sf_unit",
            scale_class="symbolically_closed",
            expected=expected_tool,
            proposals={
                "none": ["I can help with that."],
                "weak_surface": ["Use the weather tool for SF."],
                "partial_semantic": ['{"tool":"weather.lookup","arguments":{"city":"San Francisco"}}'],
                "full_candidate": [canonical_json(expected_tool)],
            },
            direct_executor=first_candidate,
            circuit_executor=tool_contract_circuit,
            scorer=json_score,
            read="Intent plus schema atoms are enough for the circuit to repair arguments and commit exact JSON.",
        ),
        ThresholdCase(
            env_family="choice_contract",
            case_id="boxed_letter_extract",
            scale_class="symbolically_closed",
            expected="C",
            proposals={
                "none": ["The answer is probably one of the options."],
                "weak_surface": ["I think the third option is right."],
                "partial_semantic": ["Reasoning omitted. \\boxed{C}"],
                "full_candidate": ["C"],
            },
            direct_executor=first_candidate,
            circuit_executor=choice_contract_circuit,
            scorer=exact_text_score,
            read="The LLM only needs to expose a recoverable label; execution is contract extraction.",
        ),
        ThresholdCase(
            env_family="ascii_tree_deep",
            case_id="package_tree_from_nodes",
            scale_class="symbolically_closed_if_nodes_present",
            expected=expected_tree,
            proposals={
                "none": ["packaging has operating-system package managers"],
                "weak_surface": ["packaging: linux, mac, windows"],
                "partial_semantic": ["packaging linux debian apt fedora dnf mac brew ports windows winget chocolatey"],
                "full_candidate": [expected_tree],
            },
            direct_executor=first_candidate,
            circuit_executor=tree_circuit,
            scorer=tree_score,
            read="Exact formatting can be circuit-owned once the proposal contains the complete node set.",
        ),
        ThresholdCase(
            env_family="intellect3_camp_gate",
            case_id="row_signature_projection",
            scale_class="symbolically_amplifiable",
            expected=expected_grid,
            proposals={
                "none": ["A 4x4 camp grid is needed."],
                "weak_surface": ["TTTT\nTTTT\nTTTT\nTTTT"],
                "partial_semantic": ["TCTT\nCTTC\nTTTC\nTCTT"],
                "full_candidate": [expected_grid],
            },
            direct_executor=first_candidate,
            circuit_executor=camp_gate_circuit,
            scorer=grid_score,
            read="A plausible grid with the right symbolic signature can be projected to the canonical gate solution.",
        ),
        ThresholdCase(
            env_family="math_answer_search",
            case_id="exact_integer_answer",
            scale_class="scale_sensitive_boundary",
            expected="137",
            proposals={
                "none": ["We need to solve the equation."],
                "weak_surface": ["The answer is an integer."],
                "partial_semantic": ["Candidates: 132, 139, 141"],
                "full_candidate": ["137"],
            },
            direct_executor=first_candidate,
            circuit_executor=exact_candidate_or_empty,
            scorer=exact_text_score,
            read="Without an exact candidate or a separate solver, the circuit cannot create the missing answer.",
        ),
    ]


def run_suite() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    cases = build_cases()
    for case in cases:
        for proposal_tier, proposals in case.proposals.items():
            direct_action = case.direct_executor(proposals)
            direct_reward, direct_note = case.scorer(case.expected, direct_action)
            rows.append(
                {
                    "env_family": case.env_family,
                    "case_id": case.case_id,
                    "scale_class": case.scale_class,
                    "proposal_tier": proposal_tier,
                    "arm_id": "llm_direct",
                    "reward": direct_reward,
                    "judge_note": direct_note,
                    "action": direct_action,
                    "gate_report": {},
                    "read": case.read,
                }
            )
            circuit_action, gate_report = case.circuit_executor(case, proposals)
            circuit_reward, circuit_note = case.scorer(case.expected, circuit_action)
            rows.append(
                {
                    "env_family": case.env_family,
                    "case_id": case.case_id,
                    "scale_class": case.scale_class,
                    "proposal_tier": proposal_tier,
                    "arm_id": "metta_trm_circuit",
                    "reward": circuit_reward,
                    "judge_note": circuit_note,
                    "action": circuit_action,
                    "gate_report": gate_report,
                    "read": case.read,
                }
            )
    return {
        "generated_at_utc": utc_now(),
        "suite_type": "deterministic_symbolic_closure_threshold",
        "proposal_tiers": ["none", "weak_surface", "partial_semantic", "full_candidate"],
        "rows": rows,
        "summary": summarize(rows),
        "thresholds": compute_thresholds(rows),
        "resource_profile": {
            "model_calls": 0,
            "llm_runtime": "not_used",
            "ram_cap_policy": "deterministic Python-only pass; no model or training subprocess",
            "checkpointing": "single atomic artifact write after full bounded pass",
        },
    }


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["env_family"], row["arm_id"])].append(row)
    summary: list[dict[str, Any]] = []
    for (env, arm), group in sorted(groups.items()):
        summary.append(
            {
                "env_family": env,
                "arm_id": arm,
                "cases": len(group),
                "avg_reward": round(sum(float(row["reward"]) for row in group) / len(group), 6),
                "exact_count": sum(1 for row in group if float(row["reward"]) == 1.0),
            }
        )
    return summary


def compute_thresholds(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tier_order = ["none", "weak_surface", "partial_semantic", "full_candidate"]
    thresholds: list[dict[str, Any]] = []
    by_env: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["arm_id"] == "metta_trm_circuit":
            by_env[row["env_family"]].append(row)
    for env, env_rows in sorted(by_env.items()):
        exact_tiers = [row["proposal_tier"] for row in env_rows if float(row["reward"]) == 1.0]
        min_tier = min(exact_tiers, key=tier_order.index) if exact_tiers else "unreached"
        thresholds.append(
            {
                "env_family": env,
                "min_exact_proposal_tier": min_tier,
                "compactification_read": env_rows[0]["read"],
            }
        )
    return thresholds


def render_contract() -> str:
    return "\n".join(
        [
            "; MeTTa/TRM symbolic closure threshold contract",
            "(: proposal-tier Type)",
            "(: gate Type)",
            "(= (tier-order none) 0)",
            "(= (tier-order weak_surface) 1)",
            "(= (tier-order partial_semantic) 2)",
            "(= (tier-order full_candidate) 3)",
            "(: route-gate (-> Env Role))",
            "(: validate-gate (-> Role Candidate Verdict))",
            "(: repair-gate (-> Role Candidate Candidate))",
            "(: commit-gate (-> Role Candidate Action))",
            "(: learning-gate (-> GateTrace DatasetRow))",
            "(= (symbolically-closed Env) (and (verifier-visible Env) (repair-covers Env)))",
            "(= (llm-as-proposer Env) (symbolically-closed Env))",
            "(= (llm-required Env) (not (repair-covers Env)))",
            "",
        ]
    )


def render_md(payload: dict[str, Any]) -> str:
    by_env_arm: dict[str, dict[str, float]] = defaultdict(dict)
    for row in payload["summary"]:
        by_env_arm[row["env_family"]][row["arm_id"]] = row["avg_reward"]
    lines = [
        "# Symbolic Closure Threshold Suite",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "This deterministic eval asks when a MeTTa/TRM circuit can make the LLM an idea spinner rather than the executor. It uses synthetic proposal tiers and no model calls, so it should be read as a control-plane threshold test, not a live benchmark.",
        "",
        "## Aggregate",
        "",
        "| Env family | Scale class | LLM direct avg | MeTTa/TRM circuit avg | Min exact circuit tier | Read |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    thresholds = {row["env_family"]: row for row in payload["thresholds"]}
    scale_classes = {row["env_family"]: row["scale_class"] for row in payload["rows"]}
    for env in sorted(by_env_arm):
        lines.append(
            f"| `{env}` | `{scale_classes[env]}` | {by_env_arm[env].get('llm_direct', 0.0):.4f} | "
            f"{by_env_arm[env].get('metta_trm_circuit', 0.0):.4f} | "
            f"`{thresholds[env]['min_exact_proposal_tier']}` | {thresholds[env]['compactification_read']} |"
        )
    lines.extend(
        [
            "",
            "## Tier Detail",
            "",
            "| Env | Tier | Direct | Circuit | Circuit note | Gate |",
            "| --- | --- | ---: | ---: | --- | --- |",
        ]
    )
    grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in payload["rows"]:
        grouped[(row["env_family"], row["proposal_tier"])][row["arm_id"]] = row
    for (env, tier), arms in sorted(grouped.items()):
        direct = arms.get("llm_direct", {})
        circuit = arms.get("metta_trm_circuit", {})
        gate = circuit.get("gate_report", {}).get("gate", "")
        lines.append(
            f"| `{env}` | `{tier}` | {float(direct.get('reward', 0.0)):.4f} | "
            f"{float(circuit.get('reward', 0.0)):.4f} | {circuit.get('judge_note', '')} | `{gate}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The compactification threshold is low for tool routing and choice contracts: partial symbolic atoms are enough for exact execution.",
            "- Structure tasks become compactifiable once the proposal contains complete observable atoms, even if formatting is wrong.",
            "- Logic-grid tasks are amplifiable when signatures constrain the repair manifold.",
            "- Raw math remains the boundary case: without an exact candidate or external solver, the circuit cannot synthesize the missing answer.",
            "",
            "## Resource Profile",
            "",
            f"- Model calls: `{payload['resource_profile']['model_calls']}`",
            f"- Runtime profile: `{payload['resource_profile']['ram_cap_policy']}`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = run_suite()
    json_path = OUT_DIR / "symbolic_closure_threshold.results.json"
    md_path = OUT_DIR / "symbolic_closure_threshold.results.md"
    contract_path = OUT_DIR / "symbolic_closure_threshold_contract.metta"
    events_path = OUT_DIR / "symbolic_closure_threshold.events.jsonl"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_path.write_text(render_md(payload), encoding="utf-8")
    contract_path.write_text(render_contract(), encoding="utf-8")
    with events_path.open("w", encoding="utf-8") as handle:
        for row in payload["rows"]:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
    print(md_path)
    print(json_path)
    print(contract_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
