from __future__ import annotations

import argparse
import ctypes
import json
import re
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "qwen35_4b_skill_smoke"


if sys.platform == "win32":
    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_ulonglong),
            ("WriteOperationCount", ctypes.c_ulonglong),
            ("OtherOperationCount", ctypes.c_ulonglong),
            ("ReadTransferCount", ctypes.c_ulonglong),
            ("WriteTransferCount", ctypes.c_ulonglong),
            ("OtherTransferCount", ctypes.c_ulonglong),
        ]


    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_longlong),
            ("PerJobUserTimeLimit", ctypes.c_longlong),
            ("LimitFlags", ctypes.c_uint32),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", ctypes.c_uint32),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", ctypes.c_uint32),
            ("SchedulingClass", ctypes.c_uint32),
        ]


    class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]


    class JOBOBJECT_CPU_RATE_CONTROL_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("ControlFlags", ctypes.c_uint32),
            ("CpuRate", ctypes.c_uint32),
        ]


    kernel32 = ctypes.windll.kernel32
    CreateJobObjectW = kernel32.CreateJobObjectW
    CreateJobObjectW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
    CreateJobObjectW.restype = ctypes.c_void_p
    AssignProcessToJobObject = kernel32.AssignProcessToJobObject
    AssignProcessToJobObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    AssignProcessToJobObject.restype = ctypes.c_int
    SetInformationJobObject = kernel32.SetInformationJobObject
    SetInformationJobObject.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    SetInformationJobObject.restype = ctypes.c_int
    JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
    JOB_OBJECT_CPU_RATE_CONTROL_ENABLE = 0x1
    JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP = 0x4
    JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
    JOB_OBJECT_CPU_RATE_CONTROL_INFORMATION_CLASS = 15


@dataclass(frozen=True)
class SkillCase:
    case_id: str
    skill_name: str
    task_prompt: str
    json_schema: Dict[str, Any]
    required_substrings: List[str]
    forbidden_substrings: List[str]


SKILL_FILES = {
    "intellect3-logic-hermes": ROOT / "intellect3-logic-hermes" / "SKILL.md",
    "intellect3-math-hermes": ROOT / "intellect3-math-hermes" / "SKILL.md",
    "pixie-mechinterp": ROOT / "pixie-mechinterp" / "SKILL.md",
    "hermes-bluebeam-research": ROOT / "hermes-bluebeam-research" / "SKILL.md",
    "trm-observability-workflow": ROOT / "trm-observability-workflow" / "SKILL.md",
    "trm-public-rationale-chain": ROOT / "trm-public-rationale-chain" / "SKILL.md",
}

SKILL_FILE_CACHE: Dict[str, str] = {}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def _logic_excerpt() -> str:
    return (
        "Skill: intellect3-logic-hermes. Contract: parse grid and signatures, build a candidate, "
        "verify tent adjacency plus row/column counts and tree pairing, then commit the final T/X/C grid. "
        "When row and column constraints are available, use scripts/check_signature_gate.py. "
        "Route to logic_skill_trm only on an exact signature match; otherwise route to logic_skill. "
        "Prefer the helper script over guessing from puzzle shape."
    )


def _math_excerpt() -> str:
    return (
        "Skill: intellect3-math-hermes. Contract: parse givens, solve with a short candidate path, "
        "verify arithmetic consistency, then commit the final integer answer string. "
        "Default to the plain math path. Use the TRM path only when an explicit support pattern says it is helpful. "
        "When prompt text is available, use scripts/check_support_pattern.py instead of guessing."
    )


def _pixie_excerpt() -> str:
    return (
        "Skill: pixie-mechinterp. Workflow: read references/paths.md first, inspect the latest receipt or study root, "
        "then use the narrowest matching script. For trigger-vs-drift matrix comparisons use run_fae_ablation_matrix.py. "
        "Prefer existing packaged outputs over fresh long reruns."
    )


