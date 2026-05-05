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
BOOTSTRAP = SCRIPT_DIR / "run_small_model_bootstrap_bench.py"

DOMAIN_SPECS: dict[str, dict[str, Any]] = {
    "formal_reasoning": {
        "label": "formal reasoning",
        "modes": ["proof", "symbolic_search", "counterexample", "invariant_check"],
        "keywords": ["theorem", "proof", "logic", "invariant", "contradiction", "symbolic", "math", "graph"],
        "focus": "proof objects, invariants, candidate search, contradiction repair",
    },
    "empirical_science": {
        "label": "empirical science",
        "modes": ["hypothesis", "experiment", "measurement", "ablation"],
        "keywords": ["experiment", "measurement", "ablation", "hypothesis", "lab", "causal", "instrument", "dataset"],
        "focus": "hypotheses, measurements, ablations, evidence quality",
    },
    "systems_engineering": {
        "label": "systems engineering",
        "modes": ["architecture", "interface", "control_loop", "reliability"],
        "keywords": ["architecture", "interface", "latency", "reliability", "scheduler", "pipeline", "integration", "control loop"],
        "focus": "interfaces, failure budgets, control loops, integration gates",
    },
    "biosocial_ecology": {
        "label": "biosocial ecology",
        "modes": ["agent_ecology", "adaptation", "selection_pressure", "emergence"],
        "keywords": ["alife", "ecology", "ecosystem", "adaptation", "agents", "population", "morphology", "selection"],
        "focus": "agent interactions, adaptation, complexity, ecological failure modes",
    },
    "social_governance": {
        "label": "social governance",
        "modes": ["institutional_analysis", "incentive_modeling", "coalition_forecast", "legitimacy_check"],
        "keywords": ["law", "policy", "coalition", "diplomacy", "institution", "incentive", "governance", "legitimacy"],
        "focus": "institutions, incentives, coalitions, legitimacy constraints",
    },
    "humanities_interpretive": {
        "label": "humanities interpretation",
        "modes": ["hermeneutics", "historical_context", "motif_analysis", "argument_mapping"],
        "keywords": ["text", "history", "theology", "philosophy", "motif", "kalam", "mutazili", "interpret"],
        "focus": "meaning, historical context, concepts, motifs, argument structure",
    },
    "creative_narrative": {
        "label": "creative narrative",
        "modes": ["character_model", "theme_tracking", "encounter_dag", "secret_pathing"],
        "keywords": ["storyworld", "character", "encounter", "secret ending", "narrative", "motif", "player", "choice"],
        "focus": "characters, themes, encounter DAGs, secret path balance",
    },
    "safety_security": {
        "label": "safety and security",
        "modes": ["threat_model", "anomaly_detection", "containment", "escalation_gate"],
        "keywords": ["tamper", "security", "red-team", "anomaly", "containment", "exploit", "probe", "drift"],
        "focus": "threat models, anomalies, containment, escalation gates",
    },
    "tool_operations": {
        "label": "tool operations",
        "modes": ["tool_contract", "json_schema", "repo_navigation", "safe_execution"],
        "keywords": ["tool", "json", "repo", "shell", "file lookup", "search", "api", "contract"],
        "focus": "tool contracts, schema validation, repo navigation, safe execution",
    },
    "metacognition_learning": {
        "label": "metacognition and learning",
        "modes": ["curriculum", "self_evaluation", "memory_retrieval", "skill_patch"],
        "keywords": ["curriculum", "skill", "training", "learn", "memory", "feedback", "benchmark", "self-improve"],
        "focus": "curricula, feedback loops, memory, verifier-guided skill repair",
    },
}

