from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import shlex
import traceback
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from primehub_role_imprint import load_cluster_role_gate


DEFAULT_TRM_ROOT = Path(r"C:/projects/trm_observability_harness")
DEFAULT_MANIFEST = Path(r"C:/projects/Hermes-Skills/Hermes Skills/data/primehub_env_manifest.json")
DEFAULT_SKILL_BATCH_MANIFEST = Path(r"C:/projects/Hermes-Skills/Hermes Skills/data/primehub_skill_batch_evolution/latest.manifest.json")
DEFAULT_ROLE_IMPRINT = Path(r"C:/projects/Hermes-Skills/Hermes Skills/data/primehub_skill_trm_matrix/latest/role_based_imprint.json")
DEFAULT_RUN_ROOT = Path(r"C:/projects/Hermes-Skills/Hermes Skills/data/primehub_overnight")
DEFAULT_HOST = "snacksack-ms-7d32.tail3156cd.ts.net"
DEFAULT_9B_URL = f"http://{DEFAULT_HOST}:8082/v1"
DEFAULT_27B_URL = f"http://{DEFAULT_HOST}:8081/v1"
DEFAULT_RESEARCH_ENV_ROOT = Path(r"C:/projects/prime_intellect_research_environments/environments")
DEFAULT_RESEARCH_API = "https://api.github.com/repos/PrimeIntellect-ai/research-environments/contents/environments?per_page=120"
DEFAULT_COMMUNITY_API = "https://api.github.com/repos/PrimeIntellect-ai/community-environments/contents/environments"
DEFAULT_COMMUNITY_TIMEOUT = 20
DEFAULT_BRIDGE_SCRIPT = (Path(__file__).resolve().parent / "remote_prime_env_bridge.py").as_posix()
DEFAULT_PRIMEHUB_CMD = (
    '"{python_exec}" '
    f'"{DEFAULT_BRIDGE_SCRIPT}" '
    "--source {env_source} "
    f'--host "{DEFAULT_HOST}" '
    '--user "snacksack" '
    '--identity-file "C:/Users/patri/.ssh/id_ed25519" '
    '--ssh-timeout-seconds 120 '
    '--research-root "/home/snacksack/prime_repos_tmp/research-environments/environments" '
    '--community-root "/home/snacksack/prime_repos_tmp/community-environments/environments" '
    "{env_id}"
)
DEFAULT_TRAJECTORY_ROOT = Path(r"C:/projects/Tesseract/Tesseract/data/normalized_trajectories")
DEFAULT_TRAJECTORY_EXCLUDES = {"combined_20_envs", "wordle"}
DEFAULT_TRAJECTORY_MANIFEST = ""
DEFAULT_ENV_MODE = "auto"
DEFAULT_VARIANT_IDS = ["single-model-baseline"]
CLUSTER_PRIORITY = {
    "internal_action": 0,
    "structured_map": 1,
    "hard_reasoning_numeric": 2,
    "hard_reasoning_logic": 3,
    "abstain_guard": 4,
    "choice_contract": 5,
}
FORCE_DIRECT_OUTPUT_ENVS = {
    "mmlu_pro",
    "simpleqa",
    "simpleqa_verified",
    "simpleqa_verified_2",
    "truthfulqa",
}
MIN_COMPLETION_TOKENS_BY_ENV = {
    "mmlu_pro": 512,
    "simpleqa": 256,
    "simpleqa_verified": 256,
    "simpleqa_verified_2": 256,
    "truthfulqa": 256,
}
MIN_REQUEST_TIMEOUT_BY_ENV = {
    "mmlu_pro": 600,
}


def now_ts() -> float:
    return time.time()


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.loads(handle.read())


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def normalize_slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", str(value).strip())
    cleaned = cleaned.strip("._-")
    return cleaned or "item"


def _as_int_mapping(payload: Any) -> Dict[str, int]:
    if not isinstance(payload, dict):
        return {}
    result: Dict[str, int] = {}
    for key, value in payload.items():
        try:
            count = int(value)
        except (TypeError, ValueError):
            continue
        if count > 0:
            result[str(key)] = count
    return result


def fetch_github_dir_names(api_url: str, timeout_sec: int = DEFAULT_COMMUNITY_TIMEOUT) -> List[str]:
    names: List[str] = []
    next_url: Optional[str] = api_url
    while next_url:
        req = urllib.request.Request(next_url)
        req.add_header("User-Agent", "HermesSkillsBenchmark")
        with urllib.request.urlopen(req, timeout=timeout_sec) as response:
            payload = json.loads(response.read().decode("utf-8"))
            names.extend(
                [
                    str(item["name"])
                    for item in payload
                    if str(item.get("type")) == "dir" and item.get("name")
                ]
            )
            link_header = response.headers.get("Link", "")
            next_url = None
            if link_header:
                for segment in link_header.split(","):
                    pieces = segment.strip().split(";")
                    if len(pieces) >= 2 and 'rel="next"' in pieces[1]:
                        next_url = pieces[0].strip()[1:-1]
                        break
    return sorted(set(names))


def collect_research_env_ids(research_root: Path) -> List[str]:
    if not research_root.exists():
        return []
    return sorted(
        [
            item.name
            for item in research_root.iterdir()
            if item.is_dir() and not item.name.startswith(".")
        ]
    )


def load_trajectory_manifest(path: Path) -> List[str]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    rows: List[str] = []
    if isinstance(payload, dict):
        rows = payload.get("envs", [])
    elif isinstance(payload, list):
        rows = payload
    elif isinstance(payload, tuple):
        rows = list(payload)
    return [str(item).strip() for item in rows if str(item).strip()]


def discover_trajectory_envs(
    root: Path,
    manifest: List[str] | None,
    excludes: Iterable[str] | None = None,
) -> List[str]:
    if manifest:
        return sorted({str(item) for item in manifest if str(item).strip()})
    if not root.exists():
        return []
    found = []
    for item in sorted(root.glob("*.jsonl")):
        stem = item.stem
        if not stem:
            continue
        if stem in set(excludes or DEFAULT_TRAJECTORY_EXCLUDES):
            continue
        if stem == "combined_20_envs":
            continue
        found.append(stem)
    return sorted(set(found))


def render_primehub_command(command_template: str, python_exec: str, env: Dict[str, Any]) -> List[str]:
    env_id = str(env.get("env_id", ""))
    rendered = command_template.format(
        python_exec=python_exec,
        env_id=env_id,
        env_source=str(env.get("source", "")),
        env_owner=str(env.get("owner", "")),
        env_folder=str(env.get("folder", "")),
        command_name=str(env.get("command_name", env_id)),
    )
    rendered = rendered.strip()
    if not rendered:
        return []
    try:
        parts = shlex.split(rendered, posix=False)
    except ValueError:
        return []
    normalized = []
    for part in parts:
        if len(part) >= 2 and part[0] == part[-1] and part[0] in {'"', "'"}:
            normalized.append(part[1:-1])
        else:
            normalized.append(part)
    return normalized