def _bluebeam_excerpt() -> str:
    return (
        "Skill: hermes-bluebeam-research. First check state with scripts/bluebeam_research_status.py. "
        "Prefer existing artifacts over reruns. If the loop is already running, report it and do not launch a duplicate."
    )


def _trm_excerpt() -> str:
    return (
        "Skill: trm-observability-workflow. Workflow order: bootstrap the harness, collect teacher traces, "
        "build TRM rows, merge corpora, then train or benchmark components. "
        "The first local script is scripts/bootstrap_harness.py."
    )


def _public_rationale_excerpt() -> str:
    return (
        "Skill: trm-public-rationale-chain. Contract: use TRM_PARSE -> TRM_CRITIC -> TRM_COMPRESS -> FINAL, "
        "keep the public trace to three short rationale lines, and never claim to reveal hidden chain-of-thought. "
        "Use scripts/build_skill_prompt.py for logic, math, or generic public-trace prompts."
    )


def build_cases() -> List[SkillCase]:
    return [
        SkillCase(
            case_id="logic_known_signature",
            skill_name="intellect3-logic-hermes",
            task_prompt=(
                "Rows=[2,0,2,0,1] Cols=[1,1,0,2,1]. "
                "Return one-line JSON with keys helper_script and route."
            ),
            json_schema={
                "type": "object",
                "properties": {
                    "helper_script": {"type": "string"},
                    "route": {"type": "string"},
                },
                "required": ["helper_script", "route"],
                "additionalProperties": False,
            },
            required_substrings=["scripts/check_signature_gate.py", "logic_skill_trm"],
            forbidden_substrings=[],
        ),
        SkillCase(
            case_id="logic_unknown_signature",
            skill_name="intellect3-logic-hermes",
            task_prompt=(
                "Rows=[9,9,9] Cols=[9,9,9]. "
                "Return one-line JSON with keys helper_script and route."
            ),
            json_schema={
                "type": "object",
                "properties": {
                    "helper_script": {"type": "string"},
                    "route": {"type": "string"},
                },
                "required": ["helper_script", "route"],
                "additionalProperties": False,
            },
            required_substrings=["scripts/check_signature_gate.py", "logic_skill"],
            forbidden_substrings=['"route":"logic_skill_trm"', '"route": "logic_skill_trm"'],
        ),
        SkillCase(
            case_id="math_supported_pattern",
            skill_name="intellect3-math-hermes",
            task_prompt=(
                "Prompt text: Find two marked cells with consecutive integers whose product is 72. "
                "Return one-line JSON with keys helper_script and route."
            ),
            json_schema={
                "type": "object",
                "properties": {
                    "helper_script": {"type": "string"},
                    "route": {"type": "string"},
                },
                "required": ["helper_script", "route"],
                "additionalProperties": False,
            },
            required_substrings=["scripts/check_support_pattern.py", "math_skill_trm"],
            forbidden_substrings=[],
        ),
        SkillCase(
            case_id="math_default_path",
            skill_name="intellect3-math-hermes",
            task_prompt=(
                "Prompt text: Compute 17*19+23. "
                "Return one-line JSON with keys helper_script and route."
            ),
            json_schema={
                "type": "object",
                "properties": {
                    "helper_script": {"type": "string"},
                    "route": {"type": "string"},
                },
                "required": ["helper_script", "route"],
                "additionalProperties": False,
            },
            required_substrings=["scripts/check_support_pattern.py", "math_skill"],
            forbidden_substrings=['"route":"math_skill_trm"', '"route": "math_skill_trm"'],
        ),
        SkillCase(
            case_id="pixie_matrix_choice",
            skill_name="pixie-mechinterp",
            task_prompt=(
                "Task: trigger-vs-drift matrix comparisons. "
                "Return one-line JSON with keys first_reference and script."
            ),
            json_schema={
                "type": "object",
                "properties": {
                    "first_reference": {"type": "string"},
                    "script": {"type": "string"},
                },
                "required": ["first_reference", "script"],
                "additionalProperties": False,
            },
            required_substrings=["references/paths.md", "run_fae_ablation_matrix.py"],
            forbidden_substrings=[],
        ),
        SkillCase(
            case_id="bluebeam_status_first",
            skill_name="hermes-bluebeam-research",
            task_prompt=(
                "Task: continue the local BlueBeam loop while avoiding duplicate launches. "
                "Return one-line JSON with keys first_script and duplicate_rule."
            ),
            json_schema={
                "type": "object",
                "properties": {
                    "first_script": {"type": "string"},
                    "duplicate_rule": {"type": "string"},
                },
                "required": ["first_script", "duplicate_rule"],
                "additionalProperties": False,
            },
            required_substrings=["scripts/bluebeam_research_status.py", "do not launch a duplicate"],
            forbidden_substrings=[],
        ),
        SkillCase(
            case_id="trm_bootstrap_first",
            skill_name="trm-observability-workflow",
            task_prompt=(
                "Task: bootstrap before teacher-trace collection. "
                "Return one-line JSON with keys first_script and next_stage."
            ),
            json_schema={
                "type": "object",
                "properties": {
                    "first_script": {"type": "string"},
                    "next_stage": {"type": "string"},
                },
                "required": ["first_script", "next_stage"],
                "additionalProperties": False,
            },
            required_substrings=["scripts/bootstrap_harness.py", "collect teacher traces"],
            forbidden_substrings=[],
        ),
        SkillCase(
            case_id="trm_public_trace_contract",
            skill_name="trm-public-rationale-chain",
            task_prompt=(
                "Task: define the public rationale chain for a small-model benchmark. "
                "Return one-line JSON with keys stage_order, max_public_lines, and warning."
            ),
            json_schema={
                "type": "object",
                "properties": {
                    "stage_order": {"type": "string"},
                    "max_public_lines": {"type": "string"},
                    "warning": {"type": "string"},
                },
                "required": ["stage_order", "max_public_lines", "warning"],
                "additionalProperties": False,
            },
            required_substrings=["TRM_PARSE", "TRM_CRITIC", "TRM_COMPRESS", "hidden chain-of-thought"],
            forbidden_substrings=[],
        ),
    ]


