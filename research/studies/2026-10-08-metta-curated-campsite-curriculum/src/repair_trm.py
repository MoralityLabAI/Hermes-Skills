"""SPEC-R: train repair TRMs under each corpus framing and write their per-cell predictions on every test set.

usage: python repair_trm.py run --arm atoms [--sym] [--threads 4]     (selection, 5 seeds, learning curves)
       python repair_trm.py smoke
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import campsite  # noqa: E402
import repair_cells as rc  # noqa: E402
from common import RESULTS, lower_priority, read_jsonl, write_json  # noqa: E402

OUT = RESULTS / "repair_trm"
PROPOSERS = ("Qwen2.5-3B", "Bonsai-8B")
LRS = (1e-3, 3e-4)
SCHEDULE = 80               # cosine schedule length in epochs (addendum R-A1)
CHECKPOINTS = (20, 40, 80)  # registered epoch grid, evaluated as checkpoints of one run
SEEDS = range(5)
CURVE_FRACTIONS = (0.25, 0.5)
CURVE_SEEDS = range(3)
TESTS = ("TQ", "TQs", "T8", "T8s", "T27")
D, HEADS, LAYERS, CYCLES, INNER = 64, 4, 2, 3, 3


# ---------------------------------------------------------------------------- data


def examples(split: str) -> list[dict]:
    """Real broken answers: train = train + train2 pools of both proposers; val; tests by name."""
    pools = {"train": ("train", "train2"), "val": ("val",)}
    if split in pools:
        return [_example(p, prop) for prop in PROPOSERS for p in read_jsonl(RESULTS / "proposals" / f"{prop}.jsonl")
                if p["pool"] in pools[split]]
    prop, k, pool = {"TQ": ("Qwen2.5-3B", 0, "test"), "TQs": ("Qwen2.5-3B", 1, "test"), "T8": ("Bonsai-8B", 0, "test"),
                     "T8s": ("Bonsai-8B", 1, "test"), "T27": ("Bonsai-27B", 0, "test"),
                     "TQ2": ("Qwen2.5-3B", 0, "test2"), "T82": ("Bonsai-8B", 0, "test2")}[split]
    return [_example(p, prop) for p in read_jsonl(RESULTS / "proposals" / f"{prop}.jsonl") if p["pool"] == pool and p["k"] == k]


def _example(p: dict, prop: str) -> dict:
    task, _ = campsite.task_by_id(p["pool"])[p["puzzle_id"]]
    cand = rc.normalise(task.grid, p["grid"])
    return {"id": f"{prop}:{p['pool']}:{p['puzzle_id']}:{p['k']}", "pool": p["pool"], "puzzle_id": p["puzzle_id"], "proposer": prop,
            "trees": task.grid, "rows": task.row_constraints, "cols": task.col_constraints, "cand": cand,
            "target": rc.nearest_solution(p["pool"], p["puzzle_id"], cand), "raw_grid": p["grid"]}


def tensors(exs: list[dict], framing: str, sym: bool):
    """Encoded tensors; with sym, one block per declared symmetry plus identity: shape [S, B, 36, C]."""
    import torch

    syms = ["identity"] + (rc.package()["symmetries"] if sym else [])
    F, L, M, V = [], [], [], []
    for s in syms:
        f_, l_, m_, v_ = [], [], [], []
        for e in exs:
            trees, rows, cols, cand, tgt = rc.transform(s, e["trees"], e["rows"], e["cols"], e["cand"], e["target"])
            f, lab, msk, val = rc.encode(framing, trees, rows, cols, cand, tgt)
            f_.append(f), l_.append(lab), m_.append(msk), v_.append(val)
        F.append(f_), L.append(l_), M.append(m_), V.append(v_)
    t = lambda x: torch.tensor(x, dtype=torch.float32)  # noqa: E731
    return t(F), t(L), t(M), t(V)


# ---------------------------------------------------------------------------- model


def build(channels: int):
    import torch
    from torch import nn

    class RepairTRM(nn.Module):
        """TRM-style recursion: one shared 2-layer transformer block updates a latent z (INNER times) and then the
        answer y, for CYCLES cycles; a per-cell tent logit is read from y."""

        def __init__(self):
            super().__init__()
            self.inp = nn.Linear(channels, D)
            self.row = nn.Embedding(rc.N, D)
            self.col = nn.Embedding(rc.N, D)
            layer = nn.TransformerEncoderLayer(D, HEADS, 2 * D, dropout=0.0, batch_first=True, norm_first=True)
            self.block = nn.TransformerEncoder(layer, LAYERS, enable_nested_tensor=False)
            self.head = nn.Linear(D, 1)
            idx = torch.arange(rc.N * rc.N)
            self.register_buffer("r_idx", idx // rc.N)
            self.register_buffer("c_idx", idx % rc.N)

        def forward(self, x, valid):
            pad = valid < 0.5
            e = self.inp(x) + self.row(self.r_idx) + self.col(self.c_idx)
            y = torch.zeros_like(e)
            z = torch.zeros_like(e)
            for _ in range(CYCLES):
                for _ in range(INNER):
                    z = self.block(e + y + z, src_key_padding_mask=pad)
                y = self.block(y + z, src_key_padding_mask=pad)
            return self.head(y).squeeze(-1)

    return RepairTRM()


def train(tr, lr: float, seed: int, stop_at: int, on_checkpoint=None):
    """Cosine schedule over SCHEDULE epochs; `on_checkpoint(epoch, model)` at each registered checkpoint up to stop_at."""
    import torch
    from torch import nn

    torch.manual_seed(seed)
    rng = random.Random(seed)
    F, L, M, V = tr
    S, B = F.shape[0], F.shape[1]
    model = build(F.shape[-1])
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=SCHEDULE * ((B + 63) // 64))
    for epoch in range(1, stop_at + 1):
        model.train()
        order = list(range(B))
        rng.shuffle(order)
        for i in range(0, B, 64):
            idx = torch.tensor(order[i:i + 64])
            s = torch.tensor([rng.randrange(S) for _ in range(len(idx))])
            x, y, m, v = F[s, idx], L[s, idx], M[s, idx], V[s, idx]
            logits = model(x, v)
            loss = (nn.functional.binary_cross_entropy_with_logits(logits, y, reduction="none") * m).sum() / m.sum()
            opt.zero_grad()
            loss.backward()
            opt.step()
            sched.step()
        if on_checkpoint and epoch in CHECKPOINTS:
            model.eval()
            on_checkpoint(epoch, model)
    model.eval()
    return model


def logits_for(model, t) -> list[list[float]]:
    import torch

    F, _, _, V = t
    with torch.no_grad():
        return model(F[0], V[0]).tolist()


def solved_rate(model, exs, t) -> float:
    ok = 0
    for e, l in zip(exs, logits_for(model, t)):
        task, _ = campsite.task_by_id(e["pool"])[e["puzzle_id"]]
        ok += campsite.passes(task, rc.decode(e["trees"], l))
    return ok / len(exs)


def subset_by_puzzle(exs, frac: float, seed: int):
    pids = sorted({e["pool"] + "|" + e["puzzle_id"] for e in exs})
    random.Random(f"curve:{seed}").shuffle(pids)
    keep = set(pids[: int(len(pids) * frac)])
    return [e for e in exs if e["pool"] + "|" + e["puzzle_id"] in keep]


def main() -> int:
    import torch

    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("run", "smoke"))
    ap.add_argument("--arm", choices=("raw", "atoms"), default="atoms")
    ap.add_argument("--sym", action="store_true")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--confirm", action="store_true", help="addendum R-A3: seeds 5-9 at the selected setting, plus TQ2/T82")
    args = ap.parse_args()
    torch.set_num_threads(args.threads)
    lower_priority()
    framing, sym = args.arm, args.sym
    tag = f"{framing}{'+sym' if sym else ''}"
    t0 = time.time()
    tr_exs, va_exs = examples("train"), examples("val")
    print(f"{tag}: train {len(tr_exs)} val {len(va_exs)} ({time.time() - t0:.0f}s)", flush=True)
    tr, va = tensors(tr_exs, framing, sym), tensors(va_exs, framing, False)
    if args.mode == "smoke":
        t1 = time.time()
        model = train(tr, 1e-3, 0, 1)
        print(f"smoke: 1 epoch {time.time() - t1:.0f}s, val solved {solved_rate(model, va_exs, va):.3f}")
        return 0
    test_names = TESTS + (("TQ2", "T82") if args.confirm else ())
    tests = {name: examples(name) for name in test_names}
    te = {name: tensors(exs, framing, False) for name, exs in tests.items()}
    OUT.mkdir(parents=True, exist_ok=True)
    log = OUT / f"runs.{tag}.jsonl"
    done = {(r["lr"], r["epochs"], r["seed"], r["frac"]) for r in read_jsonl(log)}

    def record(model, lr, epochs, seed, frac, rows, val):
        key = (lr, epochs, seed, frac)
        if key in done:
            return
        rec = {"framing": framing, "sym": sym, "lr": lr, "epochs": epochs, "seed": seed, "frac": frac, "train_rows": rows,
               "val_solved": val, "logits": {name: dict(zip((e["id"] for e in tests[name]), logits_for(model, te[name]))) for name in test_names}}
        with log.open("a", encoding="utf-8") as h:
            h.write(json.dumps(rec) + "\n")
        done.add(key)
        print(f"{tag} lr={lr} ep={epochs} seed={seed} frac={frac}: val {val:.3f} ({time.time() - t0:.0f}s)", flush=True)

    if args.confirm:  # R-A3: no reselection, new seeds only
        sel = json.loads((OUT / f"selected.{tag}.json").read_text(encoding="utf-8"))
        for seed in range(5, 10):
            if (sel["lr"], sel["epochs"], seed, 1.0) not in done:
                m = train(tr, sel["lr"], seed, sel["epochs"])
                record(m, sel["lr"], sel["epochs"], seed, 1.0, len(tr_exs), solved_rate(m, va_exs, va))
        print(f"{tag}: confirmation finished in {(time.time() - t0) / 60:.0f} min", flush=True)
        return 0
    # selection: one cosine run per learning rate, checkpoints at 20/40/80, seed 0
    for lr in LRS:
        if all((lr, ep, 0, 1.0) in done for ep in CHECKPOINTS):
            continue
        train(tr, lr, 0, SCHEDULE, lambda ep, m, lr=lr: record(m, lr, ep, 0, 1.0, len(tr_exs), solved_rate(m, va_exs, va)))
    grid = [r for r in read_jsonl(log) if r["seed"] == 0 and r["frac"] == 1.0]
    best = max(grid, key=lambda r: (r["val_solved"], -r["epochs"], r["lr"]))
    lr, ep = best["lr"], best["epochs"]
    write_json(OUT / f"selected.{tag}.json", {"framing": framing, "sym": sym, "lr": lr, "epochs": ep, "val_solved": best["val_solved"],
                                              "grid": [{"lr": r["lr"], "epochs": r["epochs"], "val_solved": r["val_solved"]} for r in grid]})
    for seed in SEEDS:
        if (lr, ep, seed, 1.0) not in done:
            m = train(tr, lr, seed, ep)
            record(m, lr, ep, seed, 1.0, len(tr_exs), solved_rate(m, va_exs, va))
    for frac in CURVE_FRACTIONS:
        for seed in CURVE_SEEDS:
            if (lr, ep, seed, frac) not in done:
                sub = subset_by_puzzle(tr_exs, frac, seed)
                m = train(tensors(sub, framing, sym), lr, seed, ep)
                record(m, lr, ep, seed, frac, len(sub), solved_rate(m, va_exs, va))
    print(f"{tag}: finished in {(time.time() - t0) / 60:.0f} min", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
