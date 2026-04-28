from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict


DEFAULT_HOST = "snacksack-ms-7d32.tail3156cd.ts.net"
DEFAULT_USER = "snacksack"
DEFAULT_IDENTITY_FILE = Path(r"C:/Users/patri/.ssh/id_ed25519")
DEFAULT_RESEARCH_ROOT = "/home/snacksack/prime_repos_tmp/research-environments/environments"
DEFAULT_COMMUNITY_ROOT = "/home/snacksack/prime_repos_tmp/community-environments/environments"
DEFAULT_STATE_ROOT = "/dev/shm/prime_env_bridge_state"
DEFAULT_REMOTE_SITE_PACKAGES = "/dev/shm/prime_env_bridge_site"
DEFAULT_REMOTE_CACHE_ROOT = "/dev/shm/prime_env_bridge_cache"
DEFAULT_JUDGE_BASE_URL = f"http://{DEFAULT_HOST}:8081/v1"
DEFAULT_JUDGE_MODEL = "Qwen3.5-27B.Q4_K_M.gguf"


REMOTE_BRIDGE = r"""
from __future__ import annotations

import argparse
import base64
import asyncio
import contextlib
import importlib
import io
import inspect
import json
import logging
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict

logging.disable(logging.CRITICAL)
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("HF_HUB_VERBOSITY", "error")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OPENAI_API_KEY", "EMPTY")
site_root = os.environ.get("HERMES_REMOTE_SITE_PACKAGES", "").strip()
cache_root = os.environ.get("HERMES_REMOTE_CACHE_ROOT", "").strip()
if site_root:
    Path(site_root).mkdir(parents=True, exist_ok=True)
    if site_root not in sys.path:
        sys.path.insert(0, site_root)
if cache_root:
    cache_path = Path(cache_root)
    cache_path.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("XDG_CACHE_HOME", str(cache_path / "xdg"))
    os.environ.setdefault("HF_HOME", str(cache_path / "hf_home"))
    os.environ.setdefault("HF_HUB_CACHE", str(cache_path / "hf_home" / "hub"))
    os.environ.setdefault("HF_DATASETS_CACHE", str(cache_path / "hf_home" / "datasets"))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(cache_path / "hf_home" / "transformers"))
    os.environ.setdefault("NLTK_DATA", str(cache_path / "nltk_data"))
    os.environ.setdefault("MPLCONFIGDIR", str(cache_path / "matplotlib"))
    os.environ.setdefault("PIP_CACHE_DIR", str(cache_path / "pip"))
    os.environ["PATH"] = str(cache_path / "bin") + os.pathsep + os.environ.get("PATH", "")

ACTION_ONLY_TRACE_PROFILE = {
    "contract_version": "trm_trace_v1",
    "family": "prime_single_turn",
    "mode": "stepwise",
    "response_mode": "action_only",
    "max_trace_steps": 1,
    "max_step_chars": 80,
    "action_guidance": "Return only the final answer string that should be scored by the verifier.",
    "output_contract": "Return only the final answer text. No JSON. No markdown fences. No explanation.",
    "step_labels": ["answer"],
}


def _safe_json(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=True)


def _emit(payload: Dict[str, Any]) -> int:
    print(_safe_json(payload))
    return 0


def _capture(fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        result = fn()
    return result, buf.getvalue()


def _failure_observation(env_id: str, message: str) -> Dict[str, Any]:
    return {
        "observation": f"[{env_id}] {message}",
        "task": f"Complete task in {env_id}",
        "trace_profile": dict(ACTION_ONLY_TRACE_PROFILE),
        "session": {},
    }


def _load_env_module(env_root: Path, env_id: str):
    if env_id in {"math_env", "math_env_rlm"}:
        from verifiers.rubrics.experimental.hybrid_math_rubric import HybridMathRubric

        if not hasattr(HybridMathRubric, "DEFAULT_JUDGE_PROMPT"):
            HybridMathRubric.DEFAULT_JUDGE_PROMPT = ""
        if not hasattr(HybridMathRubric, "DEFAULT_JUDGE_MODEL"):
            HybridMathRubric.DEFAULT_JUDGE_MODEL = ""
        if not getattr(HybridMathRubric, "_hermes_parser_alias_patch", False):
            original_init = HybridMathRubric.__init__
            init_params = inspect.signature(original_init).parameters

            def _patched_init(self, *args, parser=None, **kwargs):
                if parser is not None:
                    if "parser" in init_params and "parser" not in kwargs:
                        kwargs["parser"] = parser
                    elif "judge_parser" in init_params and "judge_parser" not in kwargs:
                        kwargs["judge_parser"] = parser
                if "judge_parser" in kwargs and "judge_parser" not in init_params:
                    if "parser" in init_params and "parser" not in kwargs:
                        kwargs["parser"] = kwargs.pop("judge_parser")
                    else:
                        kwargs.pop("judge_parser", None)
                if "parser" in kwargs and "parser" not in init_params:
                    if "judge_parser" in init_params and "judge_parser" not in kwargs:
                        kwargs["judge_parser"] = kwargs.pop("parser")
                    else:
                        kwargs.pop("parser", None)
                kwargs.pop("use_judge_fallback", None)
                return original_init(self, *args, **kwargs)

            HybridMathRubric.__init__ = _patched_init
            HybridMathRubric._hermes_parser_alias_patch = True
    sys.path.insert(0, str(env_root))
    try:
        module = importlib.import_module(env_id)
    finally:
        if sys.path and sys.path[0] == str(env_root):
            sys.path.pop(0)
    if not hasattr(module, "load_environment"):
        raise AttributeError(f"Environment module {env_id!r} has no load_environment")
    return module


def _default_env_kwargs(env_id: str, judge_base_url: str, judge_model: str) -> Dict[str, Any]:
    if env_id in {"simpleqa", "simpleqa_verified", "simpleqa_verified_2"}:
        return {
            "judge_model": judge_model,
            "judge_base_url": judge_base_url,
            "judge_api_key_var": "OPENAI_API_KEY",
        }
    if env_id == "if_summarize_judge":
        return {
            "judge_url": judge_base_url,
            "judge_model": judge_model,
            "judge_api_key_var": "OPENAI_API_KEY",
            "judge_timeout_seconds": 90.0,
        }
    return {}


def _resolve_env_kwargs(env_id: str, raw: str, judge_base_url: str, judge_model: str) -> Dict[str, Any]:
    merged = _default_env_kwargs(env_id, judge_base_url, judge_model)
    if raw.strip():
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("--env-kwargs-json must decode to an object")
        merged.update(payload)
    return merged


def _flatten_content(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        chunks = []
        for item in value:
            if isinstance(item, dict):
                item_type = str(item.get("type", "")).strip().lower()
                if item_type == "text":
                    text = str(item.get("text", "")).strip()
                    if text:
                        chunks.append(text)
                elif item_type == "image_url":
                    chunks.append("[image omitted]")
                else:
                    text = str(item.get("content", "") or item.get("text", "")).strip()
                    if text:
                        chunks.append(text)
            else:
                text = str(item).strip()
                if text:
                    chunks.append(text)
        return "\n".join(chunks).strip()
    return str(value).strip()


def _messages_to_observation(prompt: Any) -> str:
    if isinstance(prompt, str):
        return prompt.strip()
    if not isinstance(prompt, list):
        return str(prompt).strip()
    lines = []
    for message in prompt:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role", "user")).strip().upper()
        content = _flatten_content(message.get("content", ""))
        if content:
            lines.append(f"{role}: {content}")
    return "\n\n".join(lines).strip()


def _state_path(root: Path, session_id: str) -> Path:
    return root / f"{session_id}.json"


def _cleanup_runtime_caches() -> None:
    candidates = []
    for key in ("HF_HUB_CACHE", "HF_DATASETS_CACHE", "TRANSFORMERS_CACHE", "XDG_CACHE_HOME"):
        value = os.environ.get(key, "").strip()
        if value:
            candidates.append(Path(value))
    hf_home = os.environ.get("HF_HOME", "").strip()
    if hf_home:
        candidates.extend([Path(hf_home) / "datasets", Path(hf_home) / "hub", Path(hf_home) / "transformers"])
    seen = set()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        marker = str(resolved)
        if marker in seen:
            continue
        seen.add(marker)
        shutil.rmtree(path, ignore_errors=True)


def _build_reset_payload(args: argparse.Namespace) -> Dict[str, Any]:
    env_root = Path(args.env_root) / args.env_id
    env_kwargs = _resolve_env_kwargs(
        env_id=args.env_id,
        raw=args.env_kwargs_json,
        judge_base_url=args.judge_base_url,
        judge_model=args.judge_model,
    )

    def _load_row():
        module = _load_env_module(env_root, args.env_id)
        env = module.load_environment(**env_kwargs)
        env_type = type(env).__name__
        if env_type != "SingleTurnEnv":
            return {
                "unsupported": True,
                "reason": f"unsupported env type: {env_type}",
            }
        dataset = env.get_eval_dataset(n=1, seed=args.seed)
        if len(dataset) == 0:
            return {
                "unsupported": True,
                "reason": "environment returned no eval examples",
            }
        row = dataset[0]
        return {
            "unsupported": False,
            "row": row,
            "env_type": env_type,
        }

    loaded, captured = _capture(_load_row)
    if loaded.get("unsupported"):
        payload = _failure_observation(args.env_id, loaded["reason"])
        payload["bridge_debug"] = captured[:800]
        return payload

    row = loaded["row"]
    prompt = row.get("prompt")
    answer = row.get("answer", "")
    task = row.get("task", args.env_id)
    info = row.get("info", {})
    observation = _messages_to_observation(prompt)
    if not observation:
        payload = _failure_observation(args.env_id, "empty prompt after flattening")
        payload["bridge_debug"] = captured[:800]
        return payload

    session_id = str(uuid.uuid4())
    state_root = Path(args.state_root)
    state_root.mkdir(parents=True, exist_ok=True)
    session_path = _state_path(state_root, session_id)
    session_path.write_text(
        _safe_json(
            {
                "env_id": args.env_id,
                "env_root": str(env_root),
                "env_kwargs": env_kwargs,
                "prompt": prompt,
                "answer": answer,
                "task": task,
                "info": info,
            }
        ),
        encoding="utf-8",
    )
    return {
        "observation": observation,
        "task": str(task),
        "trace_profile": dict(ACTION_ONLY_TRACE_PROFILE),
        "session": {
            "session_id": session_id,
        },
        "bridge_debug": captured[:800],
    }


def _build_probe_payload(args: argparse.Namespace) -> Dict[str, Any]:
    env_root = Path(args.env_root) / args.env_id
    env_kwargs = _resolve_env_kwargs(
        env_id=args.env_id,
        raw=args.env_kwargs_json,
        judge_base_url=args.judge_base_url,
        judge_model=args.judge_model,
    )

    def _inspect():
        module = _load_env_module(env_root, args.env_id)
        env = module.load_environment(**env_kwargs)
        env_type = type(env).__name__
        if env_type != "SingleTurnEnv":
            return {
                "status": "unsupported",
                "reason": f"unsupported env type: {env_type}",
                "env_type": env_type,
            }
        dataset = env.get_eval_dataset(n=1, seed=args.seed)
        if len(dataset) == 0:
            return {
                "status": "unsupported",
                "reason": "environment returned no eval examples",
                "env_type": env_type,
            }
        row = dataset[0]
        observation = _messages_to_observation(row.get("prompt"))
        if not observation:
            return {
                "status": "failure",
                "reason": "empty prompt after flattening",
                "env_type": env_type,
            }
        return {
            "status": "ok",
            "reason": "",
            "env_type": env_type,
            "task": str(row.get("task", args.env_id)),
            "observation_preview": observation[:400],
        }

    inspected, captured = _capture(_inspect)
    payload = {
        "env_id": args.env_id,
        "status": str(inspected.get("status", "failure")),
        "reason": str(inspected.get("reason", "")),
        "env_type": str(inspected.get("env_type", "")),
        "task": str(inspected.get("task", "")),
        "observation_preview": str(inspected.get("observation_preview", "")),
        "bridge_debug": captured[:800],
    }
    return payload


def _build_step_payload(args: argparse.Namespace, payload: Dict[str, Any]) -> Dict[str, Any]:
    session = payload.get("state") or {}
    if not isinstance(session, dict):
        return {
            "failure_type": "bridge_failure",
            "failure_phase": "step",
            "failure_message": "missing or invalid session state",
            "observation": f"[{args.env_id}] missing or invalid session state",
            "reward": 0.0,
            "done": True,
            "valid_action": False,
            "task": f"Complete task in {args.env_id}",
        }

    session_id = str(session.get("session_id", "")).strip()
    if not session_id:
        return {
            "failure_type": "bridge_failure",
            "failure_phase": "step",
            "failure_message": "session_id missing from state",
            "observation": f"[{args.env_id}] session_id missing from state",
            "reward": 0.0,
            "done": True,
            "valid_action": False,
            "task": f"Complete task in {args.env_id}",
        }

    session_path = _state_path(Path(args.state_root), session_id)
    if not session_path.exists():
        return {
            "failure_type": "bridge_failure",
            "failure_phase": "step",
            "failure_message": f"session not found: {session_id}",
            "observation": f"[{args.env_id}] session not found: {session_id}",
            "reward": 0.0,
            "done": True,
            "valid_action": False,
            "task": f"Complete task in {args.env_id}",
        }

    record = json.loads(session_path.read_text(encoding="utf-8"))
    action = str(payload.get("action", "")).strip()
    if not action:
        return {
            "failure_type": "bridge_failure",
            "failure_phase": "step",
            "failure_message": "empty action",
            "observation": f"[{args.env_id}] empty action",
            "reward": 0.0,
            "done": True,
            "valid_action": False,
            "task": str(record.get("task", args.env_id)),
        }

    def _score():
        module = _load_env_module(Path(record["env_root"]), args.env_id)
        env = module.load_environment(**dict(record.get("env_kwargs") or {}))
        completion = [{"role": "assistant", "content": action}]
        state = {
            "prompt": record["prompt"],
            "completion": completion,
            "answer": record.get("answer", ""),
            "task": record.get("task", args.env_id),
            "info": record.get("info", {}),
            "timing": {"total_ms": 0.0},
            "trajectory": [{"prompt": record["prompt"], "completion": completion}],
            "reward": 0.0,
            "metrics": {},
        }
        asyncio.run(env.rubric.score_rollout(state))
        return state

    scored, captured = _capture(_score)
    reward = float(scored.get("reward", 0.0) or 0.0)
    metrics = scored.get("metrics", {})
    info = scored.get("info", {})
    if not isinstance(info, dict):
        info = {}
    judge_response = str(info.get("judge_response", "") or "")
    if len(judge_response) > 2000:
        judge_response = judge_response[:2000].rstrip() + "...[truncated]"
    session_path.unlink(missing_ok=True)
    return {
        "observation": f"[{args.env_id}] scored reward={reward:.4f}",
        "reward": reward,
        "score": reward,
        "done": True,
        "valid_action": True,
        "task": str(record.get("task", args.env_id)),
        "session": {
            "session_id": session_id,
        },
        "episode_summary": json.dumps({"reward": reward, "metrics": metrics}, ensure_ascii=True),
        "metrics": metrics,
        "env_info": {
            "constraint": str(info.get("constraint", "") or ""),
            "constraint_type": str(info.get("constraint_type", "") or ""),
            "judge_score": info.get("judge_score"),
            "judge_response": judge_response,
        },
        "bridge_debug": captured[:800],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["probe", "reset", "step"], required=True)
    parser.add_argument("--env-id", required=True)
    parser.add_argument("--env-root", required=True)
    parser.add_argument("--state-root", required=True)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--payload-b64", default="")
    parser.add_argument("--env-kwargs-json", default="{}")
    parser.add_argument("--judge-base-url", default="")
    parser.add_argument("--judge-model", default="")
    args = parser.parse_args()
    tmp_root = None
    for candidate in (Path("/dev/shm/prime_env_bridge_tmp"), Path(args.state_root) / "_tmp"):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
        except OSError:
            continue
        tmp_root = candidate
        break
    if tmp_root is not None:
        os.environ["TMPDIR"] = str(tmp_root)
        os.environ["TMP"] = str(tmp_root)
        os.environ["TEMP"] = str(tmp_root)
        tempfile.tempdir = str(tmp_root)

    try:
        if args.mode == "probe":
            try:
                return _emit(_build_probe_payload(args))
            finally:
                _cleanup_runtime_caches()
        if args.mode == "reset":
            try:
                return _emit(_build_reset_payload(args))
            finally:
                _cleanup_runtime_caches()

        payload = {}
        if args.payload_b64:
            payload = json.loads(
                base64.b64decode(args.payload_b64.encode("ascii")).decode("utf-8")
            )
        if not isinstance(payload, dict):
            raise ValueError("step payload must decode to an object")
        try:
            return _emit(_build_step_payload(args, payload))
        finally:
            _cleanup_runtime_caches()
    except Exception as exc:
        return _emit(
            {
                "failure_type": "bridge_failure",
                "failure_phase": args.mode,
                "failure_message": str(exc),
                "observation": f"[{args.env_id}] bridge failure: {exc}",
                "reward": 0.0,
                "done": True,
                "valid_action": False,
                "task": f"Complete task in {args.env_id}",
            }
        )


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bridge Prime Intellect verifier envs over SSH for the TRM harness.")
    parser.add_argument("env_id")
    parser.add_argument("--source", choices=["research", "community"], required=True)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--step", action="store_true")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--research-root", default=DEFAULT_RESEARCH_ROOT)
    parser.add_argument("--community-root", default=DEFAULT_COMMUNITY_ROOT)
    parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--ssh-timeout-seconds", type=int, default=45)
    parser.add_argument("--judge-base-url", default=DEFAULT_JUDGE_BASE_URL)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    parser.add_argument("--env-kwargs-json", default="{}")
    parser.add_argument("--remote-site-packages", default=DEFAULT_REMOTE_SITE_PACKAGES)
    parser.add_argument("--remote-cache-root", default=DEFAULT_REMOTE_CACHE_ROOT)
    return parser.parse_args()


def _load_step_payload() -> Dict[str, Any]:
    raw = sys.stdin.read().lstrip("\ufeff").strip()
    if not raw:
        return {}
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("step payload must decode to an object")
    return payload


def _remote_env_root(args: argparse.Namespace) -> str:
    return args.research_root if args.source == "research" else args.community_root


def _build_ssh_command(args: argparse.Namespace, payload: Dict[str, Any]) -> list[str]:
    remote = f"{args.user}@{args.host}"
    remote_cmd = [
        "env",
        f"HERMES_REMOTE_SITE_PACKAGES={args.remote_site_packages}",
        f"HERMES_REMOTE_CACHE_ROOT={args.remote_cache_root}",
        "python3",
        "-",
        "--mode",
        "probe" if args.probe else ("reset" if args.reset else "step"),
        "--env-id",
        args.env_id,
        "--env-root",
        _remote_env_root(args),
        "--state-root",
        args.state_root,
        "--seed",
        str(args.seed),
        "--env-kwargs-json",
        args.env_kwargs_json,
        "--judge-base-url",
        args.judge_base_url,
        "--judge-model",
        args.judge_model,
    ]
    if args.step:
        payload_b64 = base64.b64encode(json.dumps(payload, ensure_ascii=True).encode("utf-8")).decode("ascii")
        remote_cmd.extend(["--payload-b64", payload_b64])
    return [
        "ssh",
        "-o",
        f"ConnectTimeout={args.ssh_timeout_seconds}",
        "-i",
        args.identity_file,
        remote,
        *remote_cmd,
    ]


def main() -> int:
    args = _parse_args()
    mode_count = sum(1 for flag in (args.probe, args.reset, args.step) if flag)
    if mode_count != 1:
        raise SystemExit("pass exactly one of --probe, --reset, or --step")

    payload = _load_step_payload() if args.step else {}
    cmd = _build_ssh_command(args, payload)
    result = subprocess.run(
        cmd,
        input=REMOTE_BRIDGE,
        capture_output=True,
        text=True,
        errors="replace",
        timeout=max(30, args.ssh_timeout_seconds + 20),
        check=False,
    )
    if result.returncode != 0:
        if result.stderr:
            sys.stderr.write(result.stderr)
        elif result.stdout:
            sys.stderr.write(result.stdout)
        return result.returncode

    text = (result.stdout or "").strip()
    if not text:
        sys.stderr.write("remote bridge returned empty stdout\n")
        return 1
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"remote bridge returned invalid JSON: {exc}\n")
        if text:
            sys.stderr.write(text[-1200:] + "\n")
        return 1

    sys.stdout.write(json.dumps(payload, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