def load_skill_file(skill_name: str) -> str:
    cached = SKILL_FILE_CACHE.get(skill_name)
    if cached is not None:
        return cached
    path = SKILL_FILES.get(skill_name)
    if path is None or not path.exists():
        SKILL_FILE_CACHE[skill_name] = ""
        return ""
    text = path.read_text(encoding="utf-8").strip()
    SKILL_FILE_CACHE[skill_name] = text
    return text


def inline_excerpt(skill_name: str) -> str:
    if skill_name == "intellect3-logic-hermes":
        return _logic_excerpt()
    if skill_name == "intellect3-math-hermes":
        return _math_excerpt()
    if skill_name == "pixie-mechinterp":
        return _pixie_excerpt()
    if skill_name == "hermes-bluebeam-research":
        return _bluebeam_excerpt()
    if skill_name == "trm-observability-workflow":
        return _trm_excerpt()
    if skill_name == "trm-public-rationale-chain":
        return _public_rationale_excerpt()
    return ""


def _run_helper_script(script_path: Path, args: List[str]) -> Dict[str, str]:
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=20,
    )
    if result.returncode != 0:
        return {}
    rows: Dict[str, str] = {}
    for line in (result.stdout or "").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        rows[key.strip()] = value.strip()
    return rows


def route_hint_for_case(case: SkillCase) -> str:
    if case.skill_name == "intellect3-logic-hermes":
        match = re.search(r"Rows=(\[[^\]]+\])\s+Cols=(\[[^\]]+\])", case.task_prompt)
        if not match:
            return ""
        helper = ROOT / "intellect3-logic-hermes" / "scripts" / "check_signature_gate.py"
        rows = _run_helper_script(helper, ["--rows", match.group(1), "--cols", match.group(2)])
        if not rows:
            return ""
        return "\n".join(
            [
                "helper_script=scripts/check_signature_gate.py",
                *(f"{key}={value}" for key, value in rows.items()),
            ]
        )
    if case.skill_name == "intellect3-math-hermes":
        match = re.search(r"Prompt text:\s*(.*?)\s+Return one-line JSON", case.task_prompt)
        if not match:
            return ""
        helper = ROOT / "intellect3-math-hermes" / "scripts" / "check_support_pattern.py"
        rows = _run_helper_script(helper, ["--text", match.group(1).strip()])
        if not rows:
            return ""
        return "\n".join(
            [
                "helper_script=scripts/check_support_pattern.py",
                *(f"{key}={value}" for key, value in rows.items()),
            ]
        )
    return ""


