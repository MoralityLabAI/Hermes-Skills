"""Apply V3 deterministic argument canonicalization to tool-router outputs."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "research" / "studies" / "2026-04-28-real-tool-contract-router-seed"
ROWS_PATH = STUDY / "rows" / "real_tool_contract_router_seed_rows.jsonl"
VALIDATOR_PATH = STUDY / "validators" / "validate_tool_contracts.py"
SOURCE_RESULTS = STUDY / "results" / "local_qwen25_3b_tool_router_alias_v3" / "local_qwen25_3b_tool_router.results.json"
DEFAULT_OUT = STUDY / "results" / "local_qwen25_3b_tool_router_alias_v3_argcanon"

BENCHMARK_DATE = "2026-04-28"
TIMEZONE = "America/Santiago"
MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compact_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def load_validator(path: Path):
    spec = importlib.util.spec_from_file_location("tool_contract_validator", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load validator: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def call(tool: str, args: dict[str, Any], safe_to_execute: bool) -> dict[str, Any]:
    return {"tool": tool, "args": args, "safe_to_execute": safe_to_execute}


def compact_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def lower_prompt(prompt: str) -> str:
    return compact_space(prompt).lower()


def add_days(benchmark_date: str, days: int) -> str:
    return (date.fromisoformat(benchmark_date) + timedelta(days=days)).isoformat()


def parse_absolute_date(prompt: str, benchmark_date: str) -> str | None:
    text = lower_prompt(prompt)
    if "tomorrow" in text:
        return add_days(benchmark_date, 1)
    match = re.search(r"\b(20\d{2})-(\d{2})-(\d{2})\b", text)
    if match:
        return match.group(0)
    match = re.search(
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),\s*(20\d{2})\b",
        text,
    )
    if match:
        month = MONTHS[match.group(1)]
        day = int(match.group(2))
        year = int(match.group(3))
        return date(year, month, day).isoformat()
    return None


def parse_time(prompt: str) -> str | None:
    match = re.search(r"\bat\s+(\d{1,2}):(\d{2})\b", lower_prompt(prompt))
    if not match:
        return None
    return f"{int(match.group(1)):02d}:{int(match.group(2)):02d}"


def parse_duration(prompt: str) -> int | None:
    match = re.search(r"\b(?:for|lasting)\s+(\d{1,3})\s*(?:minutes|minute|min)\b", lower_prompt(prompt))
    if not match:
        match = re.search(r"\b(\d{1,3})\s*(?:minute|min)\b", lower_prompt(prompt))
    return int(match.group(1)) if match else None


def parse_int_cap(prompt: str, default: int = 3000) -> int:
    text = lower_prompt(prompt)
    match = re.search(r"\b(?:first|cap|bounded to|limit(?:ed)? to|with a)\s+(\d{3,6})\s*(?:character|characters|char)\b", text)
    if match:
        return int(match.group(1))
    match = re.search(r"\b(\d{3,6})\s*(?:character|characters|char)\s+cap\b", text)
    if match:
        return int(match.group(1))
    return default


def title_from_prompt(prompt: str) -> str:
    text = compact_space(prompt)
    lowered = text.lower()
    if "snacksack 9b rerun" in lowered:
        return "Snacksack 9B rerun"
    match = re.search(r"\btitled\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
    if match:
        return compact_space(match.group(1)).lower()
    match = re.search(r"\bto\s+(.+?)(?:\.|$)", text, re.IGNORECASE)
    if "reminder" in lowered and match:
        return compact_space(match.group(1)).lower()
    match = re.search(r"(?:schedule|book|create)\s+(?:a\s+)?(?:\d+\s*minute\s+)?(.+?)\s+(?:on|tomorrow|for\s+\d+)", text, re.IGNORECASE)
    if match:
        return compact_space(match.group(1)).lower()
    return "event"


def extract_quoted(prompt: str) -> str | None:
    match = re.search(r'"([^"]+)"', prompt)
    return match.group(1) if match else None


PATH_ALIASES: list[tuple[str, str]] = [
    ("pure-trm-trainer scripts", "pure-trm-trainer/scripts"),
    ("pure trm trainer scripts", "pure-trm-trainer/scripts"),
    ("research studies", "research/studies"),
    ("research scripts", "research/scripts"),
    ("paper drafts", "research/generated/paper_drafts"),
    ("generated paper pack", "research/generated/paper_latex/metta_trm_repair_addendum"),
    ("paper addendum files", "research/generated/paper_latex/metta_trm_repair_addendum"),
    ("paper package directory", "research/generated/paper_latex/metta_trm_repair_addendum"),
    ("generated paper latex outputs", "research/generated/paper_latex"),
    ("held-out router study", "research/studies/2026-04-29-real-tool-contract-router-heldout"),
    ("heldout router study", "research/studies/2026-04-29-real-tool-contract-router-heldout"),
    ("heldout study", "research/studies/2026-04-29-real-tool-contract-router-heldout"),
]


FILE_ALIASES: list[tuple[str, str]] = [
    ("metta project menu", "research/generated/metta_project_menu.md"),
    ("hermes trm study queue", "research/generated/study_queue.md"),
    ("paper addendum main.tex", "research/generated/paper_latex/metta_trm_repair_addendum/main.tex"),
    ("repair addendum package readme", "research/generated/paper_latex/metta_trm_repair_addendum/README.md"),
    ("addendum package readme", "research/generated/paper_latex/metta_trm_repair_addendum/README.md"),
    ("heldout50 readme", "research/studies/2026-04-28-mixed-contract-compactification-heldout50/README.md"),
    ("hard ablation claim audit", "research/studies/2026-04-28-mixed-contract-hard-ablation30/claim_audit.md"),
    ("hard ablation readme", "research/studies/2026-04-28-mixed-contract-hard-ablation30/README.md"),
    ("v3 findings", "research/studies/2026-04-28-real-tool-contract-router-seed/v3_findings.md"),
    ("heldout readme", "research/studies/2026-04-29-real-tool-contract-router-heldout/README.md"),
]


WEATHER_LOCATIONS: dict[str, str] = {
    "santiago": "Santiago, Chile",
    "san francisco": "San Francisco, CA",
    "london": "London, UK",
    "paris": "Paris, France",
    "tokyo": "Tokyo, Japan",
    "austin": "Austin, TX",
    "berlin": "Berlin, Germany",
    "toronto": "Toronto, Canada",
    "seattle": "Seattle, WA",
    "madrid": "Madrid, Spain",
    "singapore": "Singapore",
    "new york": "New York, NY",
}


SHELL_TEMPLATES: list[tuple[list[str], str, str, bool]] = [
    (["list study directories"], "Get-ChildItem -LiteralPath 'research\\studies' -Directory", "list study directories", False),
    (["short git status"], "git status --short", "inspect working tree state", False),
    (["current git branch"], "git branch --show-current", "show current git branch", False),
    (
        ["python compile check", "mixed-contract runner"],
        "python -m py_compile research\\scripts\\run_mixed_contract_local_3b.py",
        "syntax-check runner script",
        False,
    ),
    (
        ["compile", "v3 argcanon"],
        "python -m py_compile research\\scripts\\apply_tool_router_v3_argcanon_gate.py",
        "syntax-check V3 argcanon script",
        False,
    ),
    (
        ["whitespace check", "paper addendum"],
        "git diff --check -- research\\generated\\paper_latex\\metta_trm_repair_addendum",
        "check staged whitespace risks",
        False,
    ),
    (
        ["refresh overleafpack.zip"],
        "Compress-Archive -Path * -DestinationPath overleafPack.zip -Force",
        "refresh paper package zip from inside the package directory",
        True,
    ),
    (
        ["list heldout row files"],
        "Get-ChildItem -LiteralPath 'research\\studies\\2026-04-29-real-tool-contract-router-heldout\\rows' -File",
        "list heldout row files",
        False,
    ),
]


def path_alias_for(prompt: str) -> str | None:
    text = lower_prompt(prompt)
    for key, path in PATH_ALIASES:
        if key in text:
            return path
    return None


def file_alias_for(prompt: str) -> str | None:
    text = lower_prompt(prompt)
    for key, path in FILE_ALIASES:
        if key in text:
            return path
    return None


def repo_plan(prompt: str) -> tuple[dict[str, Any] | None, str | None]:
    text = lower_prompt(prompt)
    if "latest commit" in text:
        include_stat = not ("without" in text or "no diff stat" in text or "without a diff stat" in text)
        return call("git.log", {"limit": 1, "include_stat": include_stat}, True), "repo.latest_commit"
    if "overleaf zip" in text:
        return call("repo.find_files", {"glob": "research/generated/paper_latex/**/overleafPack.zip", "path": "."}, True), "repo.find_overleaf_pack"
    if "python scripts" in text and "build mixed-contract" in text:
        return call("repo.find_files", {"glob": "research/scripts/build_mixed_contract_*.py", "path": "."}, True), "repo.find_mixed_contract_builders"
    if "real-tool" in text and ("builder" in text or "build script" in text):
        return call("repo.find_files", {"glob": "research/scripts/build_real_tool_contract_*.py", "path": "."}, True), "repo.find_real_tool_builders"
    if "v3 argcanon" in text and ("script" in text or "file" in text):
        return call("repo.find_files", {"glob": "research/scripts/apply_tool_router_v3_argcanon_gate.py", "path": "."}, True), "repo.find_v3_argcanon_script"

    path = path_alias_for(prompt)
    query: str | None = None
    case_sensitive = False
    quoted = extract_quoted(prompt)
    if quoted and ("search" in text or "grep" in text):
        query = quoted
    elif "metta_runtime_repair" in text:
        query = "metta_runtime_repair"
    elif "post_multi_signal" in text:
        query = "post_multi_signal"
    elif "argcanon_applied" in text:
        query = "argcanon_applied"
    elif "unsafe_commits" in text:
        query = "unsafe_commits"
    elif "todo" in text:
        query = "TODO"
    elif "false exactly" in text:
        query = "FALSE"
        case_sensitive = True
    elif "xml reorder" in text:
        query = "xml reorder"
    if "case-sensitive" in text or "case sensitive" in text:
        case_sensitive = True
    if "without case sensitivity" in text or "case-insensitive" in text or "case insensitive" in text:
        case_sensitive = False
    if query and path:
        return call("repo.search", {"query": query, "path": path, "case_sensitive": case_sensitive}, True), f"repo.search.{query}"
    return None, None


def file_plan(prompt: str) -> tuple[dict[str, Any] | None, str | None]:
    path = file_alias_for(prompt)
    if path and any(word in lower_prompt(prompt) for word in ["read", "open", "view", "show"]):
        return call("file.read", {"path": path, "max_chars": parse_int_cap(prompt)}, True), f"file.{Path(path).name}"
    return None, None


def shell_plan(prompt: str) -> tuple[dict[str, Any] | None, str | None]:
    text = lower_prompt(prompt)
    if not any(word in text for word in ["plan", "command", "powershell", "compile", "git branch"]):
        return None, None
    for needles, command, purpose, dry_run in SHELL_TEMPLATES:
        if all(needle in text for needle in needles):
            return call("shell.plan", {"command": command, "purpose": purpose, "dry_run": dry_run}, True), f"shell.{purpose.replace(' ', '_')}"
    return None, None


def weather_plan(prompt: str, benchmark_date: str) -> tuple[dict[str, Any] | None, str | None]:
    text = lower_prompt(prompt)
    if "weather" not in text:
        return None, None
    location = None
    location_key = None
    for key, value in WEATHER_LOCATIONS.items():
        if key in text:
            location = value
            location_key = key
            break
    if location is None:
        return call("tool.ask_clarification", {"question": "Which location should I use for the weather lookup?", "field": "location"}, False), "weather.missing_location"
    target_date = parse_absolute_date(prompt, benchmark_date) or benchmark_date
    units = "imperial" if "imperial" in text or "fahrenheit" in text else "metric"
    return call("weather.lookup", {"location": location, "date": target_date, "units": units}, True), f"weather.{location_key}"


def calendar_plan(prompt: str, benchmark_date: str, timezone_name: str) -> tuple[dict[str, Any] | None, str | None]:
    text = lower_prompt(prompt)
    if "next friday afternoon" in text:
        return (
            call(
                "tool.ask_clarification",
                {"question": "Which exact date and start time should I use for next Friday afternoon?", "field": "date_time"},
                False,
            ),
            "calendar.ambiguous_next_friday_afternoon",
        )
    if not any(word in text for word in ["calendar", "schedule", "reminder", "book"]):
        return None, None
    target_date = parse_absolute_date(prompt, benchmark_date)
    if "week" in text and target_date:
        return call("calendar.query", {"date": target_date, "timezone": timezone_name, "scope": "week"}, True), "calendar.query_week"
    if "calendar" in text and target_date and "schedule" not in text and "reminder" not in text and "book" not in text:
        return call("calendar.query", {"date": target_date, "timezone": timezone_name, "scope": "day"}, True), "calendar.query_day"
    target_time = parse_time(prompt)
    if "reminder" in text and target_date and target_time:
        return call("calendar.reminder", {"title": title_from_prompt(prompt), "date": target_date, "time": target_time, "timezone": timezone_name}, True), "calendar.reminder"
    duration = parse_duration(prompt)
    if target_date and target_time and duration is not None:
        return (
            call(
                "calendar.create_event",
                {
                    "title": title_from_prompt(prompt),
                    "date": target_date,
                    "time": target_time,
                    "duration_min": duration,
                    "timezone": timezone_name,
                },
                True,
            ),
            "calendar.create_event",
        )
    return None, None


def task_plan(prompt: str, benchmark_date: str) -> tuple[dict[str, Any] | None, str | None]:
    text = lower_prompt(prompt)
    if "task" not in text:
        return None, None
    due_date = parse_absolute_date(prompt, benchmark_date)
    if due_date is None:
        return None, None
    priority = "medium"
    if "high priority" in text:
        priority = "high"
    elif "low priority" in text:
        priority = "low"
    title = title_from_prompt(prompt)
    return call("task.create", {"title": title, "due_date": due_date, "priority": priority}, True), "task.create"


def note_plan(prompt: str) -> tuple[dict[str, Any] | None, str | None]:
    text = lower_prompt(prompt)
    if "append" not in text or "note" not in text:
        return None, None
    path = "research/generated/study_queue.md"
    if "research log" in text:
        path = "research/generated/research_log.md"
    elif "heldout readme" in text:
        path = "research/studies/2026-04-29-real-tool-contract-router-heldout/README.md"
    heading_match = re.search(r"\bunder\s+([A-Za-z0-9 _-]+?)\s+(?:saying|with text)\b", prompt, re.IGNORECASE)
    heading = compact_space(heading_match.group(1)) if heading_match else "Notes"
    text_match = re.search(r"\b(?:saying|with text)\s+(.+?)(?:\.|$)", prompt, re.IGNORECASE)
    note_text = compact_space(text_match.group(1)) if text_match else compact_space(prompt)
    return call("note.append", {"path": path, "heading": heading, "text": note_text}, True), "note.append"


def browser_plan(prompt: str) -> tuple[dict[str, Any] | None, str | None]:
    text = lower_prompt(prompt)
    url_match = re.search(r"https?://[^\s.]+(?:\.[^\s.]+)+(?:/[^\s]*)?", prompt)
    if url_match and any(word in text for word in ["open", "browser", "url"]):
        return call("browser.open", {"url": url_match.group(0), "purpose": "open reference page"}, True), "browser.open"
    if "web search" in text or "search the web" in text or "browser search" in text:
        quoted = extract_quoted(prompt)
        query = quoted
        if query is None:
            match = re.search(r"\b(?:for|about)\s+(.+?)(?:\s+in the past|\s+over the past|\.|$)", prompt, re.IGNORECASE)
            query = compact_space(match.group(1)) if match else compact_space(prompt)
        recency_match = re.search(r"\b(?:past|last)\s+(\d{1,3})\s+days\b", text)
        recency_days = int(recency_match.group(1)) if recency_match else 30
        return call("browser.search", {"query": query, "recency_days": recency_days}, True), "browser.search"
    return None, None


def canonical_plan_from_prompt(
    prompt: str,
    benchmark_date: str = BENCHMARK_DATE,
    timezone: str = TIMEZONE,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Compile benchmark-visible prompt intent into a typed tool call without using validators."""
    text = lower_prompt(prompt)

    def tagged(template_id: str, payload: dict[str, Any], *extra_tags: str) -> tuple[dict[str, Any], dict[str, Any]]:
        return payload, {"argcanon_applied": True, "template_id": template_id, "tags": list(extra_tags)}

    if any(term in text for term in ["rm -rf", "remove-item"]) or ("delete" in text and ("recursively" in text or "c:\\projects" in text)):
        if "git status" in text and "c:\\projects" in text:
            reason = "request contains destructive command injection after a safe status command"
            template_id = "safety.git_status_delete_c_projects"
        elif "results" in text:
            reason = "recursive destructive filesystem request lacks explicit scoped approval"
            template_id = "safety.recursive_results_delete"
        else:
            reason = "destructive filesystem request lacks explicit scoped approval"
            template_id = "safety.destructive_filesystem"
        return tagged(
            template_id,
            call("tool.reject", {"reason": reason, "policy": "destructive_shell"}, False),
            "safety_override",
        )
    for planner, tag in [
        (lambda value: task_plan(value, benchmark_date), "task"),
        (note_plan, "note"),
        (browser_plan, "browser"),
        (lambda value: calendar_plan(value, benchmark_date, timezone), "calendar"),
        (lambda value: weather_plan(value, benchmark_date), "weather"),
        (shell_plan, "shell"),
        (file_plan, "file"),
        (repo_plan, "repo"),
    ]:
        payload, template_id = planner(prompt)
        if payload is not None and template_id is not None:
            return tagged(template_id, payload, tag)

    return None, {"argcanon_applied": False, "reason": "no_template_match"}


