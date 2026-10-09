"""Part G: train the pre-repair action gate (hermes-lite TinyRecursivePolicy structure, 4-way head) on the
curriculum, for every (features, source, N, seed), and write its action on every test row.

usage: python gates.py
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import metta_schema  # noqa: E402
from common import RESULTS, lower_priority, read_jsonl, write_json  # noqa: E402

CUR = RESULTS / "curriculum"
OUT = RESULTS / "gates"
FEATURES = ("typed", "raw", "typed+raw")
SOURCES = ("real", "synthetic", "realq")  # real = Bonsai-8B answers, realq = Qwen2.5-3B answers (addendum A3)
SIZES = (25, 50, 100, 200, 400, None)  # None = all rows
SEEDS = range(5)
STEP_GRID = (50, 100, 200, 400)
HIDDEN, STEPS, LR, WD = 64, 4, 5e-3, 1e-4


def load() -> dict[str, list[dict]]:
    syn = read_jsonl(CUR / "synthetic.jsonl")
    r8 = read_jsonl(CUR / "real-Bonsai-8B.jsonl")
    r27 = read_jsonl(CUR / "real-Bonsai-27B.jsonl")
    rq = read_jsonl(CUR / "real-Qwen2.5-3B.jsonl")
    return {
        "train:realq": [r for r in rq if r["pool"] == "train"],
        "val:realq": [r for r in rq if r["pool"] == "val"],
        "test:TQ": [r for r in rq if r["pool"] == "test" and r["k"] == 0],
        "test:TQs": [r for r in rq if r["pool"] == "test" and r["k"] == 1],
        "train:real": [r for r in r8 if r["pool"] == "train"],
        "val:real": [r for r in r8 if r["pool"] == "val"],
        "train:synthetic": [r for r in syn if r["pool"] == "train"],
        "val:synthetic": [r for r in syn if r["pool"] == "val"],
        "test:T8": [r for r in r8 if r["pool"] == "test" and r["k"] == 0],
        "test:T8s": [r for r in r8 if r["pool"] == "test" and r["k"] == 1],
        "test:T27": [r for r in r27 if r["pool"] == "test" and r["k"] == 0],
        "test:synthetic": [r for r in syn if r["pool"] == "test"],
    }


def vec(row: dict, features: str) -> list[float]:
    if features == "typed":
        return row["typed"]
    if features == "raw":
        return row["raw"]
    return row["typed"] + row["raw"]


def subset(rows: list[dict], n: int | None, seed: int) -> list[dict]:
    """Whole puzzles in a seeded order until n rows (the last puzzle is cut to fit)."""
    if n is None or n >= len(rows):
        return rows
    by_puzzle: dict[str, list[dict]] = {}
    for r in rows:
        by_puzzle.setdefault(r["puzzle_id"], []).append(r)
    order = sorted(by_puzzle)
    random.Random(f"subset:{seed}").shuffle(order)
    out: list[dict] = []
    for pid in order:
        out += by_puzzle[pid]
        if len(out) >= n:
            break
    return out[:n]


def train(train_rows, val_rows, features: str, seed: int):
    import torch
    from torch import nn

    menu = list(metta_schema.load().menu)

    class Gate(nn.Module):
        def __init__(self, dim: int):
            super().__init__()
            self.input_projection = nn.Linear(dim, HIDDEN)
            self.recurrent = nn.Linear(HIDDEN * 2, HIDDEN)
            self.action_head = nn.Linear(HIDDEN, len(menu))

        def forward(self, x):
            encoded = torch.tanh(self.input_projection(x))
            h = torch.zeros_like(encoded)
            for _ in range(STEPS):
                h = torch.tanh(self.recurrent(torch.cat([encoded, h], dim=-1)))
            return self.action_head(h)

    xt = torch.tensor([vec(r, features) for r in train_rows], dtype=torch.float32)
    yt = torch.tensor([menu.index(r["best_action"]) for r in train_rows])
    xv = torch.tensor([vec(r, features) for r in val_rows], dtype=torch.float32)
    yv = torch.tensor([menu.index(r["best_action"]) for r in val_rows])
    torch.manual_seed(seed)
    model = Gate(xt.shape[1])
    opt = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
    best, done = None, 0
    for target in STEP_GRID:  # one run, checkpoints at each registered step count
        for _ in range(target - done):
            opt.zero_grad()
            nn.functional.cross_entropy(model(xt), yt).backward()
            opt.step()
        done = target
        with torch.no_grad():
            acc = (model(xv).argmax(-1) == yv).float().mean().item()
        if best is None or acc > best[0]:
            best = (acc, target, {k: v.clone() for k, v in model.state_dict().items()})
    acc, steps, state = best
    model.load_state_dict(state)
    model.eval()

    def predict(rows):
        if not rows:
            return []
        with torch.no_grad():
            idx = model(torch.tensor([vec(r, features) for r in rows], dtype=torch.float32)).argmax(-1).tolist()
        return [menu[i] for i in idx]

    return predict, {"val_accuracy": round(acc, 4), "steps": steps, "params": sum(p.numel() for p in model.parameters())}


def main() -> int:
    import torch

    torch.set_num_threads(4)
    lower_priority()
    data = load()
    tests = {k: v for k, v in data.items() if k.startswith("test:") and v}
    print({k: len(v) for k, v in data.items()}, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "predictions.jsonl"
    path.write_text("", encoding="utf-8")
    t0 = time.time()
    for source in SOURCES:
        if not data[f"train:{source}"]:
            print(f"skipping {source}: no rows", flush=True)
            continue
        for features in FEATURES:
            for n in SIZES:
                for seed in SEEDS:
                    rows = subset(data[f"train:{source}"], n, seed)
                    predict, info = train(rows, data[f"val:{source}"], features, seed)
                    rec = {"source": source, "features": features, "n": n if n is not None else "all", "n_rows": len(rows),
                           "seed": seed, **info,
                           "predictions": {name: dict(zip((r["row_id"] for r in rs), predict(rs))) for name, rs in tests.items()}}
                    with path.open("a", encoding="utf-8") as h:
                        h.write(json.dumps(rec) + "\n")
                print(f"{source} {features} n={n}: done ({time.time() - t0:.0f}s)", flush=True)
    write_json(OUT / "config.json", {"hidden": HIDDEN, "recursive_steps": STEPS, "lr": LR, "weight_decay": WD,
                                     "step_grid": STEP_GRID, "sizes": [s if s else "all" for s in SIZES], "seeds": list(SEEDS),
                                     "features": FEATURES, "sources": SOURCES})
    return 0


if __name__ == "__main__":
    sys.exit(main())