def render_prompt(case: SkillCase, variant: str) -> tuple[str, str]:
    task = case.task_prompt.strip()
    if variant == "baseline":
        return task, "baseline"
    if variant == "inline_excerpt":
        excerpt = inline_excerpt(case.skill_name)
        return f"{excerpt} {task}".strip(), "inline_excerpt"

    skill_file = load_skill_file(case.skill_name)
    route_hint = route_hint_for_case(case)

    if skill_file:
        prompt = (
            "You are using the following Hermes skill instructions. "
            "Follow them for the user task.\n\n"
            "<SKILL>\n"
            f"{skill_file}\n"
            "</SKILL>\n"
        )
        if variant == "skill_file":
            prompt += f"\nUSER TASK:\n{task}\n"
            return prompt, "skill_file"
        if variant == "skill_file_routed":
            if route_hint:
                prompt += f"\nLOCAL ROUTE HINT:\n{route_hint}\n"
                prompt += f"\nUSER TASK:\n{task}\n"
                return prompt, "skill_file_routed"
            prompt += f"\nUSER TASK:\n{task}\n"
            return prompt, "skill_file_fallback"
    excerpt = inline_excerpt(case.skill_name)
    if variant == "skill_file_routed" and route_hint:
        return f"{excerpt}\nLOCAL ROUTE HINT:\n{route_hint}\n\nUSER TASK:\n{task}".strip(), "inline_excerpt_routed_fallback"
    return f"{excerpt} {task}".strip(), "inline_excerpt_fallback"


def call_completion(
    base_url: str,
    prompt: str,
    *,
    max_tokens: int = 80,
    timeout_seconds: int = 300,
) -> Dict[str, Any]:
    payload = {
        "prompt": prompt,
        "n_predict": max_tokens,
        "temperature": 0.0,
        "top_p": 1.0,
        "stop": ["\n\nUSER TASK:"],
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/completion",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_cli_completion(
    *,
    exe_path: Path,
    model_path: Path,
    prompt: str,
    json_schema: Dict[str, Any],
    memory_limit_mb: int,
    cpu_percent: int,
    ctx_size: int,
    max_tokens: int,
    timeout_seconds: int,
) -> Dict[str, Any]:
    args = [
        str(exe_path),
        "--model",
        str(model_path),
        "-c",
        str(ctx_size),
        "-n",
        str(max_tokens),
        "--n-gpu-layers",
        "99",
        "--threads",
        "4",
        "--threads-batch",
        "2",
        "--flash-attn",
        "on",
        "--cache-type-k",
        "q4_0",
        "--cache-type-v",
        "q4_0",
        "--reasoning",
        "off",
        "--reasoning-budget",
        "0",
        "--reasoning-format",
        "none",
        "--color",
        "off",
        "--no-display-prompt",
        "--log-disable",
        "-no-cnv",
        "-j",
        json.dumps(json_schema, separators=(",", ":")),
        "-p",
        prompt,
    ]
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    job_handle: Optional[int] = None
    try:
        if sys.platform == "win32":
            job_handle = int(CreateJobObjectW(None, f"codex-qwen35-skill-cli-{int(time.time() * 1000)}"))
            if not job_handle:
                raise OSError("CreateJobObjectW failed")
            _configure_job(job_handle, memory_limit_mb, cpu_percent)
            if not AssignProcessToJobObject(job_handle, int(proc._handle)):
                proc.terminate()
                raise OSError("AssignProcessToJobObject failed")
        stdout_text, stderr_text = proc.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout_text, stderr_text = proc.communicate()
        raise TimeoutError("llama-cli completion timed out") from None
    raw_text = (stdout_text or "").strip()
    return {
        "content": raw_text,
        "stderr": (stderr_text or "").strip(),
        "returncode": proc.returncode,
    }


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def score_case(text: str, case: SkillCase) -> Dict[str, Any]:
    lowered = normalize(text)
    missing = [item for item in case.required_substrings if normalize(item) not in lowered]
    forbidden_hits = [item for item in case.forbidden_substrings if normalize(item) in lowered]
    passed = not missing and not forbidden_hits
    return {
        "passed": passed,
        "missing": missing,
        "forbidden_hits": forbidden_hits,
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def append_event(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def append_stdout(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "ts": time.time(),
                    **payload,
                },
                ensure_ascii=True,
            )
            + "\n"
        )