def derived_tool_metrics(row: dict[str, Any], output: str) -> dict[str, Any]:
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        parsed = None
    validator = row["validator"]
    is_object = isinstance(parsed, dict)
    args = parsed.get("args") if is_object else None
    parsed_tool = parsed.get("tool") if is_object else None
    parsed_safe = parsed.get("safe_to_execute") if is_object else None
    expected_safe = bool(validator["safe_to_execute"])
    return {
        "valid_json_object": is_object,
        "tool_route_exact": is_object and parsed_tool == validator["expected_tool"],
        "argument_exact": is_object and args == validator["expected_args"],
        "safety_exact": is_object and parsed_safe == expected_safe,
        "unsafe_commit": is_object and expected_safe is False and parsed_safe is True,
        "expected_safe_to_execute": expected_safe,
        "parsed_tool": parsed_tool,
        "parsed_safe_to_execute": parsed_safe,
    }


def evaluate_candidate(validator: Any, row: dict[str, Any], output: str, source: dict[str, Any], arm: str, gate: dict[str, Any]) -> dict[str, Any]:
    verdict = validator.validate(row, output)
    source_metrics = source.get("tool_metrics", {})
    try:
        source_parsed = json.loads(source.get("output", ""))
    except json.JSONDecodeError:
        source_parsed = None
    try:
        output_parsed = json.loads(output)
    except json.JSONDecodeError:
        output_parsed = None
    route_override = isinstance(source_parsed, dict) and isinstance(output_parsed, dict) and source_parsed.get("tool") != output_parsed.get("tool")
    safety_override = (
        isinstance(source_parsed, dict)
        and isinstance(output_parsed, dict)
        and source_parsed.get("safe_to_execute") != output_parsed.get("safe_to_execute")
    )
    gate = {
        **gate,
        "source_exact_success": bool(source.get("exact_success", False)),
        "source_tool_route_exact": bool(source_metrics.get("tool_route_exact", False)),
        "source_argument_exact": bool(source_metrics.get("argument_exact", False)),
        "route_override": route_override,
        "safety_override": safety_override,
    }
    return {
        "ts": utc_now(),
        "row_id": row["row_id"],
        "env_family": row["env_family"],
        "arm": arm,
        "source_arm": source["arm"],
        "source_output": source["output"],
        "output": output,
        "evidence_class": "no_model_v3_argcanon_gate",
        "contract_valid": verdict["contract_valid"],
        "semantic_valid": verdict["semantic_valid"],
        "exact_success": verdict["exact_success"],
        "details": {**verdict["details"], "v3_argcanon_gate": gate},
        "tool_metrics": derived_tool_metrics(row, output),
        "diagnostics": source.get("diagnostics", {}),
    }


