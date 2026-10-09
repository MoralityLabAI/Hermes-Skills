"""Run results/queue.txt one line at a time (one model server at a time). Lines can be appended while it
runs; finished lines are recorded in results/queue_done.txt. Exits after 30 idle minutes."""

from __future__ import annotations

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

STUDY = Path(__file__).resolve().parents[1]
QUEUE = STUDY / "results" / "queue.txt"
DONE = STUDY / "results" / "queue_done.txt"
LOGS = STUDY / "results" / "logs"
PY = sys.executable


def pending() -> list[str]:
    lines = [l.strip() for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    done = set(DONE.read_text(encoding="utf-8").splitlines()) if DONE.exists() else set()
    return [l for l in lines if l not in done]


def main() -> int:
    LOGS.mkdir(parents=True, exist_ok=True)
    idle_since = time.time()
    while True:
        todo = pending()
        if not todo:
            if time.time() - idle_since > 1800:
                return 0
            time.sleep(60)
            continue
        line = todo[0]
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log = LOGS / f"{stamp}.log"
        with log.open("w", encoding="utf-8") as handle:
            handle.write(f"# {line}\n")
            handle.flush()
            rc = subprocess.call([PY, "-u", *line.split()], cwd=STUDY / "src", stdout=handle, stderr=subprocess.STDOUT)
        with (STUDY / "results" / "queue_status.txt").open("a", encoding="utf-8") as status:
            status.write(f"{stamp} rc={rc} {line}\n")
        if rc == 0:
            with DONE.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
        else:
            time.sleep(120)  # a failed line is retried after a pause; three failures stop the runner
            fails = sum(1 for s in (STUDY / "results" / "queue_status.txt").read_text().splitlines() if s.endswith(line) and "rc=0" not in s)
            if fails >= 3:
                return 1
        idle_since = time.time()


if __name__ == "__main__":
    sys.exit(main())