def wait_for_health(base_url: str, timeout_seconds: int = 60) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            req = urllib.request.Request(f"{base_url.rstrip('/')}/health")
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(1.5)
    return False


def _configure_job(job: int, memory_limit_mb: int, cpu_percent: int) -> None:
    if sys.platform != "win32":
        return
    extended = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    extended.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_PROCESS_MEMORY
    extended.ProcessMemoryLimit = int(memory_limit_mb * 1024 * 1024)
    if not SetInformationJobObject(
        job,
        JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
        ctypes.byref(extended),
        ctypes.sizeof(extended),
    ):
        raise OSError("SetInformationJobObject failed for memory limit")

    cpu = JOBOBJECT_CPU_RATE_CONTROL_INFORMATION()
    cpu.ControlFlags = JOB_OBJECT_CPU_RATE_CONTROL_ENABLE | JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP
    cpu.CpuRate = max(1, min(10000, int(cpu_percent * 100)))
    if not SetInformationJobObject(
        job,
        JOB_OBJECT_CPU_RATE_CONTROL_INFORMATION_CLASS,
        ctypes.byref(cpu),
        ctypes.sizeof(cpu),
    ):
        raise OSError("SetInformationJobObject failed for CPU limit")


def select_cases(cases: List[SkillCase], case_id: Optional[str]) -> List[SkillCase]:
    if not case_id:
        return cases
    requested = {c.strip() for c in case_id.split(",") if c.strip()}
    selected = [case for case in cases if case.case_id in requested]
    if not selected:
        unknown = sorted(requested)
        known = ", ".join(case.case_id for case in cases)
        raise ValueError(f"No matching case_id(s): {unknown}. Known: {known}")
    missing = sorted(requested - {case.case_id for case in cases})
    if missing:
        raise ValueError(f"Unknown case_id(s): {missing}")
    return selected


