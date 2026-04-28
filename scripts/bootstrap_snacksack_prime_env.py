from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List


DEFAULT_HOST = "snacksack-ms-7d32.tail3156cd.ts.net"
DEFAULT_USER = "snacksack"
DEFAULT_IDENTITY_FILE = Path(r"C:/Users/patri/.ssh/id_ed25519")
DEFAULT_REMOTE_SITE_PACKAGES = "/dev/shm/prime_env_bridge_site"
DEFAULT_REMOTE_CACHE_ROOT = "/dev/shm/prime_env_bridge_cache"
DEFAULT_VERIFIERS_URL = "https://github.com/primeintellect-ai/verifiers/archive/refs/heads/main.zip"
DEFAULT_PACKAGES = [
    "cachetools",
    "loguru",
    "nltk",
    "langdetect",
    "chromadb",
    "modal",
    "swebench",
    "Faker",
    "emoji",
    "beautifulsoup4",
    "exa-py",
    "json-repair",
    "gdown",
]


def split_values(values: Iterable[str]) -> List[str]:
    items: List[str] = []
    for value in values:
        for piece in str(value).split(","):
            text = piece.strip()
            if text:
                items.append(text)
    return items


def remote_exec(host: str, user: str, identity_file: str, remote_script: str, args: List[str]) -> subprocess.CompletedProcess[str]:
    remote = f"{user}@{host}"
    cmd = [
        "ssh",
        "-i",
        identity_file,
        remote,
        "python3",
        "-",
        *args,
    ]
    return subprocess.run(
        cmd,
        input=remote_script,
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
    )


def build_remote_script() -> str:
    return r"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-root", required=True)
    parser.add_argument("--cache-root", required=True)
    parser.add_argument("--install", nargs="*")
    parser.add_argument("--check", nargs="*")
    parser.add_argument("--upgrade-verifiers", action="store_true")
    parser.add_argument("--verifiers-url", default="")
    args = parser.parse_args()

    site_root = pathlib.Path(args.site_root)
    cache_root = pathlib.Path(args.cache_root)
    site_root.mkdir(parents=True, exist_ok=True)
    cache_root.mkdir(parents=True, exist_ok=True)
    if str(site_root) not in sys.path:
        sys.path.insert(0, str(site_root))
    for name in ["xdg", "hf_home", "nltk_data", "matplotlib", "pip", "bin"]:
        (cache_root / name).mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["PYTHONPATH"] = str(site_root) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["TMPDIR"] = str(cache_root / "tmp")
    env["TMP"] = env["TMPDIR"]
    env["TEMP"] = env["TMPDIR"]
    env["XDG_CACHE_HOME"] = str(cache_root / "xdg")
    env["HF_HOME"] = str(cache_root / "hf_home")
    env["HF_HUB_CACHE"] = str(cache_root / "hf_home" / "hub")
    env["HF_DATASETS_CACHE"] = str(cache_root / "hf_home" / "datasets")
    env["TRANSFORMERS_CACHE"] = str(cache_root / "hf_home" / "transformers")
    env["NLTK_DATA"] = str(cache_root / "nltk_data")
    env["MPLCONFIGDIR"] = str(cache_root / "matplotlib")
    env["PIP_CACHE_DIR"] = str(cache_root / "pip")
    env["PATH"] = str(cache_root / "bin") + os.pathsep + env.get("PATH", "")
    pathlib.Path(env["TMPDIR"]).mkdir(parents=True, exist_ok=True)

    steps = []
    if args.upgrade_verifiers:
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            "--target",
            str(site_root),
            "--upgrade",
            (f"verifiers @ {args.verifiers_url}" if args.verifiers_url else "verifiers"),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
        steps.append(
            {
                "step": "upgrade_verifiers",
                "returncode": proc.returncode,
                "stdout_tail": (proc.stdout or "")[-1200:],
                "stderr_tail": (proc.stderr or "")[-1200:],
            }
        )

    if args.install:
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-cache-dir",
            "--upgrade",
            "--target",
            str(site_root),
            *args.install,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)
        steps.append(
            {
                "step": "install_packages",
                "packages": list(args.install),
                "returncode": proc.returncode,
                "stdout_tail": (proc.stdout or "")[-1200:],
                "stderr_tail": (proc.stderr or "")[-1200:],
            }
        )

    checks = {}
    for name in args.check or []:
        checks[name] = bool(importlib.util.find_spec(name))

    payload = {
        "site_root": str(site_root),
        "cache_root": str(cache_root),
        "steps": steps,
        "checks": checks,
    }
    print(json.dumps(payload, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install missing Prime env Python dependencies on snacksack into /dev/shm overlays.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--identity-file", default=str(DEFAULT_IDENTITY_FILE))
    parser.add_argument("--remote-site-packages", default=DEFAULT_REMOTE_SITE_PACKAGES)
    parser.add_argument("--remote-cache-root", default=DEFAULT_REMOTE_CACHE_ROOT)
    parser.add_argument("--packages", nargs="*", default=DEFAULT_PACKAGES)
    parser.add_argument("--check-modules", nargs="*", default=[
        "cachetools",
        "loguru",
        "nltk",
        "langdetect",
        "chromadb",
        "modal",
        "swebench",
        "faker",
        "emoji",
        "bs4",
        "exa_py",
        "json_repair",
        "gdown",
    ])
    parser.add_argument("--skip-verifiers-upgrade", action="store_true")
    parser.add_argument("--verifiers-url", default=DEFAULT_VERIFIERS_URL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packages = split_values(args.packages)
    check_modules = split_values(args.check_modules)
    remote_script = build_remote_script()
    remote_args = [
        "--site-root",
        args.remote_site_packages,
        "--cache-root",
        args.remote_cache_root,
    ]
    if not args.skip_verifiers_upgrade:
        remote_args.extend(["--upgrade-verifiers", "--verifiers-url", args.verifiers_url])
    if packages:
        remote_args.extend(["--install", *packages])
    if check_modules:
        remote_args.extend(["--check", *check_modules])

    result = remote_exec(
        host=args.host,
        user=args.user,
        identity_file=args.identity_file,
        remote_script=remote_script,
        args=remote_args,
    )
    if result.returncode != 0:
        if result.stderr:
            sys.stderr.write(result.stderr)
        if result.stdout:
            sys.stderr.write(result.stdout)
        return result.returncode
    sys.stdout.write(result.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