PROMPT_CASES: list[dict[str, str]] = [
    {
        "case_id": "graph_invariant_router",
        "expected_domain": "formal_reasoning",
        "prompt": "Build a verifier for graph transformation invariants that catches contradiction traces and repairs candidate proofs.",
    },
    {
        "case_id": "wetlab_ablation_router",
        "expected_domain": "empirical_science",
        "prompt": "Design an ablation study and measurement plan for a wet lab hypothesis with noisy instrument readings.",
    },
    {
        "case_id": "latency_pipeline_router",
        "expected_domain": "systems_engineering",
        "prompt": "Specialize a skill for pipeline reliability, latency budgets, interface contracts, and scheduler rollback gates.",
    },
    {
        "case_id": "alife_ecology_router",
        "expected_domain": "biosocial_ecology",
        "prompt": "Model an ALife ecosystem where agents adapt, morphology diversity rises, and novelty collapse must be detected.",
    },
    {
        "case_id": "diplomacy_institution_router",
        "expected_domain": "social_governance",
        "prompt": "Forecast coalition behavior in a diplomacy setting using institutions, incentives, legitimacy, and defection risks.",
    },
    {
        "case_id": "kalam_argument_router",
        "expected_domain": "humanities_interpretive",
        "prompt": "Organize Mutazili Kalam arguments and historical theological concepts into exam questions and interpretation cues.",
    },
    {
        "case_id": "storyworld_secret_router",
        "expected_domain": "creative_narrative",
        "prompt": "Balance a storyworld encounter DAG with characters, motifs, choice effects, and a hidden secret ending path.",
    },
    {
        "case_id": "bluebeam_security_router",
        "expected_domain": "safety_security",
        "prompt": "Create a tamper-sensing red-team evaluation with anomaly probes, drift thresholds, and containment escalation.",
    },
    {
        "case_id": "json_tool_router",
        "expected_domain": "tool_operations",
        "prompt": "Route repo search, shell-safe planning, file lookup, and JSON tool-call contracts without invalid arguments.",
    },
    {
        "case_id": "skill_curriculum_router",
        "expected_domain": "metacognition_learning",
        "prompt": "Build a feedback curriculum that lets a skill learn from benchmark failures, memory retrieval, and verifier repairs.",
    },
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def keyword_score(prompt: str, spec: dict[str, Any]) -> int:
    text = normalize(prompt)
    score = 0
    for keyword in spec["keywords"]:
        key = normalize(str(keyword))
        if " " in key:
            score += 3 if key in text else 0
        else:
            score += len(re.findall(rf"\b{re.escape(key)}\b", text))
    return score


def heuristic_route(prompt: str) -> dict[str, Any]:
    scores = {domain_id: keyword_score(prompt, spec) for domain_id, spec in DOMAIN_SPECS.items()}
    best = max(scores, key=lambda key: (scores[key], key))
    best_score = scores[best]
    total = sum(scores.values()) or 1
    spec = DOMAIN_SPECS[best]
    return {
        "domain_id": best,
        "confidence": round(best_score / total, 4) if best_score else 0.1,
        "cognitive_modes": spec["modes"][:3],
        "task_focus": spec["focus"],
        "routing_reason": f"keyword_score={best_score}",
        "router_mode": "heuristic",
        "scoreboard": scores,
    }


def domain_table() -> str:
    rows = []
    for domain_id, spec in DOMAIN_SPECS.items():
        rows.append(f"- {domain_id}: {spec['label']}; modes={', '.join(spec['modes'])}; focus={spec['focus']}")
    return "\n".join(rows)


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object found")
    payload = json.loads(stripped[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("router response is not an object")
    return payload


def post_chat(endpoint: str, model: str, messages: list[dict[str, str]], timeout: float) -> str:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 240,
        "stream": False,
    }
    req = urllib.request.Request(
        endpoint.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        parsed = json.loads(response.read().decode("utf-8", errors="replace"))
    choices = parsed.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    return str(message.get("content") or choices[0].get("text") or "")


def llm_route(prompt: str, endpoint: str, model: str, timeout: float) -> dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": "Route the user prompt to one broad domain. Return JSON only.",
        },
        {
            "role": "user",
            "content": (
                "DOMAINS:\n"
                f"{domain_table()}\n\n"
                "Return keys: domain_id, confidence, cognitive_modes, task_focus, routing_reason.\n"
                f"Prompt: {prompt}"
            ),
        },
    ]
    content = post_chat(endpoint, model, messages, timeout)
    payload = extract_json_object(content)
    domain_id = str(payload.get("domain_id") or "")
    if domain_id not in DOMAIN_SPECS:
        raise ValueError(f"unknown domain_id: {domain_id}")
    spec = DOMAIN_SPECS[domain_id]
    payload.setdefault("confidence", 0.5)
    payload.setdefault("cognitive_modes", spec["modes"][:3])
    payload.setdefault("task_focus", spec["focus"])
    payload.setdefault("routing_reason", "llm_json_router")
    payload["router_mode"] = "llm"
    return payload


def route_prompt(prompt: str, mode: str, endpoint: str, model: str, timeout: float) -> dict[str, Any]:
    if mode == "heuristic":
        return heuristic_route(prompt)
    try:
        return llm_route(prompt, endpoint, model, timeout)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
        fallback = heuristic_route(prompt)
        fallback["router_mode"] = "llm_fallback_heuristic"
        fallback["routing_error"] = f"{type(exc).__name__}: {exc}"
        return fallback


def build_task(case: dict[str, str], route: dict[str, Any], index: int) -> dict[str, str]:
    domain_id = str(route["domain_id"])
    spec = DOMAIN_SPECS[domain_id]
    modes = ", ".join(str(mode) for mode in route.get("cognitive_modes") or spec["modes"][:3])
    task_id = f"domain_router_{index:02d}_{domain_id}"
    target_env = f"domain_{domain_id}"
    return {
        "task_id": task_id,
        "base_skill": "metta-general-domain-adapter",
        "target_env": target_env,
        "task": (
            f"Bootstrap a MeTTa package for broad domain specialization, not a final task skill. "
            f"Domain: {spec['label']} ({domain_id}). Cognitive modes: {modes}. "
            f"Focus: {route.get('task_focus') or spec['focus']}. "
            f"Original prompt: {case['prompt']} "
            f"The package should encode domain-level constraints, retrieval cues, failure modes, validation paths, "
            f"repair hints, and commit/veto gates that help a small model specialize from this broad adapter."
        ),
    }


def summarize_routes(rows: list[dict[str, Any]]) -> dict[str, Any]:
    correct = [row for row in rows if row["expected_domain"] == row["route"]["domain_id"]]
    mode_counts: dict[str, int] = {}
    domain_counts: dict[str, int] = {}
    for row in rows:
        mode = str(row["route"].get("router_mode") or "unknown")
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
        domain = str(row["route"].get("domain_id") or "unknown")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "case_count": len(rows),
        "router_accuracy": round(len(correct) / len(rows), 4) if rows else 0.0,
        "router_mode_counts": mode_counts,
        "routed_domain_counts": domain_counts,
    }