def launch_managed_server(
    *,
    event_log: Path,
    exe_path: Path,
    model_path: Path,
    base_url: str,
    memory_limit_mb: int,
    cpu_percent: int,
    ctx_size: int,
    reasoning_mode: str,
    startup_timeout_seconds: int,
) -> tuple[subprocess.Popen[bytes], Optional[int]]:
    port_match = re.search(r":(\d+)$", base_url.rstrip("/"))
    if not port_match:
        raise ValueError(f"Could not infer port from base URL: {base_url}")
    port = int(port_match.group(1))
    stdout_path = DATA_DIR / "managed_server.out.log"
    stderr_path = DATA_DIR / "managed_server.err.log"
    for path in (stdout_path, stderr_path):
        if path.exists():
            path.unlink()

    job_handle: Optional[int] = None
    if sys.platform == "win32":
        job_handle = int(CreateJobObjectW(None, f"codex-qwen35-skill-smoke-{int(time.time())}"))
        if not job_handle:
            raise OSError("CreateJobObjectW failed")
        _configure_job(job_handle, memory_limit_mb, cpu_percent)

    args = [
        str(exe_path),
        "--model",
        str(model_path),
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--ctx-size",
        str(ctx_size),
        "--n-gpu-layers",
        "99",
        "--threads",
        "4",
        "--threads-batch",
        "2",
        "--batch-size",
        "64",
        "--ubatch-size",
        "32",
        "--parallel",
        "1",
        "--reasoning",
        reasoning_mode,
        "--flash-attn",
        "on",
        "--cache-type-k",
        "q4_0",
        "--cache-type-v",
        "q4_0",
        "--no-webui",
    ]
    append_event(
        event_log,
        {
            "ts": time.time(),
            "event": "server_start",
            "base_url": base_url,
            "memory_limit_mb": memory_limit_mb,
            "cpu_percent": cpu_percent,
            "ctx_size": ctx_size,
        },
    )
    stdout_handle = stdout_path.open("wb")
    stderr_handle = stderr_path.open("wb")
    proc = subprocess.Popen(args, stdout=stdout_handle, stderr=stderr_handle)
    if job_handle is not None and sys.platform == "win32":
        if not AssignProcessToJobObject(job_handle, int(proc._handle)):
            proc.terminate()
            raise OSError("AssignProcessToJobObject failed")
    ready = wait_for_health(base_url, timeout_seconds=startup_timeout_seconds)
    append_event(
        event_log,
        {
            "ts": time.time(),
            "event": "server_ready" if ready else "server_not_ready",
            "pid": proc.pid,
            "ready": ready,
        },
    )
    if not ready:
        proc.terminate()
        raise RuntimeError("Managed local server did not become healthy under the default hard cap.")
    return proc, job_handle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", default="server", choices=["server", "cli"])
    parser.add_argument("--base-url", default="http://127.0.0.1:18083")
    parser.add_argument("--run-id", default="qwen35-4b-skill-smoke")
    parser.add_argument("--managed-server", action="store_true")
    parser.add_argument("--memory-limit-mb", type=int, default=2048)
    parser.add_argument("--cpu-percent", type=int, default=50)
    parser.add_argument("--ctx-size", type=int, default=512)
    parser.add_argument("--startup-timeout-seconds", type=int, default=180)
    parser.add_argument("--case-timeout-seconds", type=int, default=240)
    parser.add_argument("--request-timeout-seconds", type=int, default=600)
    parser.add_argument("--max-tokens", type=int, default=80)
    parser.add_argument("--case-id", default="", help="Comma-separated case_id list to run (default: all)")
    parser.add_argument(
        "--variant",
        nargs="+",
        default=["inline_excerpt"],
        choices=["baseline", "inline_excerpt", "skill_file", "skill_file_routed"],
        help="Prompt variants to compare in one run",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop batch after first case error or timeout",
    )
    parser.add_argument("--reasoning-mode", default="auto", choices=["auto", "on", "off"])
    parser.add_argument(
        "--exe-path",
        default=r"D:\Research_Engine\runtime\llama-b8665-win-cuda-12.4-x64\llama-server.exe",
    )
    parser.add_argument(
        "--cli-exe-path",
        default=r"D:\Research_Engine\runtime\llama-b8665-win-cuda-12.4-x64\llama-cli.exe",
    )
    parser.add_argument(
        "--model-path",
        default=r"D:\Research_Engine\models\Qwen3.5\Qwen3.5-4B\Qwen3.5-4B-Q4_K_M.gguf",
    )
    parser.add_argument(
        "--stout-log",
        default="",
        help="Structured stdout artifact path; defaults to <run-id>.stout.jsonl",
    )
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    event_log = DATA_DIR / f"{args.run_id}.events.jsonl"
    summary_path = DATA_DIR / f"{args.run_id}.summary.json"
    stout_log = Path(args.stout_log or str(DATA_DIR / f"{args.run_id}.stout.jsonl"))
    if event_log.exists():
        event_log.unlink()
    if stout_log.exists():
        stout_log.unlink()

    managed_proc: Optional[subprocess.Popen[bytes]] = None
    job_handle: Optional[int] = None
    if args.runner == "server" and args.managed_server:
        managed_proc, job_handle = launch_managed_server(
            event_log=event_log,
            exe_path=Path(args.exe_path),
            model_path=Path(args.model_path),
            base_url=args.base_url,
            memory_limit_mb=args.memory_limit_mb,
            cpu_percent=args.cpu_percent,
            ctx_size=args.ctx_size,
            reasoning_mode=args.reasoning_mode,
            startup_timeout_seconds=args.startup_timeout_seconds,
        )

    try:
        cases = select_cases(build_cases(), args.case_id)
    except ValueError as exc:
        raise RuntimeError(str(exc))

    records: List[Dict[str, Any]] = []
    try:
        append_stdout(
            stout_log,
            {
                "event": "run_start",
                "run_id": args.run_id,
                "runner": args.runner,
                "base_url": args.base_url,
                "managed_server": bool(args.managed_server),
                "case_id_filter": args.case_id or None,
                "variants": args.variant,
                "max_tokens": args.max_tokens,
            },
        )
        total_steps = len(cases) * len(args.variant)
        step = 0
        for variant in args.variant:
            for case in cases:
                step += 1
                prompt_text, effective_variant = render_prompt(case, variant)
                started = time.perf_counter()
                try:
                    if args.runner == "cli":
                        raw = run_cli_completion(
                            exe_path=Path(args.cli_exe_path),
                            model_path=Path(args.model_path),
                            prompt=prompt_text,
                            json_schema=case.json_schema,
                            memory_limit_mb=args.memory_limit_mb,
                            cpu_percent=args.cpu_percent,
                            ctx_size=args.ctx_size,
                            max_tokens=args.max_tokens,
                            timeout_seconds=args.case_timeout_seconds,
                        )
                    else:
                        raw = call_completion(
                            args.base_url,
                            prompt_text,
                            max_tokens=args.max_tokens,
                            timeout_seconds=args.request_timeout_seconds,
                        )
                    status = "ok"
                    if int(raw.get("returncode") or 0) != 0:
                        raw["error"] = raw.get("error") or f"nonzero_returncode={raw.get('returncode')}"
                        raw["status"] = "error"
                        status = "error"
                except TimeoutError as exc:
                    raw = {
                        "content": "",
                        "returncode": -1,
                        "tokens_evaluated": 0,
                        "tokens_predicted": 0,
                        "error": str(exc),
                        "status": "timeout",
                    }
                    status = "timeout"
                except Exception as exc:
                    raw = {
                        "content": "",
                        "returncode": -1,
                        "tokens_evaluated": 0,
                        "tokens_predicted": 0,
                        "error": str(exc),
                        "status": "error",
                    }
                    status = "error"

                latency = round(time.perf_counter() - started, 4)
                text = str(raw.get("content") or "").strip()
                scored = score_case(text, case) if not raw.get("status") else {
                    "passed": False,
                    "missing": [],
                    "forbidden_hits": [],
                }
                record = {
                    "case_id": case.case_id,
                    "skill_name": case.skill_name,
                    "requested_variant": variant,
                    "effective_variant": effective_variant,
                    "latency_seconds": latency,
                    "response_text": text,
                    "runner": args.runner,
                    "case_status": status,
                    "prompt_chars": len(prompt_text),
                    "returncode": raw.get("returncode"),
                    "tokens_evaluated": int(raw.get("tokens_evaluated") or 0),
                    "tokens_predicted": int(raw.get("tokens_predicted") or 0),
                    **({"error": raw.get("error")} if raw.get("error") else {}),
                    **scored,
                }
                if raw.get("stderr"):
                    record["stderr_tail"] = str(raw["stderr"])[-800:]
                records.append(record)
                append_event(event_log, {"step": step, "total_steps": total_steps, **record})
                append_stdout(
                    stout_log,
                    {
                        "event": "case_result",
                        "step": step,
                        "total_steps": total_steps,
                        "case_id": case.case_id,
                        "skill_name": case.skill_name,
                        "requested_variant": variant,
                        "effective_variant": effective_variant,
                        "status": status,
                        "latency_seconds": latency,
                        "score": scored,
                        "response_preview": text[:800],
                    },
                )
                if status != "ok" and args.stop_on_error:
                    break
            if status != "ok" and args.stop_on_error:
                break
    finally:
        if managed_proc is not None:
            try:
                managed_proc.terminate()
                managed_proc.wait(timeout=10)
            except Exception:
                managed_proc.kill()
            append_event(
                event_log,
                {
                    "ts": time.time(),
                    "event": "server_stop",
                    "pid": managed_proc.pid,
                },
            )
            append_stdout(
                stout_log,
                {
                    "event": "server_stopped",
                    "pid": managed_proc.pid,
                },
            )

    per_skill: Dict[str, Dict[str, Any]] = {}
    per_variant: Dict[str, Dict[str, Any]] = {}
    per_skill_variant: Dict[str, Dict[str, Any]] = {}
    for record in records:
        bucket = per_skill.setdefault(record["skill_name"], {"rows": 0, "passes": 0})
        bucket["rows"] += 1
        bucket["passes"] += int(bool(record["passed"]))
        variant_bucket = per_variant.setdefault(record["effective_variant"], {"rows": 0, "passes": 0})
        variant_bucket["rows"] += 1
        variant_bucket["passes"] += int(bool(record["passed"]))
        combo_key = f"{record['effective_variant']}::{record['skill_name']}"
        combo_bucket = per_skill_variant.setdefault(combo_key, {"rows": 0, "passes": 0})
        combo_bucket["rows"] += 1
        combo_bucket["passes"] += int(bool(record["passed"]))
    for bucket in per_skill.values():
        bucket["pass_rate"] = round(bucket["passes"] / bucket["rows"], 4) if bucket["rows"] else 0.0
    for bucket in per_variant.values():
        bucket["pass_rate"] = round(bucket["passes"] / bucket["rows"], 4) if bucket["rows"] else 0.0
    for bucket in per_skill_variant.values():
        bucket["pass_rate"] = round(bucket["passes"] / bucket["rows"], 4) if bucket["rows"] else 0.0

    summary = {
        "run_id": args.run_id,
        "runner": args.runner,
        "base_url": args.base_url,
        "managed_server": bool(args.managed_server),
        "requested_variants": args.variant,
        "rows": len(records),
        "passes": sum(int(bool(record["passed"])) for record in records),
        "pass_rate": round(sum(int(bool(record["passed"])) for record in records) / len(records), 4) if records else 0.0,
        "per_skill": per_skill,
        "per_variant": per_variant,
        "per_skill_variant": per_skill_variant,
        "artifacts": {
            "event_log": str(event_log.resolve()),
            "summary": str(summary_path.resolve()),
        },
        "records": records,
    }
    summary["artifacts"]["stout_log"] = str(stout_log.resolve())
    write_json(summary_path, summary)
    append_stdout(
        stout_log,
        {
            "event": "run_complete",
            "run_id": args.run_id,
            "rows": len(records),
            "passes": sum(int(bool(record["passed"])) for record in records),
            "pass_rate": summary["pass_rate"],
        },
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
