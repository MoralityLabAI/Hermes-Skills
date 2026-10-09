"""Run several repair_trm.py arms as parallel 4-thread processes and wait for all (one queue line).

usage: python repair_parallel.py raw atoms        |  python repair_parallel.py raw+sym atoms+sym
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
LOGS = SRC.parent / "results" / "logs"


def main() -> int:
    procs = []
    argv = sys.argv[1:]
    extra = argv[argv.index("--") + 1:] if "--" in argv else []
    arms = argv[: argv.index("--")] if "--" in argv else argv
    for arm in arms:
        framing, _, sym = arm.partition("+")
        cmd = [sys.executable, "-u", str(SRC / "repair_trm.py"), "run", "--arm", framing, "--threads", "4"] + (["--sym"] if sym else []) + extra
        log = (LOGS / f"repair_trm.{arm}.log").open("a", encoding="utf-8")
        procs.append((arm, subprocess.Popen(cmd, cwd=str(SRC), stdout=log, stderr=subprocess.STDOUT), log))
    rc = 0
    for arm, p, log in procs:
        code = p.wait()
        log.close()
        print(f"{arm}: rc={code}", flush=True)
        rc = rc or code
    return rc


if __name__ == "__main__":
    sys.exit(main())