def load_cases(path: str | None) -> list[dict[str, str]]:
    if not path:
        return PROMPT_CASES
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise SystemExit("--cases-json must contain a list")
    return payload


def run_bootstrap(tasks_path: Path, out_dir: Path, args: argparse.Namespace) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BOOTSTRAP),
            "--tasks-json",
            str(tasks_path),
            "--out-dir",
            str(out_dir),
            "--prompt-mode",
            "compact",
            "--generation-mode",
            "staged",
            "--stage-max-tokens",
            str(args.stage_max_tokens),
            "--timeout",
            str(args.timeout),
            "--endpoint",
            args.endpoint,
            "--model",
            args.model,
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Route broad cognition/domain prompts into MeTTa bootstrap tasks and optionally run the small-model bootstrap harness.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--cases-json")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--router-mode", choices=["heuristic", "llm"], default="heuristic")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8084")
    parser.add_argument("--model", default="Qwen3.5-4B.Q4_K_M.gguf")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--stage-max-tokens", type=int, default=520)
    parser.add_argument("--run-bootstrap", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.out_dir) / f"domain_router_bootstrap_{utc_stamp()}"
    root.mkdir(parents=True, exist_ok=True)
    cases = load_cases(args.cases_json)
    if args.limit:
        cases = cases[: args.limit]

    rows: list[dict[str, Any]] = []
    tasks: list[dict[str, str]] = []
    for index, case in enumerate(cases, 1):
        route = route_prompt(case["prompt"], args.router_mode, args.endpoint, args.model, args.timeout)
        rows.append(
            {
                "case_id": case["case_id"],
                "prompt": case["prompt"],
                "expected_domain": case["expected_domain"],
                "route": route,
            }
        )
        tasks.append(build_task(case, route, index))

    routes_path = root / "domain_routes.jsonl"
    with routes_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    tasks_path = root / "routed_tasks.json"
    tasks_path.write_text(json.dumps(tasks, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = summarize_routes(rows)
    (root / "routing_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.run_bootstrap:
        bootstrap_dir = root / "bootstrap_runs"
        started = time.time()
        proc = run_bootstrap(tasks_path, bootstrap_dir, args)
        (root / "bootstrap_process.json").write_text(
            json.dumps(
                {
                    "returncode": proc.returncode,
                    "elapsed_seconds": round(time.time() - started, 2),
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        if proc.returncode != 0:
            print(root)
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return proc.returncode

    print(root)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
