"""Paths and read-only access to Hermes-Skills HEAD and hermes-lite (no checkout, no config writes)."""

from __future__ import annotations

import contextlib
import importlib
import json
import subprocess
import sys
import types
from functools import lru_cache
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
RESULTS = STUDY / "results"
HERMES_SKILLS = STUDY.parents[2]
HERMES_LITE = Path(r"C:\Users\patri\Documents\Codex\hermes-lite")
GIT = r"C:\Program Files\Git\cmd\git.exe"


def git_show(path: str, root: Path = HERMES_SKILLS) -> str:
    """A file's committed content. The Hermes-Skills working tree differs from HEAD, so HEAD is read
    directly; safe.directory is passed per call and never written to any config."""
    out = subprocess.run([GIT, "-c", "safe.directory=*", "show", f"HEAD:{path}"], cwd=root, capture_output=True, check=True)
    return out.stdout.decode("utf-8-sig")


def git_head(root: Path = HERMES_SKILLS) -> str:
    out = subprocess.run([GIT, "-c", "safe.directory=*", "rev-parse", "HEAD"], cwd=root, capture_output=True, check=True)
    return out.stdout.decode().strip()


def head_module(path: str, name: str, stubs: tuple[str, ...] = ()) -> types.ModuleType:
    """Execute a HEAD file as a module. `stubs` are third-party imports it makes but this study never calls."""
    for stub in stubs:
        sys.modules.setdefault(stub, types.ModuleType(stub))
    module = types.ModuleType(name)
    module.__file__ = f"Hermes-Skills HEAD:{path}"
    exec(compile(git_show(path), module.__file__, "exec"), module.__dict__)  # noqa: S102
    return module


def head_jsonl(path: str) -> list[dict]:
    return [json.loads(line) for line in git_show(path).splitlines() if line.strip()]


@contextlib.contextmanager
def _no_bytecode():
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        yield
    finally:
        sys.dont_write_bytecode = previous


@lru_cache(maxsize=None)
def hermes_lite_campsite():
    base = HERMES_LITE / "src"
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))
    with _no_bytecode():
        return importlib.import_module("agent.intellect3_logic")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")
        handle.flush()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def lower_priority() -> None:
    try:
        import psutil

        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:  # noqa: BLE001
        pass
