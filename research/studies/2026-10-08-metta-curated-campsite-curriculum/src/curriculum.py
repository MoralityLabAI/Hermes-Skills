"""Build the near-miss curriculum: one row per candidate (real proposal or synthetic defect), carrying the
MeTTa-typed state, the raw state, each repair operator's outcome, the bucket and the best-action label.

usage: python curriculum.py
"""

from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import campsite  # noqa: E402
import metta_schema  # noqa: E402
from common import RESULTS, git_head, read_jsonl, write_json  # noqa: E402

OUT = RESULTS / "curriculum"


def build_row(task, gold, grid, **meta) -> dict:
    v0 = campsite.verify(task, grid) if grid is not None else {"official_pass": False, "failed_gates": ["syntax_valid"] * 7}
    failed0 = len(v0["failed_gates"])
    ops = {}
    for op in campsite.operators():
        t0 = time.time()
        out = campsite.repair(task, gold, grid, op)
        if out is None:
            ops[op] = {"grid": None, "passes": False, "failed_gates": None, "applied": False}
        else:
            v = campsite.verify(task, out)
            ops[op] = {"grid": out, "passes": bool(v["official_pass"]), "failed_gates": len(v["failed_gates"]), "applied": True,
                       "changed": out != grid, "seconds": round(time.time() - t0, 4)}
    menu = metta_schema.load().menu
    if v0["official_pass"]:
        best, bucket = "commit", "exact_positive"
    else:
        best = next((op for op in menu[1:-1] if ops[op]["passes"]), "reject")
        if best != "reject":
            bucket = "repair_success"
        elif any(o["applied"] and o["failed_gates"] is not None and o["failed_gates"] < failed0 for o in ops.values()):
            bucket = "partial_improvement"
        else:
            bucket = "no_gain"
    return {**meta, "puzzle_id": task.task_id, "size": f"{len(task.grid)}x{len(task.grid[0])}", "candidate": grid,
            "pass_as_written": bool(v0["official_pass"]), "failed_gates": failed0, "failed_gate_names": v0["failed_gates"],
            "typed": campsite.typed_features(task, grid), "raw": campsite.raw_features(task, grid), "ops": ops,
            "bucket": bucket, "best_action": best}


def real_rows(proposer: str) -> list[dict]:
    rows = []
    for p in read_jsonl(RESULTS / "proposals" / f"{proposer}.jsonl"):
        task, gold = campsite.task_by_id(p["pool"])[p["puzzle_id"]]
        rows.append(build_row(task, gold, p["grid"], source=f"real:{proposer}", pool=p["pool"], k=p["k"], sampled=p["sampled"],
                              row_id=f"{proposer}:{p['pool']}:{p['puzzle_id']}:{p['k']}"))
    return rows


def synthetic_rows(pool: str) -> list[dict]:
    rows = []
    for task, gold in campsite.puzzles(pool):
        for kind in campsite.DEFECTS:
            grid = campsite.synthetic(task, gold, kind, random.Random(f"synthetic:{pool}:{task.task_id}:{kind}"))
            if grid is None:
                continue
            rows.append(build_row(task, gold, grid, source="synthetic", pool=pool, kind=kind, k=0, sampled=False,
                                  row_id=f"synthetic:{pool}:{task.task_id}:{kind}"))
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    meta = {"hermes_skills_head": git_head(), "repair_source_sha16": campsite.source_hash(),
            "metta_package": str(metta_schema.PACKAGE), "feature_names": metta_schema.load().feature_names, "files": {}}
    for name, builder in [("synthetic", lambda: [r for pool in ("train", "val", "test") for r in synthetic_rows(pool)]),
                          ("real-Bonsai-8B", lambda: real_rows("Bonsai-8B")),
                          ("real-Bonsai-27B", lambda: real_rows("Bonsai-27B")),
                          ("real-Qwen2.5-3B", lambda: real_rows("Qwen2.5-3B"))]:
        t0 = time.time()
        rows = builder()
        path = OUT / f"{name}.jsonl"
        path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        by_pool = Counter((r["pool"], r["bucket"]) for r in rows)
        meta["files"][name] = {"rows": len(rows), "seconds": round(time.time() - t0, 1),
                               "pool_bucket": {f"{p}|{b}": n for (p, b), n in sorted(by_pool.items())},
                               "best_action": dict(Counter((r["pool"], r["best_action"]) for r in rows).most_common())
                               if False else {f"{p}|{a}": n for (p, a), n in sorted(Counter((r['pool'], r['best_action']) for r in rows).items())}}
        print(name, len(rows), "rows", f"{time.time() - t0:.0f}s", flush=True)
    write_json(OUT / "manifest.json", meta)
    return 0


if __name__ == "__main__":
    sys.exit(main())