def build_manifest(
    profiles: List[Dict[str, Any]],
    research_root: Path = DEFAULT_RESEARCH_ENV_ROOT,
    community_api: str = DEFAULT_COMMUNITY_API,
    research_api: Optional[str] = None,
) -> Dict[str, Any]:
    if not isinstance(profiles, list):
        profiles = []

    existing = {
        (str(item.get("source", "")), str(item.get("folder", ""))): item
        for item in profiles
        if isinstance(item, dict)
    }

    def profile_for(source: str, folder: str, owner: str) -> Dict[str, Any]:
        key = (source, folder)
        existing_row = existing.get(key, {})
        if not isinstance(existing_row, dict):
            existing_row = {}
        existing_row["source"] = source
        existing_row["folder"] = folder
        existing_row.setdefault("env_id", folder)
        existing_row.setdefault("command_name", folder)
        existing_row.setdefault("available", True)
        existing_row.setdefault("owner", owner)
        return existing_row

    rows: List[Dict[str, Any]] = []
    seen: set[Tuple[str, str]] = set()

    try:
        research_names = collect_research_env_ids(research_root)
    except OSError as exc:
        print(f"[warn] failed to enumerate research env directory {research_root}: {exc}")
        research_names = []

    if research_api:
        try:
            for name in fetch_github_dir_names(research_api):
                if name not in research_names:
                    research_names.append(name)
            research_names = sorted(set(research_names))
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, ValueError) as exc:
            print(f"[warn] research API lookup failed: {exc}")

    for name in sorted(set(research_names)):
        key = ("research", name)
        if key in seen:
            continue
        rows.append(profile_for("research", name, "primeintellect"))
        seen.add(key)

    try:
        community_names = fetch_github_dir_names(community_api)
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, ValueError) as exc:
        print(f"[warn] community API lookup failed: {exc}")
        community_names = []
    for name in sorted(set(community_names)):
        key = ("community", name)
        if key in seen:
            continue
        rows.append(profile_for("community", name, "community"))
        seen.add(key)

    return {
        "generated_at": now_iso(),
        "total": len(rows),
        "profiles": rows,
    }


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    lines: List[Dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            lines.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return lines


def load_manifest(path: Path) -> List[Dict[str, Any]]:
    data = read_json(path)
    profiles = data.get("profiles", [])
    if not isinstance(profiles, list):
        raise ValueError(f"Manifest is malformed: expected list at {path}")
    return profiles


def load_skill_batch_manifest(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Skill batch manifest is malformed: {path}")
    return payload


def build_variant_lookup(skill_manifest: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {
        "single-model-baseline": {
            "variant_id": "single-model-baseline",
            "description": "Baseline reasoning-mode run without an env-targeted Hermes skill prompt.",
            "routing": {},
        }
    }
    for item in skill_manifest.get("evolution_variants", []):
        if not isinstance(item, dict):
            continue
        variant_id = str(item.get("variant_id", "")).strip()
        if not variant_id:
            continue
        lookup[variant_id] = item
    return lookup


def resolve_variant_binding(
    env_id: str,
    variant_spec: Dict[str, Any],
    skill_manifest: Dict[str, Any],
    *,
    role_imprint_path: str = "",
    enable_role_gate: bool = True,
) -> Optional[Dict[str, Any]]:
    variant_id = str(variant_spec.get("variant_id", "")).strip() or "single-model-baseline"
    if variant_id == "single-model-baseline":
        return {
            "variant_id": variant_id,
            "skill_name": "",
            "skill_cluster": "",
            "prompt_builder": "",
            "role_mode": "",
            "role_support_tier": "",
            "role_gate_applied": False,
            "role_gate_downgraded": False,
            "role_gate_reason": "",
        }

    routing = variant_spec.get("routing", {})
    env_clusters = skill_manifest.get("env_clusters", {})
    skills = skill_manifest.get("skills", {})
    if not isinstance(routing, dict) or not isinstance(env_clusters, dict) or not isinstance(skills, dict):
        return None

    candidates: List[Tuple[int, str, str]] = []
    for cluster_name, skill_name in routing.items():
        cluster_envs = env_clusters.get(cluster_name, [])
        if not isinstance(cluster_envs, list):
            continue
        if env_id in {str(item).strip() for item in cluster_envs if str(item).strip()}:
            candidates.append((CLUSTER_PRIORITY.get(str(cluster_name), 999), str(cluster_name), str(skill_name)))
    if not candidates:
        return None

    _, cluster_name, skill_name = sorted(candidates, key=lambda item: (item[0], item[1], item[2]))[0]
    skill_spec = skills.get(skill_name, {})
    if not isinstance(skill_spec, dict):
        return None
    prompt_builder = str(skill_spec.get("prompt_builder", "")).strip()
    if not prompt_builder:
        return None
    role_gate = load_cluster_role_gate(cluster_name, role_imprint_path=role_imprint_path) if enable_role_gate else {}
    role_mode = str(role_gate.get("role_mode") or "")
    support_tier = str(role_gate.get("support_tier") or "")
    action_oriented_cluster = bool(role_gate.get("action_oriented_cluster"))
    allow_action = bool(role_gate.get("allow_action"))
    role_gate_downgraded = bool(enable_role_gate and action_oriented_cluster and not allow_action)
    role_gate_reason = ""
    downgraded_prompt_builder = prompt_builder
    downgraded_skill_name = skill_name
    downgraded_skill_cluster = cluster_name
    if role_gate_downgraded:
        role_gate_reason = (
            f"cluster {cluster_name} is action-oriented but support tier {support_tier or 'unknown'} "
            "is not action-support capable yet; downgraded to baseline"
        )
        downgraded_prompt_builder = ""
        downgraded_skill_name = ""
        downgraded_skill_cluster = ""
    return {
        "variant_id": variant_id,
        "skill_name": downgraded_skill_name,
        "skill_cluster": downgraded_skill_cluster,
        "prompt_builder": downgraded_prompt_builder,
        "role_mode": role_mode,
        "role_support_tier": support_tier,
        "role_gate_applied": bool(enable_role_gate),
        "role_gate_downgraded": role_gate_downgraded,
        "role_gate_reason": role_gate_reason,
    }


def render_skill_prompt(
    prompt_builder: str,
    env_name: str,
    python_exec: str,
    cache: Dict[Tuple[str, str, str], str],
    role_mode: str = "",
) -> str:
    key = (prompt_builder, env_name, role_mode)
    if key in cache:
        return cache[key]
    cmd = [python_exec, prompt_builder, "--env-name", env_name]
    if role_mode:
        cmd.extend(["--role-mode", role_mode])
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"skill prompt builder failed for {prompt_builder} ({env_name}): "
            f"{(result.stderr or result.stdout or '').strip()[:500]}"
        )
    prompt = (result.stdout or "").strip()
    if not prompt:
        raise RuntimeError(f"skill prompt builder returned empty output for {prompt_builder} ({env_name})")
    cache[key] = prompt
    return prompt


def env_selector(envs: Iterable[Dict[str, Any]], args: argparse.Namespace) -> List[Dict[str, Any]]:
    selected: List[Dict[str, Any]] = []
    source_set = set(args.sources)
    pattern = re.compile(args.env_pattern) if args.env_pattern else None
    prefix = args.env_prefix
    include = set(args.include or [])
    exclude = set(args.exclude or [])
    for env in envs:
        env_id = str(env.get("env_id", ""))
        source = str(env.get("source", ""))
        if source_set and source not in source_set:
            continue
        if args.owner and str(env.get("owner", "")) not in set(args.owner):
            continue
        if include and env_id not in include:
            continue
        if env_id in exclude:
            continue
        if prefix and not env_id.startswith(prefix):
            continue
        if pattern and not pattern.search(env_id):
            continue
        selected.append(env)
    selected.sort(key=lambda e: (str(e.get("source", "")), str(e.get("env_id", ""))))
    return selected


def select_trajectory_env_ids(trajectory_envs: Iterable[str], args: argparse.Namespace) -> List[str]:
    env_set = set(str(item).strip() for item in trajectory_envs if str(item).strip())
    if not env_set:
        return []
    include = set(args.include or [])
    exclude = set(args.exclude or [])
    prefix = args.env_prefix
    pattern = re.compile(args.env_pattern) if args.env_pattern else None
    selected = []
    for env_id in sorted(env_set):
        if include and env_id not in include:
            continue
        if env_id in exclude:
            continue
        if prefix and not env_id.startswith(prefix):
            continue
        if pattern and not pattern.search(env_id):
            continue
        selected.append(env_id)
    return selected


@dataclass(frozen=True)
class ModelProfile:
    model_id: str
    base_url: str
    model_name: str
    max_new_tokens: int
    temperature: float
    top_p: float
    request_timeout: int = 120


def default_models(args: argparse.Namespace) -> List[ModelProfile]:
    requested = set(args.model)
    result: List[ModelProfile] = []
    if "9b" in requested:
        result.append(
            ModelProfile(
                model_id="qwen35_9b",
                base_url=args.base_url_9b,
                model_name=args.model_name_9b,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                request_timeout=args.request_timeout,
            )
        )
    if "27b" in requested:
        result.append(
            ModelProfile(
                model_id="qwen35_27b",
                base_url=args.base_url_27b,
                model_name=args.model_name_27b,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                top_p=args.top_p,
                request_timeout=args.request_timeout,
            )
        )
    if not result:
        raise ValueError("No models selected; pass --model 9b and/or 27b.")
    return result


def model_key(model: ModelProfile, variant_id: str, env_id: str) -> str:
    return f"{model.model_id}:{variant_id}:{env_id}"


def resolve_reasoning_mode(env_id: str, requested_reasoning_mode: str) -> str:
    mode = str(requested_reasoning_mode or "").strip().lower()
    if mode in {"", "off", "false", "0"}:
        return "off"
    if env_id in FORCE_DIRECT_OUTPUT_ENVS:
        return "off"
    return mode


def resolve_max_new_tokens(env_id: str, requested_max_new_tokens: int) -> int:
    floor = int(MIN_COMPLETION_TOKENS_BY_ENV.get(env_id, 0))
    return max(int(requested_max_new_tokens), floor)


def resolve_request_timeout(env_id: str, requested_request_timeout: int) -> int:
    floor = int(MIN_REQUEST_TIMEOUT_BY_ENV.get(env_id, 0))
    return max(int(requested_request_timeout), floor)


def completed_runs(ledger_path: Path) -> set[str]:
    done = set()
    for row in read_jsonl(ledger_path):
        if row.get("status") == "success":
            key = row.get("task_key")
            if isinstance(key, str):
                done.add(key)
    return done


def probe_endpoint(base_url: str, timeout_sec: int = 8) -> bool:
    candidates = []
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        candidates.append(f"{base}/health")
        candidates.append(f"{base}/models")
    else:
        candidates.append(f"{base}/health")
        candidates.append(f"{base}/v1/health")
        candidates.append(f"{base}/v1/models")
    for url in candidates:
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                if 200 <= int(response.status) < 400:
                    return True
        except Exception:
            continue
    return False


def check_primehub_cli(command_tpl: List[str], timeout_sec: int = 8) -> Tuple[bool, str]:
    if not command_tpl:
        return False, "empty command template"
    interpreter = command_tpl[0]
    interp_path = Path(interpreter)
    if interpreter.endswith(".exe") and not interp_path.exists():
        return False, f"interpreter not found: {interpreter}"
    if not interpreter.endswith(".exe") and shutil.which(interpreter) is None and not interp_path.exists():
        return False, f"interpreter not found: {command_tpl[0]}"
    probe_cmd = command_tpl[:]
    if "--help" not in probe_cmd:
        probe_cmd.append("--help")
    try:
        result = subprocess.run(
            probe_cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        if result.returncode == 0:
            return True, "ok"
        return False, (result.stderr or result.stdout or "probe returned non-zero").strip()[:500]
    except Exception as exc:
        return False, str(exc)


def build_config(
    model: ModelProfile,
    env_id: str,
    env_name: str,
    env_source: str,
    env_owner: str,
    env_folder: str,
    export_path: Path,
    python_exec: str,
    command_template: str,
    env_mode: str = "primehub",
    trajectory_root: Optional[Path] = None,
    variant_id: str = "single-model-baseline",
    reasoning_mode: str = "off",
    skill_name: str = "",
    skill_prompt: str = "",
    skill_cluster: str = "",
    role_mode: str = "",
    role_support_tier: str = "",
    role_gate_applied: bool = False,
    role_gate_downgraded: bool = False,
    role_gate_reason: str = "",
) -> Dict[str, Any]:
    export_path = Path(export_path).resolve()
    effective_max_new_tokens = resolve_max_new_tokens(env_id, model.max_new_tokens)
    effective_request_timeout = resolve_request_timeout(env_id, model.request_timeout)
    trace_profile_overrides: Dict[str, Any] = {}
    if reasoning_mode:
        trace_profile_overrides["reasoning_mode"] = reasoning_mode
    if skill_name:
        trace_profile_overrides["skill_name"] = skill_name
    if skill_prompt:
        trace_profile_overrides["skill_prompt"] = skill_prompt
    if skill_cluster:
        trace_profile_overrides["skill_cluster"] = skill_cluster
    if role_mode:
        trace_profile_overrides["role_mode"] = role_mode
    if role_support_tier:
        trace_profile_overrides["role_support_tier"] = role_support_tier
    if role_gate_applied:
        trace_profile_overrides["role_gate_applied"] = role_gate_applied
    if role_gate_downgraded:
        trace_profile_overrides["role_gate_downgraded"] = role_gate_downgraded
    if role_gate_reason:
        trace_profile_overrides["role_gate_reason"] = role_gate_reason
    if variant_id:
        trace_profile_overrides["variant_id"] = variant_id
    envs: List[Dict[str, Any]]
    if env_mode == "trajectory":
        source_path = Path(trajectory_root or Path(".")).resolve() / f"{env_id}.jsonl"
        envs = [
            {
                "type": "jsonl_trajectory",
                "name": env_name,
                "source_path": str(source_path),
                "reasoning_mode": reasoning_mode,
                "trace_profile_overrides": trace_profile_overrides,
            }
        ]
    else:
        command = render_primehub_command(
            command_template,
            python_exec,
            {
                "env_id": env_id,
                "source": env_source,
                "owner": env_owner,
                "folder": env_folder,
                "command_name": env_name,
            },
        )
        envs = [
            {
                "type": "primehub_external",
                "name": env_name,
                "command_template": command,
                "reset_args": ["--reset"],
                "trace_profile_overrides": trace_profile_overrides,
            }
        ]
    return {
        "run_name": f"overnight-{model.model_id}-{normalize_slug(variant_id)}-{env_id}",
        "max_episodes": 1,
        "max_steps_per_episode": 8,
        "export_path": str(export_path),
        "model": {
            "provider": "openai_compatible",
            "base_url": model.base_url,
            "model_name": model.model_name,
            "max_new_tokens": effective_max_new_tokens,
            "temperature": model.temperature,
            "top_p": model.top_p,
            "request_timeout": effective_request_timeout,
        },
        "metadata": {
            "variant_id": variant_id,
            "skill_name": skill_name,
            "skill_cluster": skill_cluster,
            "role_mode": role_mode,
            "role_support_tier": role_support_tier,
            "role_gate_applied": role_gate_applied,
            "role_gate_downgraded": role_gate_downgraded,
            "role_gate_reason": role_gate_reason,
            "requested_max_new_tokens": model.max_new_tokens,
            "max_new_tokens": effective_max_new_tokens,
            "requested_request_timeout": model.request_timeout,
            "request_timeout": effective_request_timeout,
            "reasoning_mode": reasoning_mode,
        },
        "envs": [
            *envs
        ],
    }


def run_one_task(
    trm_root: Path,
    python_exec: str,
    config_path: Path,
    config_obj: Dict[str, Any],
    export_path: Path,
    episodes: int,
    token_budget: Optional[int],
    task_key: str,
    task_timeout: int,
) -> Tuple[bool, Dict[str, Any], str, str]:
    def _tail(text: str, *, max_chars: int = 2000) -> str:
        return (text or "")[-max_chars:]

    config_path = Path(config_path).resolve()
    export_path = Path(export_path).resolve()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(config_obj, handle, indent=2, ensure_ascii=True)

    run_eval = trm_root / "scripts" / "run_eval.py"
    cmd = [
        python_exec,
        str(run_eval),
        "--config",
        str(config_path),
        "--fixed-output-path",
        "--run-id",
        task_key.replace(":", "_"),
    ]
    if token_budget is not None:
        cmd += ["--token-budget", str(token_budget)]
    cmd += ["--episodes", str(max(1, episodes))]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(trm_root),
            capture_output=True,
            text=True,
            errors="replace",
            timeout=task_timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return (
            False,
            {"status": "timeout", "error": f"task timed out after {task_timeout}s"},
            "",
            "",
        )
    except Exception as exc:  # pragma: no cover - defensive
        return False, {"status": "execution_error", "error": str(exc)}, "", ""

    payload = {
        "status": "success" if result.returncode == 0 else "failed",
        "returncode": result.returncode,
        "cmd": cmd,
        "stdout_tail": _tail(result.stdout or ""),
        "stderr_tail": _tail(result.stderr or ""),
    }
    if result.returncode != 0:
        return False, payload, result.stdout or "", result.stderr or ""

    summary_path = export_path.with_suffix(".summary.json")
    if not summary_path.exists():
        return False, {"status": "missing_summary", **payload}, result.stdout or "", result.stderr or ""
    try:
        summary = read_json(summary_path)
    except json.JSONDecodeError as exc:
        return False, {"status": "invalid_summary", "error": f"invalid summary JSON: {exc}"}, result.stdout or "", result.stderr or ""
    except OSError as exc:  # pragma: no cover - defensive
        return False, {"status": "unreadable_summary", "error": str(exc)}, result.stdout or "", result.stderr or ""

    failure_types = _as_int_mapping(summary.get("failure_types"))
    if failure_types:
        payload = {
            "status": "execution_failure",
            "returncode": result.returncode,
            "failure_types": failure_types,
            "failure_count": int(sum(failure_types.values())),
            "stderr_tail": (result.stderr or "")[-2000:],
            "stdout_tail": (result.stdout or "")[-2000:],
        }
        return False, payload, result.stdout or "", result.stderr or ""

    return (
        True,
        {
            "status": "success",
            "summary": summary,
            "returncode": result.returncode,
            "stdout_tail": (result.stdout or "")[-2000:],
            "stderr_tail": (result.stderr or "")[-2000:],
        },
        result.stdout or "",
        result.stderr or "",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark Hermes/TRM harness on Prime Intellect envs.")
    parser.add_argument("--trm-root", default=str(DEFAULT_TRM_ROOT))
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--skill-batch-manifest", default=str(DEFAULT_SKILL_BATCH_MANIFEST))
    parser.add_argument("--role-imprint-json", default=str(DEFAULT_ROLE_IMPRINT))
    parser.add_argument("--disable-role-gate", action="store_true", help="Do not consult role-based TRM support tiers during skill binding.")
    parser.add_argument("--refresh-manifest", action="store_true", help="Rebuild manifest from local/remote env catalogs.")
    parser.add_argument("--research-root", default=str(DEFAULT_RESEARCH_ENV_ROOT))
    parser.add_argument("--research-api", default=DEFAULT_RESEARCH_API, help="GitHub API for Prime Intellect research envs.")
    parser.add_argument("--community-api", default=DEFAULT_COMMUNITY_API, help="GitHub API for community envs.")
    parser.add_argument("--run-root", default=str(DEFAULT_RUN_ROOT))
    parser.add_argument("--stout", default="", help="Path to stout JSONL log. Defaults to run-root/stout.jsonl.")
    parser.add_argument("--ledger", default="", help="Path to jsonl ledger. Defaults to run-root/ledger.jsonl.")
    parser.add_argument("--python", default=sys.executable, dest="python_exec")
    parser.add_argument(
        "--primehub-cmd",
        default=DEFAULT_PRIMEHUB_CMD,
        help=(
            "Template command used to invoke PrimeHub envs. "
            "Available placeholders: {python_exec}, {env_id}, {env_source}, {env_owner}, {env_folder}, {command_name}."
        ),
    )
    parser.add_argument("--model", nargs="+", default=["9b", "27b"], choices=["9b", "27b"])
    parser.add_argument(
        "--variant",
        nargs="+",
        default=list(DEFAULT_VARIANT_IDS),
        help="Benchmark variant ids from the skill batch manifest. Include single-model-baseline for the no-skill arm.",
    )
    parser.add_argument("--base-url-9b", default=DEFAULT_9B_URL)
    parser.add_argument("--base-url-27b", default=DEFAULT_27B_URL)
    parser.add_argument("--model-name-9b", default="Qwen_Qwen3.5-9B-Q4_K_M.gguf")
    parser.add_argument("--model-name-27b", default="Qwen3.5-27B.Q4_K_M.gguf")
    parser.add_argument("--max-new-tokens", type=int, default=64)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--episodes", type=int, default=1)
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--token-budget", type=int, default=None)
    parser.add_argument("--task-timeout-seconds", type=int, default=600)
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=120,
        help="Per-request timeout passed to OpenAI-compatible endpoints.",
    )
    parser.add_argument("--max-tasks", type=int, default=None)
    parser.add_argument("--sources", nargs="+", default=["research", "community"])
    parser.add_argument("--owner", nargs="*", default=None)
    parser.add_argument("--env-prefix", default="")
    parser.add_argument("--env-pattern", default="")
    parser.add_argument("--include", nargs="*", default=None)
    parser.add_argument("--exclude", nargs="*", default=None)
    parser.add_argument(
        "--env-mode",
        default=DEFAULT_ENV_MODE,
        choices=["auto", "primehub", "trajectory"],
        help="Env execution mode. auto prefers primehub if available, otherwise trajectory replay envs.",
    )
    parser.add_argument(
        "--trajectory-root",
        default=str(DEFAULT_TRAJECTORY_ROOT),
        help="Root folder for jsonl trajectory env data (used in trajectory mode).",
    )
    parser.add_argument(
        "--trajectory-manifest",
        default=DEFAULT_TRAJECTORY_MANIFEST,
        help="Optional JSON manifest with {\"envs\": [...]} list for trajectory mode.",
    )
    parser.add_argument(
        "--trajectory-excludes",
        nargs="*",
        default=sorted(DEFAULT_TRAJECTORY_EXCLUDES),
        help="Env ids to exclude from trajectory mode when auto-discovering files.",
    )
    parser.add_argument("--endpoint-probe-timeout", type=int, default=8)
    parser.add_argument(
        "--reasoning-mode",
        default="off",
        choices=["off", "on"],
        help="Reasoning mode hint injected into the trace profile for all tasks.",
    )
    parser.add_argument("--skip-once-start", action="store_true", help="Stop immediately if endpoint/cli is unavailable.")
    parser.add_argument("--force-rerun", action="store_true", help="Ignore ledger and rerun completed tasks.")
    parser.add_argument("--max-runtime-minutes", type=float, default=None)
    parser.add_argument("--skip-cli-check", action="store_true", help="Skip prime_env_hub.cli availability check.")
    parser.add_argument("--skip-endpoint-check", action="store_true", help="Skip remote endpoint health checks.")
    parser.add_argument("--dry-run", action="store_true", help="Build task list and write logs, but do not run tasks.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    trm_root = Path(args.trm_root).resolve()
    run_root = Path(args.run_root).resolve()
    research_root = Path(args.research_root).resolve()
    skill_manifest_path = Path(args.skill_batch_manifest).resolve()
    role_imprint_path = Path(args.role_imprint_json).resolve() if args.role_imprint_json else Path("")
    stout_path = Path(args.stout).resolve() if args.stout else (run_root / "overnight_primehub_benchmark.stout.jsonl")
    ledger_path = Path(args.ledger).resolve() if args.ledger else (run_root / "ledger.jsonl")
    manifest_path = Path(args.manifest).resolve()
    if not trm_root.exists():
        append_jsonl(
            stout_path,
            {
                "ts": now_ts(),
                "event": "run_error",
                "error": f"trm root missing: {trm_root}",
            },
        )
        return 2

    append_jsonl(
        stout_path,
        {
            "ts": now_ts(),
            "event": "run_start",
            "python": args.python_exec,
            "trm_root": str(trm_root.resolve()),
            "run_root": str(run_root.resolve()),
            "manifest": str(manifest_path.resolve()),
            "skill_batch_manifest": str(skill_manifest_path),
            "role_imprint_json": str(role_imprint_path) if args.role_imprint_json else "",
            "role_gate_enabled": not args.disable_role_gate,
            "research_root": str(research_root.resolve()),
            "research_api": args.research_api,
            "community_api": args.community_api,
            "requested_env_mode": args.env_mode,
            "requested_variants": list(args.variant),
            "reasoning_mode": args.reasoning_mode,
            "primehub_cmd": args.primehub_cmd,
            "trajectory_root": str(Path(args.trajectory_root).resolve()),
            "trajectory_manifest": args.trajectory_manifest,
        },
    )

    run_eval_script = trm_root / "scripts" / "run_eval.py"
    if not run_eval_script.exists():
        append_jsonl(stout_path, {"ts": now_ts(), "event": "run_error", "error": f"missing run_eval.py at {run_eval_script}"})
        return 2

    if not manifest_path.exists() or args.refresh_manifest:
        existing_profiles: List[Dict[str, Any]] = []
        if manifest_path.exists():
            try:
                existing_profiles = load_manifest(manifest_path)
            except Exception as exc:
                append_jsonl(
                    stout_path,
                    {
                        "ts": now_ts(),
                        "event": "manifest_warn",
                        "warning": f"existing manifest malformed: {exc}",
                    },
                )
        manifest = build_manifest(
            existing_profiles,
            research_root=research_root,
            community_api=args.community_api,
            research_api=args.research_api,
        )
        write_json(manifest_path, manifest)
        profiles = manifest["profiles"]
    else:
        profiles = load_manifest(manifest_path)

    skill_manifest = load_skill_batch_manifest(skill_manifest_path)
    variant_lookup = build_variant_lookup(skill_manifest)
    selected_variants: List[Dict[str, Any]] = []
    for variant_id in args.variant or DEFAULT_VARIANT_IDS:
        variant_key = str(variant_id).strip()
        if not variant_key:
            continue
        spec = variant_lookup.get(variant_key)
        if spec is None:
            append_jsonl(
                stout_path,
                {
                    "ts": now_ts(),
                    "event": "variant_warn",
                    "variant_id": variant_key,
                    "warning": "variant not found in skill manifest; skipping",
                },
            )
            continue
        selected_variants.append(spec)
    if not selected_variants:
        append_jsonl(
            stout_path,
            {
                "ts": now_ts(),
                "event": "run_error",
                "error": "no benchmark variants selected",
            },
        )
        return 2

    models = default_models(args)
    selected_envs = env_selector(profiles, args)
    trajectory_root = Path(args.trajectory_root).resolve()
    trajectory_manifest = load_trajectory_manifest(Path(args.trajectory_manifest)) if args.trajectory_manifest else []
    trajectory_env_set = set(
        discover_trajectory_envs(
            trajectory_root,
            trajectory_manifest,
            args.trajectory_excludes,
        )
    )
    trajectory_env_ids = select_trajectory_env_ids(trajectory_env_set, args)
    trajectory_selected = [
        {"env_id": env_id, "source": "trajectory", "owner": "local_trajectory", "command_name": env_id}
        for env_id in trajectory_env_ids
    ]
    if args.env_mode == "trajectory":
        selected_envs = trajectory_selected

    if args.max_tasks is not None:
        selected_envs = selected_envs[: args.max_tasks]
        if args.env_mode == "trajectory":
            trajectory_selected = selected_envs
        elif not selected_envs:
            trajectory_selected = trajectory_selected[: args.max_tasks]
        elif selected_envs:
            selected_ids = {str(env.get("env_id", "")) for env in selected_envs}
            trajectory_selected = [
                env
                for env in trajectory_selected
                if str(env.get("env_id", "")) in selected_ids
            ]

    if args.env_mode == "trajectory" and not trajectory_selected:
        append_jsonl(
            stout_path,
            {
                "ts": now_ts(),
                "event": "run_error",
                "error": "no environments available for trajectory mode",
                "requested": len(selected_envs),
                "trajectory_source_count": len(trajectory_env_set),
                "trajectory_root": str(trajectory_root),
            },
        )
        return 2

    if not selected_envs and args.env_mode == "auto" and trajectory_selected:
        selected_envs = trajectory_selected
        trajectory_fallback_mode = True
        append_jsonl(
            stout_path,
            {
                "ts": now_ts(),
                "event": "env_selection_fallback",
                "reason": "selected from trajectory because prime env manifest was empty",
                "fallback_count": len(selected_envs),
            },
        )

    if not selected_envs:
        append_jsonl(stout_path, {"ts": now_ts(), "event": "run_error", "error": "no environments selected"})
        return 2

    append_jsonl(
        stout_path,
        {
            "ts": now_ts(),
            "event": "run_envs_resolved",
            "selected_envs": len(selected_envs),
            "trajectory_selected": len(trajectory_selected),
            "selected_env_ids": [str(item.get("env_id", "")) for item in selected_envs[:20]],
            "selected_variant_ids": [str(item.get("variant_id", "")) for item in selected_variants],
            "trajectory_root": str(trajectory_root),
            "trajectory_manifest": args.trajectory_manifest,
        },
    )

    done = set()
    if not args.force_rerun:
        done = completed_runs(ledger_path)

    binding_cache: Dict[str, List[Dict[str, Any]]] = {}

    def bindings_for_env(env_id: str) -> List[Dict[str, Any]]:
        cached = binding_cache.get(env_id)
        if cached is not None:
            return cached
        resolved: List[Dict[str, Any]] = []
        for variant_spec in selected_variants:
            binding = resolve_variant_binding(
                env_id,
                variant_spec,
                skill_manifest,
                role_imprint_path=str(role_imprint_path) if args.role_imprint_json else "",
                enable_role_gate=not args.disable_role_gate,
            )
            if binding is not None:
                resolved.append(binding)
        binding_cache[env_id] = resolved
        return resolved

    tasks: List[Tuple[ModelProfile, Dict[str, Any], str, Dict[str, Any]]] = []
    skipped = 0
    cli_probe_cmd = (
        render_primehub_command(
            args.primehub_cmd,
            args.python_exec,
            {
                "env_id": "probe",
                "source": "research",
                "owner": "primeintellect",
                "folder": "probe",
                "command_name": "probe",
            },
        )
        if args.env_mode in {"auto", "primehub"}
        else []
    )
    trajectory_fallback_mode = False
    cli_check_result: Tuple[bool, str] | None = None
    if args.env_mode in {"auto", "primehub"} and not args.skip_cli_check and not cli_probe_cmd:
        cli_probe_msg = "invalid --primehub-cmd after render"
        cli_check_result = (False, cli_probe_msg)

    total_selected = len(selected_envs)
    for model in models:
        cli_ok, cli_msg = (True, "skipped")
        if args.skip_cli_check:
            cli_msg = "skipped via --skip-cli-check"
            if args.env_mode == "primehub":
                cli_ok = True
            elif args.env_mode == "auto":
                cli_ok = True
        else:
            if args.env_mode in {"auto", "primehub"}:
                if cli_check_result is None:
                    if cli_probe_cmd:
                        cli_check_result = check_primehub_cli(
                            cli_probe_cmd,
                            args.endpoint_probe_timeout,
                        )
                    else:
                        cli_check_result = (False, "invalid --primehub-cmd after render")
                cli_ok, cli_msg = cli_check_result
            else:
                cli_ok, cli_msg = (True, "trajectory-only mode")
        model_available = True
        if args.skip_endpoint_check:
            model_available = True
            endpoint_msg = "skipped via --skip-endpoint-check"
        else:
            model_available = probe_endpoint(model.base_url, args.endpoint_probe_timeout)
            endpoint_msg = "reachable" if model_available else "unreachable"

        effective_mode = args.env_mode
        if args.env_mode == "auto":
            if trajectory_fallback_mode:
                effective_mode = "trajectory"
            elif cli_ok:
                effective_mode = "primehub"
            elif trajectory_selected:
                effective_mode = "trajectory"
            else:
                effective_mode = "primehub"

        run_envs = selected_envs if effective_mode == "primehub" else trajectory_selected
        missing_envs: List[Dict[str, Any]] = []
        if effective_mode == "trajectory":
            missing_envs = [env for env in selected_envs if env not in run_envs]

        no_trajectory_data = effective_mode == "trajectory" and len(run_envs) == 0
        mode_blocked = (
            (effective_mode == "primehub" and args.env_mode == "primehub" and not cli_ok)
            or (effective_mode == "primehub" and args.env_mode == "auto" and not cli_ok and not trajectory_selected)
            or (not model_available)
            or no_trajectory_data
        )

        if args.skip_once_start and mode_blocked:
            append_jsonl(
                stout_path,
                {
                    "ts": now_ts(),
                    "event": "run_abort",
                    "reason": "skip_once_start",
                    "model_id": model.model_id,
                    "cli_ok": cli_ok,
                    "endpoint_ok": model_available,
                    "cli_message": cli_msg,
                    "endpoint_message": endpoint_msg,
                    "effective_env_mode": effective_mode,
                    "requested_mode": args.env_mode,
                },
            )
            return 2

        if not model_available:
            for env in selected_envs:
                env_id = str(env.get("env_id", ""))
                for binding in bindings_for_env(env_id):
                    variant_id = binding["variant_id"]
                    key = model_key(model, variant_id, env_id)
                    if args.force_rerun or key not in done:
                        entry = {
                            "ts": now_ts(),
                            "event": "task_skipped",
                            "status": "skipped",
                            "task_key": key,
                            "variant_id": variant_id,
                            "skill_name": binding.get("skill_name", ""),
                            "skill_cluster": binding.get("skill_cluster", ""),
                            "role_mode": binding.get("role_mode", ""),
                            "role_support_tier": binding.get("role_support_tier", ""),
                            "role_gate_applied": binding.get("role_gate_applied", False),
                            "role_gate_downgraded": binding.get("role_gate_downgraded", False),
                            "role_gate_reason": binding.get("role_gate_reason", ""),
                            "model_id": model.model_id,
                            "env_id": env_id,
                            "env_source": str(env.get("source", "")),
                            "env_owner": str(env.get("owner", "")),
                            "env_mode": effective_mode,
                            "requested_mode": args.env_mode,
                            "skip_reason": "endpoint_unavailable",
                            "cli_message": cli_msg,
                            "endpoint_message": endpoint_msg,
                            "endpoint": model.base_url,
                            "endpoint_ok": model_available,
                        }
                        append_jsonl(ledger_path, entry)
                        skipped += 1
            continue

        if effective_mode == "primehub" and not cli_ok:
            for env in selected_envs:
                env_id = str(env.get("env_id", ""))
                for binding in bindings_for_env(env_id):
                    variant_id = binding["variant_id"]
                    key = model_key(model, variant_id, env_id)
                    if args.force_rerun or key not in done:
                        entry = {
                            "ts": now_ts(),
                            "event": "task_skipped",
                            "status": "skipped",
                            "task_key": key,
                            "variant_id": variant_id,
                            "skill_name": binding.get("skill_name", ""),
                            "skill_cluster": binding.get("skill_cluster", ""),
                            "role_mode": binding.get("role_mode", ""),
                            "role_support_tier": binding.get("role_support_tier", ""),
                            "role_gate_applied": binding.get("role_gate_applied", False),
                            "role_gate_downgraded": binding.get("role_gate_downgraded", False),
                            "role_gate_reason": binding.get("role_gate_reason", ""),
                            "model_id": model.model_id,
                            "env_id": env_id,
                            "env_source": str(env.get("source", "")),
                            "env_owner": str(env.get("owner", "")),
                            "env_mode": effective_mode,
                            "requested_mode": args.env_mode,
                            "skip_reason": "primehub_cli_unavailable",
                            "cli_message": cli_msg,
                            "endpoint_message": endpoint_msg,
                            "endpoint": model.base_url,
                            "endpoint_ok": model_available,
                        }
                        append_jsonl(ledger_path, entry)
                        skipped += 1
            continue

        if missing_envs:
            for env in missing_envs:
                env_id = str(env.get("env_id", ""))
                for binding in bindings_for_env(env_id):
                    variant_id = binding["variant_id"]
                    key = model_key(model, variant_id, env_id)
                    if not (not args.force_rerun and key in done):
                        entry = {
                            "ts": now_ts(),
                            "event": "task_skipped",
                            "status": "skipped",
                            "task_key": key,
                            "variant_id": variant_id,
                            "skill_name": binding.get("skill_name", ""),
                            "skill_cluster": binding.get("skill_cluster", ""),
                            "role_mode": binding.get("role_mode", ""),
                            "role_support_tier": binding.get("role_support_tier", ""),
                            "role_gate_applied": binding.get("role_gate_applied", False),
                            "role_gate_downgraded": binding.get("role_gate_downgraded", False),
                            "role_gate_reason": binding.get("role_gate_reason", ""),
                            "model_id": model.model_id,
                            "env_id": env_id,
                            "env_source": str(env.get("source", "")),
                            "env_owner": str(env.get("owner", "")),
                            "env_mode": effective_mode,
                            "requested_mode": args.env_mode,
                            "skip_reason": "trajectory_missing",
                            "cli_message": cli_msg,
                            "endpoint_message": endpoint_msg,
                            "endpoint": model.base_url,
                            "endpoint_ok": model_available,
                        }
                        append_jsonl(ledger_path, entry)
                        skipped += 1

        for env in run_envs:
            env_id = str(env.get("env_id", ""))
            for binding in bindings_for_env(env_id):
                variant_id = binding["variant_id"]
                key = model_key(model, variant_id, env_id)
                if (not args.force_rerun) and key in done:
                    continue
                tasks.append((model, env, effective_mode, binding))

    if not tasks:
        append_jsonl(
            stout_path,
            {
                "ts": now_ts(),
                "event": "run_complete",
                "status": "nothing_to_run",
                "tasks_requested": 0,
                "tasks_scheduled": 0,
                "tasks_skipped": skipped,
                "tasks_executed": 0,
                "selected_envs": total_selected,
            },
        )
        return 0

    if args.dry_run:
        for model, env, effective_mode, binding in tasks:
            env_id = str(env.get("env_id", ""))
            variant_id = binding["variant_id"]
            key = model_key(model, variant_id, env_id)
            reasoning_mode = resolve_reasoning_mode(env_id, args.reasoning_mode)
            max_new_tokens = resolve_max_new_tokens(env_id, model.max_new_tokens)
            request_timeout = resolve_request_timeout(env_id, model.request_timeout)
            row = {
                "ts": now_ts(),
                "event": "task_complete",
                "status": "dry_run",
                "task_key": key,
                "variant_id": variant_id,
                "skill_name": binding.get("skill_name", ""),
                "skill_cluster": binding.get("skill_cluster", ""),
                "role_mode": binding.get("role_mode", ""),
                "role_support_tier": binding.get("role_support_tier", ""),
                "role_gate_applied": binding.get("role_gate_applied", False),
                "role_gate_downgraded": binding.get("role_gate_downgraded", False),
                "role_gate_reason": binding.get("role_gate_reason", ""),
                "model_id": model.model_id,
                "env_id": env_id,
                "base_url": model.base_url,
                "env_mode": effective_mode,
                "env_source": str(env.get("source", "")),
                "env_owner": str(env.get("owner", "")),
                "episodes": args.episodes,
                "requested_max_new_tokens": model.max_new_tokens,
                "max_new_tokens": max_new_tokens,
                "requested_request_timeout": model.request_timeout,
                "request_timeout": request_timeout,
                "requested_reasoning_mode": args.reasoning_mode,
                "reasoning_mode": reasoning_mode,
            }
            append_jsonl(ledger_path, row)
            append_jsonl(stout_path, row)

        append_jsonl(
            stout_path,
            {
                "ts": now_ts(),
                "event": "run_complete",
                "status": "dry_run",
                "tasks_requested": len(tasks),
                "tasks_scheduled": len(tasks),
                "tasks_executed": 0,
                "tasks_failed": 0,
                "tasks_skipped": skipped,
            },
        )
        return 0

    deadline = now_ts() + (args.max_runtime_minutes * 60 if args.max_runtime_minutes else float("inf"))
    total = len(tasks)
    done_count = 0
    failed_count = 0
    prompt_cache: Dict[Tuple[str, str, str], str] = {}

    append_jsonl(stout_path, {"ts": now_ts(), "event": "tasks_scheduled", "count": total})

    for idx, (model, env, effective_mode, binding) in enumerate(tasks, start=1):
        if now_ts() >= deadline:
            append_jsonl(stout_path, {"ts": now_ts(), "event": "runtime_limit_reached"})
            break

        env_id = str(env.get("env_id", ""))
        env_name = str(env.get("command_name", env_id))
        variant_id = binding["variant_id"]
        task_key = model_key(model, variant_id, env_id)
        run_id = f"{model.model_id}_{normalize_slug(variant_id)}_{env_id}_q{idx:04d}"
        task_root = run_root / model.model_id
        task_root.mkdir(parents=True, exist_ok=True)
        config_path = task_root / f"{run_id}.config.json"
        export_path = task_root / f"{run_id}.jsonl"
        skill_name = str(binding.get("skill_name", "")).strip()
        skill_cluster = str(binding.get("skill_cluster", "")).strip()
        role_mode = str(binding.get("role_mode", "")).strip()
        role_support_tier = str(binding.get("role_support_tier", "")).strip()
        role_gate_applied = bool(binding.get("role_gate_applied"))
        role_gate_downgraded = bool(binding.get("role_gate_downgraded"))
        role_gate_reason = str(binding.get("role_gate_reason", "")).strip()
        reasoning_mode = resolve_reasoning_mode(env_id, args.reasoning_mode)
        max_new_tokens = resolve_max_new_tokens(env_id, model.max_new_tokens)
        request_timeout = resolve_request_timeout(env_id, model.request_timeout)
        skill_prompt = ""
        prompt_builder = str(binding.get("prompt_builder", "")).strip()
        if role_gate_downgraded:
            append_jsonl(
                stout_path,
                {
                    "ts": now_ts(),
                    "event": "skill_binding_downgraded",
                    "task_key": task_key,
                    "run_id": run_id,
                    "variant_id": variant_id,
                    "env_id": env_id,
                    "model_id": model.model_id,
                    "role_mode": role_mode,
                    "role_support_tier": role_support_tier,
                    "reason": role_gate_reason,
                },
            )
        if prompt_builder:
            try:
                skill_prompt = render_skill_prompt(
                    prompt_builder=prompt_builder,
                    env_name=env_id,
                    python_exec=args.python_exec,
                    cache=prompt_cache,
                    role_mode=role_mode,
                )
            except Exception as exc:
                failed_count += 1
                row = {
                    "ts": now_ts(),
                    "event": "task_complete",
                    "status": "skill_prompt_error",
                    "task_key": task_key,
                    "run_id": run_id,
                    "variant_id": variant_id,
                    "skill_name": skill_name,
                    "skill_cluster": skill_cluster,
                    "role_mode": role_mode,
                    "role_support_tier": role_support_tier,
                    "role_gate_applied": role_gate_applied,
                    "role_gate_downgraded": role_gate_downgraded,
                    "role_gate_reason": role_gate_reason,
                    "model_id": model.model_id,
                    "env_id": env_id,
                    "base_url": model.base_url,
                    "error": str(exc),
                    "config_path": str(config_path),
                    "export_path": str(export_path),
                    "summary_path": str(export_path.with_suffix(".summary.json")),
                }
                append_jsonl(ledger_path, row)
                append_jsonl(stout_path, row)
                continue

        config = build_config(
            model=model,
            env_id=env_id,
            env_name=env_name,
            env_source=str(env.get("source", "")),
            env_owner=str(env.get("owner", "")),
            env_folder=str(env.get("folder", "")),
            export_path=export_path,
            python_exec=args.python_exec,
            command_template=args.primehub_cmd,
            env_mode=effective_mode,
            trajectory_root=trajectory_root,
            variant_id=variant_id,
            reasoning_mode=reasoning_mode,
            skill_name=skill_name,
            skill_prompt=skill_prompt,
            skill_cluster=skill_cluster,
            role_mode=role_mode,
            role_support_tier=role_support_tier,
            role_gate_applied=role_gate_applied,
            role_gate_downgraded=role_gate_downgraded,
            role_gate_reason=role_gate_reason,
        )
        config["max_episodes"] = args.episodes
        config["max_steps_per_episode"] = args.max_steps
        config["episodes"] = args.episodes
        if effective_mode != "trajectory":
            rendered = render_primehub_command(args.primehub_cmd, args.python_exec, env)
            if rendered:
                config["envs"][0]["command_template"] = rendered
            config["envs"][0]["reset_args"] = ["--reset"]

        append_jsonl(
            stout_path,
            {
                "ts": now_ts(),
                "event": "task_start",
                "task_key": task_key,
                "run_id": run_id,
                "variant_id": variant_id,
                "skill_name": skill_name,
                "skill_cluster": skill_cluster,
                "role_mode": role_mode,
                "role_support_tier": role_support_tier,
                "role_gate_applied": role_gate_applied,
                "role_gate_downgraded": role_gate_downgraded,
                "role_gate_reason": role_gate_reason,
                "env_id": env_id,
                "model_id": model.model_id,
                "index": idx,
                "total": total,
                "run_root": str(run_root.resolve()),
                "env_source": str(env.get("source", "")),
                "env_owner": str(env.get("owner", "")),
                "base_url": model.base_url,
                "env_mode": effective_mode,
                "requested_max_new_tokens": model.max_new_tokens,
                "max_new_tokens": max_new_tokens,
                "requested_request_timeout": model.request_timeout,
                "request_timeout": request_timeout,
                "requested_reasoning_mode": args.reasoning_mode,
                "reasoning_mode": reasoning_mode,
            },
        )
        success, payload, _, _ = run_one_task(
            trm_root=trm_root,
            python_exec=args.python_exec,
            config_path=config_path,
            config_obj=config,
            episodes=args.episodes,
            export_path=export_path,
            token_budget=args.token_budget,
            task_key=task_key,
            task_timeout=args.task_timeout_seconds,
        )

        if success:
            done_count += 1
            summary = payload.get("summary", {})
            row = {
                "ts": now_ts(),
                "event": "task_complete",
                "status": "success",
                "task_key": task_key,
                "run_id": run_id,
                "variant_id": variant_id,
                "skill_name": skill_name,
                "skill_cluster": skill_cluster,
                "role_mode": role_mode,
                "role_support_tier": role_support_tier,
                "role_gate_applied": role_gate_applied,
                "role_gate_downgraded": role_gate_downgraded,
                "role_gate_reason": role_gate_reason,
                "model_id": model.model_id,
                "env_id": env_id,
                "base_url": model.base_url,
                "requested_max_new_tokens": model.max_new_tokens,
                "max_new_tokens": max_new_tokens,
                "requested_request_timeout": model.request_timeout,
                "request_timeout": request_timeout,
                "requested_reasoning_mode": args.reasoning_mode,
                "reasoning_mode": reasoning_mode,
                "steps": summary.get("steps", 0),
                "episodes": summary.get("episodes", 0),
                "per_env_steps": summary.get("per_env_steps", {}),
                "reward_totals": summary.get("reward_totals", {}),
                "run_token_total": summary.get("run_token_total", 0),
                "export_path": str(export_path),
                "summary_path": str(export_path.with_suffix(".summary.json")),
                "config_path": str(config_path),
            }
        else:
            failed_count += 1
            row = {
                "ts": now_ts(),
                "event": "task_complete",
                "status": str(payload.get("status", "failed")),
                "task_key": task_key,
                "run_id": run_id,
                "variant_id": variant_id,
                "skill_name": skill_name,
                "skill_cluster": skill_cluster,
                "role_mode": role_mode,
                "role_support_tier": role_support_tier,
                "role_gate_applied": role_gate_applied,
                "role_gate_downgraded": role_gate_downgraded,
                "role_gate_reason": role_gate_reason,
                "model_id": model.model_id,
                "env_id": env_id,
                "base_url": model.base_url,
                "requested_max_new_tokens": model.max_new_tokens,
                "max_new_tokens": max_new_tokens,
                "requested_request_timeout": model.request_timeout,
                "request_timeout": request_timeout,
                "requested_reasoning_mode": args.reasoning_mode,
                "reasoning_mode": reasoning_mode,
                "error": payload.get("error", ""),
                "returncode": payload.get("returncode"),
                "stdout_tail": payload.get("stdout_tail"),
                "stderr_tail": payload.get("stderr_tail"),
                "failure_types": payload.get("failure_types", {}),
                "failure_count": payload.get("failure_count"),
                "config_path": str(config_path),
                "export_path": str(export_path),
                "summary_path": str(export_path.with_suffix(".summary.json")),
            }

        append_jsonl(ledger_path, row)
        append_jsonl(stout_path, row)

    append_jsonl(
        stout_path,
        {
            "ts": now_ts(),
            "event": "run_complete",
            "tasks_requested": total,
            "tasks_completed": done_count,
            "tasks_failed": failed_count,
            "tasks_skipped": skipped,
            "tasks_scheduled": total,
        },
    )
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        try:
            args = parse_args()
            stout_path = Path(args.stout).resolve() if args.stout else (
                Path(args.run_root).resolve() / "overnight_primehub_benchmark.stout.jsonl"
            )
            append_jsonl(
                stout_path,
                {
                    "ts": now_ts(),
                    "event": "run_error",
                    "error": "interrupted_by_keyboard",
                    "status": "interrupted",
                    "exit_code": 130,
                },
            )
        except Exception:
            # best effort logging only; keep interrupt semantics
            pass
        raise SystemExit(130)
    except Exception as exc:
        exc_trace = traceback.format_exc()
        try:
            args = parse_args()
            stout_path = Path(args.stout).resolve() if args.stout else (
                Path(args.run_root).resolve() / "overnight_primehub_benchmark.stout.jsonl"
            )
            append_jsonl(
                stout_path,
                {
                    "ts": now_ts(),
                    "event": "run_error",
                    "error": str(exc),
                    "traceback": exc_trace,
                    "status": "crashed",
                    "exit_code": 1,
                },
            )
            print(f"Unhandled exception in benchmark runner: {exc}", file=sys.stderr)
            print(exc_trace, file=sys.stderr)
        except Exception:
            print(exc_trace, file=sys.stderr)
        raise SystemExit(1)