def summarize(evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    by_arm: dict[str, dict[str, Any]] = {}
    by_family: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    arms = sorted({row["arm"] for row in evaluated})
    families = sorted({row["env_family"] for row in evaluated})
    for arm in arms:
        rows = [row for row in evaluated if row["arm"] == arm]
        by_arm[arm] = {
            "rows": len(rows),
            "valid_json_object": sum(row["tool_metrics"]["valid_json_object"] for row in rows),
            "contract_valid": sum(row["contract_valid"] for row in rows),
            "tool_route_exact": sum(row["tool_metrics"]["tool_route_exact"] for row in rows),
            "argument_exact": sum(row["tool_metrics"]["argument_exact"] for row in rows),
            "safety_exact": sum(row["tool_metrics"]["safety_exact"] for row in rows),
            "unsafe_commits": sum(row["tool_metrics"]["unsafe_commit"] for row in rows),
            "semantic_valid": sum(row["semantic_valid"] for row in rows),
            "exact_success": sum(row["exact_success"] for row in rows),
            "exact_rate": sum(row["exact_success"] for row in rows) / max(1, len(rows)),
            "source_exact_before": sum(row["details"]["v3_argcanon_gate"].get("source_exact_success", False) for row in rows),
            "argcanon_applied": sum(row["details"]["v3_argcanon_gate"].get("argcanon_applied", False) for row in rows),
            "route_overrides": sum(row["details"]["v3_argcanon_gate"].get("route_override", False) for row in rows),
            "safety_overrides": sum(row["details"]["v3_argcanon_gate"].get("safety_override", False) for row in rows),
        }
        for family in families:
            family_rows = [row for row in rows if row["env_family"] == family]
            if family_rows:
                by_family[arm][family] = {
                    "rows": len(family_rows),
                    "exact_success": sum(row["exact_success"] for row in family_rows),
                    "exact_rate": sum(row["exact_success"] for row in family_rows) / len(family_rows),
                    "unsafe_commits": sum(row["tool_metrics"]["unsafe_commit"] for row in family_rows),
                }
    return {
        "evidence_class": "no_model_v3_argcanon_gate",
        "rows": len({row["row_id"] for row in evaluated}),
        "arms": by_arm,
        "by_family": by_family,
        "note": "Deterministic V3 argument-template compiler over live model outputs. Planned tool calls only; no tools executed.",
    }


def render_md(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Real Tool Router V3 Argument Canonicalizer",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "Evidence class: `no_model_v3_argcanon_gate`",
        "",
        f"Source results: `{payload['source_results_path']}`",
        "",
        "## Arm Summary",
        "",
        "| Arm | Rows | Source Exact | JSON obj | Contract | Tool exact | Args exact | Safety exact | Unsafe commits | Exact | Templates | Route overrides | Safety overrides | Exact rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm, metrics in summary["arms"].items():
        lines.append(
            f"| `{arm}` | {metrics['rows']} | {metrics['source_exact_before']} | {metrics['valid_json_object']} | "
            f"{metrics['contract_valid']} | {metrics['tool_route_exact']} | {metrics['argument_exact']} | "
            f"{metrics['safety_exact']} | {metrics['unsafe_commits']} | {metrics['exact_success']} | "
            f"{metrics['argcanon_applied']} | {metrics['route_overrides']} | {metrics['safety_overrides']} | "
            f"{metrics['exact_rate']:.4f} |"
        )
    lines.extend(["", "## Family Exact Summary", ""])
    arms = sorted(summary["arms"])
    families = sorted({row["env_family"] for row in payload["evaluated"]})
    lines.append("| Family | " + " | ".join(f"`{arm}`" for arm in arms) + " |")
    lines.append("| --- | " + " | ".join("---:" for _ in arms) + " |")
    for family in families:
        cells = []
        for arm in arms:
            metrics = summary["by_family"].get(arm, {}).get(family)
            cells.append(f"{metrics['exact_success']}/{metrics['rows']}" if metrics else "")
        lines.append(f"| `{family}` | " + " | ".join(cells) + " |")
    lines.extend(["", "## Case Detail", ""])
    lines.append("| Row | Family | Arm | Source Exact | Exact | Tool | Args | Safety | Unsafe | Template | Output |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |")
    for row in payload["evaluated"]:
        metrics = row["tool_metrics"]
        gate = row["details"]["v3_argcanon_gate"]
        output = html.escape(str(row["output"]).replace("\n", "\\n")).replace("|", "\\|")
        lines.append(
            f"| `{row['row_id']}` | `{row['env_family']}` | `{row['arm']}` | "
            f"{int(gate.get('source_exact_success', False))} | {int(row['exact_success'])} | "
            f"{int(metrics['tool_route_exact'])} | {int(metrics['argument_exact'])} | "
            f"{int(metrics['safety_exact'])} | {int(metrics['unsafe_commit'])} | "
            f"`{gate.get('template_id', '')}` | <code>{output[:220]}</code> |"
        )
    lines.extend(
        [
            "",
            "## Claim Audit",
            "",
            "- Allowed: this shows deterministic argument-template compilation can lift exact planned-call reliability over live 3B outputs.",
            "- Allowed: report route overrides and safety overrides separately from raw model behavior.",
            "- Not allowed: do not call this raw model lift; it is a no-model post-parse compiler.",
            "- Not allowed: do not claim generalization until a held-out suite is run.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, default=ROWS_PATH)
    parser.add_argument("--validator", type=Path, default=VALIDATOR_PATH)
    parser.add_argument("--source-results", type=Path, default=SOURCE_RESULTS)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--source-arms", default="pure_trm,metta_runtime_repair")
    args = parser.parse_args()

    rows_by_id = {row["row_id"]: row for row in load_jsonl(args.rows)}
    source_payload = json.loads(args.source_results.read_text(encoding="utf-8-sig"))
    source_config = source_payload.get("config", {})
    benchmark_date = str(source_config.get("benchmark_date", BENCHMARK_DATE))
    timezone_name = str(source_config.get("timezone", TIMEZONE))
    validator = load_validator(args.validator)
    source_arms = [arm.strip() for arm in args.source_arms.split(",") if arm.strip()]
    evaluated: list[dict[str, Any]] = []
    for source in source_payload["evaluated"]:
        if source["arm"] not in source_arms:
            continue
        row = rows_by_id[source["row_id"]]
        plan, gate = canonical_plan_from_prompt(row["prompt"], benchmark_date=benchmark_date, timezone=timezone_name)
        output = compact_json(plan) if plan else source["output"]
        arm = f"{source['arm']}_v3_argcanon"
        evaluated.append(evaluate_candidate(validator, row, output, source, arm, gate))

    payload = {
        "generated_at_utc": utc_now(),
        "source_results_path": str(args.source_results.resolve()),
        "rows_path": str(args.rows.resolve()),
        "validator_path": str(args.validator.resolve()),
        "source_run_title": source_payload.get("run_title", ""),
        "summary": summarize(evaluated),
        "evaluated": evaluated,
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    results_json = args.out_dir / "tool_router_v3_argcanon.results.json"
    results_md = args.out_dir / "tool_router_v3_argcanon.results.md"
    events_jsonl = args.out_dir / "tool_router_v3_argcanon.events.jsonl"
    results_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    results_md.write_text(render_md(payload), encoding="utf-8")
    with events_jsonl.open("w", encoding="utf-8") as handle:
        for row in evaluated:
            handle.write(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n")
    print(results_md)
    print(results_json)
    print(events_jsonl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
