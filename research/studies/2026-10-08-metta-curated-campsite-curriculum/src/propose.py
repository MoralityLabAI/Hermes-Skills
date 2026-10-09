"""Collect Campsite proposals from a local Bonsai model (CPU). Resumable: rows already written are skipped.

usage: python propose.py --proposer Bonsai-8B --plan test:1:1,train:1:2,val:1:1 [--slots 4]
plan entries are pool:greedy:sampled (proposals per puzzle).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bonsai  # noqa: E402
import campsite  # noqa: E402
from common import RESULTS, append_jsonl, lower_priority, read_jsonl, write_json  # noqa: E402

TEMPERATURE = 0.7


def seed_for(pool: str, puzzle_id: str, k: int) -> int:
    import hashlib

    return int(hashlib.sha256(f"{pool}|{puzzle_id}|{k}".encode()).hexdigest()[:8], 16)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--proposer", required=True, choices=sorted(bonsai.MODELS))
    ap.add_argument("--plan", required=True)
    ap.add_argument("--slots", type=int, default=1)
    ap.add_argument("--threads", type=int, default=8)
    args = ap.parse_args()
    lower_priority()
    out = RESULTS / "proposals" / f"{args.proposer}.jsonl"
    done = {(r["pool"], r["puzzle_id"], r["k"]) for r in read_jsonl(out)}
    jobs = []
    for entry in args.plan.split(","):
        pool, greedy, sampled = entry.split(":")
        for task, _ in campsite.puzzles(pool):
            for k in range(int(greedy) + int(sampled)):
                if (pool, task.task_id, k) not in done:
                    jobs.append((pool, task, k, k >= int(greedy)))
    print(f"{args.proposer}: {len(jobs)} proposals to collect ({len(done)} already written)", flush=True)
    if not jobs:
        return 0
    t_start = time.time()
    with bonsai.Server(args.proposer, threads=args.threads, slots=args.slots) as server:
        write_json(RESULTS / "proposals" / f"{args.proposer}.server.json",
                   {"model": args.proposer, "path": str(server.path), "sha256": server.sha256, "threads": args.threads,
                    "slots": args.slots, "temperature_sampled": TEMPERATURE, "gpu_layers": 0})

        def one(job):
            pool, task, k, sampled = job
            budget = 2 * len(task.grid) * len(task.grid[0]) + 16
            seed = seed_for(pool, task.task_id, k)
            t0 = time.time()
            res = server.complete(campsite.propose_prompt(task), budget, temperature=TEMPERATURE if sampled else 0.0,
                                  seed=seed, stop=["\n\n", "Puzzle:"])
            text = res.get("content", "")
            return {"pool": pool, "puzzle_id": task.task_id, "k": k, "sampled": sampled, "seed": seed,
                    "grid": campsite.parse_grid(text, len(task.grid)), "raw_text": text,
                    "tokens": res.get("timings", {}).get("predicted_n"), "latency_s": round(time.time() - t0, 2)}

        n = 0
        with ThreadPoolExecutor(args.slots) as ex:
            for row in ex.map(one, jobs):
                append_jsonl(out, row)
                n += 1
                if n % 25 == 0:
                    rate = (time.time() - t_start) / n
                    print(f"{n}/{len(jobs)} done, {rate:.1f}s each, ~{rate * (len(jobs) - n) / 60:.0f} min left", flush=True)
    print(f"finished {n} in {(time.time() - t_start) / 60:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
