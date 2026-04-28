#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4] / "basharena_latent_control_repo" / "basharena_latent_control_repo"


def tail_lines(path: Path, count: int = 8) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-count:]


def latest_file(folder: Path, pattern: str) -> Path | None:
    matches = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def powershell_python_processes() -> list[dict[str, object]]:
    cmd = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.Name -in 'python.exe','pythonw.exe' } | "
        "Select-Object ProcessId,CommandLine,CreationDate | "
        "ConvertTo-Json -Depth 3"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", cmd],
        capture_output=True,
        text=True,
        check=False,
    )
    if not result.stdout.strip():
        return []
    payload = json.loads(result.stdout)
    if isinstance(payload, dict):
        payload = [payload]
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the BlueBeam research loop state.")
    parser.add_argument("--repo-root", default=str(default_repo_root()))
    args = parser.parse_args()

    repo_root = Path(args.repo_root)
    analysis_root = repo_root / "analysis" / "snacksack_autoresearch"
    budget_path = analysis_root / "autoresearch_time_budget.json"
    report_path = analysis_root / "autoresearch_report.json"
    ranked_path = analysis_root / "autoresearch_ranked_jobs.csv"
    launch_out = latest_file(analysis_root, "launch_*.out.log")
    launch_err = latest_file(analysis_root, "launch_*.err.log")

    live_launchers = []
    for proc in powershell_python_processes():
        cmdline = str(proc.get("CommandLine") or "")
        if "run_snacksack_autoresearch_loop.py" in cmdline:
            live_launchers.append(
                {
                    "pid": proc.get("ProcessId"),
                    "creation": proc.get("CreationDate"),
                    "commandline": cmdline,
                }
            )

    summary: dict[str, object] = {
        "repo_root": str(repo_root),
        "analysis_root": str(analysis_root),
        "live_launchers": live_launchers,
        "latest_launch_out": str(launch_out) if launch_out else None,
        "latest_launch_err": str(launch_err) if launch_err else None,
        "budget_exists": budget_path.exists(),
        "report_exists": report_path.exists(),
        "ranked_exists": ranked_path.exists(),
    }

    if budget_path.exists():
        summary["budget"] = json.loads(budget_path.read_text(encoding="utf-8"))
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        summary["finished_utc"] = report.get("finished_utc")
        summary["job_count"] = len(report.get("jobs", []) or [])
        summary["top_jobs"] = (report.get("ranked_jobs", []) or [])[:5]

    print(json.dumps(summary, indent=2))

    if launch_out:
        print("\n--- launch tail ---")
        for line in tail_lines(launch_out):
            print(line)
    if launch_err:
        err_lines = tail_lines(launch_err)
        if err_lines:
            print("\n--- error tail ---")
            for line in err_lines:
                print(line)


if __name__ == "__main__":
    main()
