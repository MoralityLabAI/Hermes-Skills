"""Part R: the 88-row repair-rudder benchmark, rerun without the two defects.

Prompt builders, the published (leaky) retrieval, the MeTTa action table and the JSON parser are the
published runner's own functions, executed from Hermes-Skills HEAD.

usage: python rudder.py llm [--arms raw,...]   (Bonsai-8B, CPU)
       python rudder.py cpu                    (two-head TRM, lookup)
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS, append_jsonl, head_jsonl, head_module, lower_priority, read_jsonl, write_json  # noqa: E402

RUNNER = "research/scripts/run_3b_repair_training_rudder_benchmark.py"
SPLITS = "research/generated/near_miss_repair_curriculum/splits"
EVAL_SPLITS = ("val_seen", "holdout_seen", "holdout_unseen_family")
LLM_ARMS = ("raw", "raw-fullvocab", "retrieval-published", "retrieval-clean", "action-space")
OUT = RESULTS / "rudder"
SHOTS = 4


@lru_cache(maxsize=None)
def pub():
    return head_module(RUNNER, "published_rudder_runner", stubs=("psutil",))


@lru_cache(maxsize=None)
def rows() -> dict[str, list[dict]]:
    out = {s: head_jsonl(f"{SPLITS}/{s}.pure_trm.jsonl") for s in ("train", *EVAL_SPLITS)}
    for split, rs in out.items():
        for r in rs:
            r["_split"] = split
    return out


def eval_rows() -> list[dict]:
    return [r for s in EVAL_SPLITS for r in rows()[s]]


def key(row) -> str:
    return f"{row['_split']}|{row['state']['case_id']}"


def train_actions() -> list[str]:
    return sorted({str(r.get("action") or "") for r in rows()["train"] if r.get("action")})


def all_actions() -> list[str]:
    return sorted({str(r.get("action") or "") for s in rows().values() for r in s if r.get("action")})


def _tokens(parts) -> Counter:
    return Counter(re.findall(r"[a-z0-9_]+", " ".join(str(p or "").lower() for p in parts)))


def clean_retrieve(train: list[dict], query: dict, shots: int = SHOTS) -> list[dict]:
    """The published scorer with the outcome removed: tokens and bonuses use pre-repair fields only."""
    def parts(row):
        s = row.get("state") or {}
        return [s.get("env_family"), s.get("trm_role"), s.get("before_arm"), s.get("after_arm"), s.get("failure_label"),
                s.get("candidate_excerpt")]
    q = _tokens(parts(query))
    qs = query.get("state") or {}
    scored = []
    for row in train:
        rt = _tokens(parts(row))
        s = row.get("state") or {}
        score = sum(min(q[t], rt[t]) for t in q) + (3.0 if s.get("trm_role") == qs.get("trm_role") else 0.0) + \
            (5.0 if s.get("failure_label") == qs.get("failure_label") else 0.0)
        scored.append((score, str(s.get("case_id") or ""), row))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [r for _, _, r in scored[:shots]]


def messages_for(arm: str, row: dict) -> tuple[list[dict], str | None, list[str]]:
    p, train = pub(), rows()["train"]
    if arm == "raw":
        return p.make_prompt("raw_3b_rudder", row, [], train_actions()), None, []
    if arm == "raw-fullvocab":
        return p.make_prompt("raw_3b_rudder", row, [], all_actions()), None, []
    if arm == "retrieval-published":
        ex = p.retrieve_examples(train, row, SHOTS)
        return p.make_prompt("repair_training_rudder", row, ex, train_actions()), None, [e["state"]["case_id"] for e in ex]
    if arm == "retrieval-clean":
        ex = clean_retrieve(train, row)
        return p.make_prompt("repair_training_rudder", row, ex, train_actions()), None, [e["state"]["case_id"] for e in ex]
    if arm == "action-space":
        fixed = p.metta_repair_action(row)
        return p.make_fixed_repair_prompt("metta_action_space_rudder", row, [], fixed), fixed, []
    raise ValueError(arm)


def score(row: dict, repair: str, action: str, **extra) -> dict:
    tr, ta = str(row.get("action") or ""), str(row.get("target_action") or "")
    return {"key": key(row), "split": row["_split"], "case_id": row["state"]["case_id"],
            "failure_label": row["state"].get("failure_label"), "bucket": row.get("bucket"),
            "target_repair": tr, "target_action": ta, "pred_repair": repair, "pred_action": action,
            "repair_ok": int(repair == tr), "action_ok": int(action == ta), "joint_ok": int(repair == tr and action == ta),
            "false_commit": int(ta == "reject_or_abstain" and action == "commit"), **extra}


def run_llm(arms: list[str]) -> None:
    import bonsai

    lower_priority()
    with bonsai.Server("Bonsai-8B", threads=8, slots=1, ctx_per_slot=8192) as server:
        write_json(OUT / "server.json", {"model": "Bonsai-8B", "sha256": server.sha256, "gpu_layers": 0, "max_tokens": 64,
                                         "temperature": 0.0})
        for arm in arms:
            path = OUT / f"bonsai8b.{arm}.jsonl"
            done = {r["key"] for r in read_jsonl(path)}
            for row in eval_rows():
                if key(row) in done:
                    continue
                msgs, fixed, retrieved = messages_for(arm, row)
                t0 = time.time()
                out = server.chat(msgs, max_tokens=64)
                parsed = pub().parse_model_json(out["content"])
                repair = fixed if fixed is not None else parsed["repair_action"]
                append_jsonl(path, score(row, repair, parsed["target_action"], arm=arm, raw_output=out["content"],
                                         retrieved=retrieved, latency_s=round(time.time() - t0, 2),
                                         json_ok=int(bool(parsed["repair_action"] or parsed["target_action"]))))
            print(f"{arm}: done", flush=True)


# ---------------------------------------------------------------------------- CPU arms


def after_keyword(row) -> str:
    after = str((row.get("state") or {}).get("after_arm") or "")
    for kw in ("dual_repair", "c_repair", "original"):
        if kw in after:
            return kw
    return "other"


def lookup_arm() -> list[dict]:
    """Train majority repair and commit action per (failure_label, after-arm keyword), else global majority."""
    train = rows()["train"]
    cells: dict = {}
    for r in train:
        cells.setdefault((r["state"].get("failure_label"), after_keyword(r)), []).append(r)
    g_rep = Counter(r["action"] for r in train).most_common(1)[0][0]
    g_act = Counter(r["target_action"] for r in train).most_common(1)[0][0]
    out = []
    for row in eval_rows():
        cell = cells.get((row["state"].get("failure_label"), after_keyword(row)))
        rep = Counter(r["action"] for r in cell).most_common(1)[0][0] if cell else g_rep
        act = Counter(r["target_action"] for r in cell).most_common(1)[0][0] if cell else g_act
        out.append(score(row, rep, act, arm="lookup"))
    return out


def trm_arm(seed: int) -> tuple[list[dict], dict]:
    """Two-head tiny recursive model on the published state fields (as jev-qwen U3)."""
    import torch
    from torch import nn

    torch.manual_seed(seed)
    train, val = rows()["train"], rows()["val_seen"]
    fields = ("env_family", "trm_role", "before_arm", "failure_label")
    vocab = {f: sorted({str(r["state"].get(f)) for r in train}) + ["<unk>"] for f in fields}
    kws = ["dual_repair", "c_repair", "original", "other"]
    acts = train_actions()

    def feat(r):
        v = []
        for f in fields:
            val_ = str(r["state"].get(f))
            v += [float(val_ == x) for x in vocab[f][:-1]] + [float(val_ not in vocab[f][:-1])]
        v += [float(after_keyword(r) == k) for k in kws] + [float(r["state"].get("before_reward") or 0.0)]
        return v

    X = torch.tensor([feat(r) for r in train])
    yr = torch.tensor([acts.index(r["action"]) for r in train])
    ya = torch.tensor([int(r["target_action"] == "commit") for r in train])

    class TRM(nn.Module):
        def __init__(self, d, h=2048, steps=4):
            super().__init__()
            self.inp, self.tr, self.norm, self.steps = nn.Linear(d, h), nn.Linear(h, h), nn.LayerNorm(h), steps
            self.rep, self.act = nn.Linear(h, len(acts)), nn.Linear(h, 2)

        def forward(self, x):
            z = torch.tanh(self.inp(x))
            for _ in range(self.steps):
                z = self.norm(z + torch.tanh(self.tr(z)))
            return self.rep(z), self.act(z)

    def predict(model, rs):
        with torch.no_grad():
            r_, a_ = model(torch.tensor([feat(r) for r in rs]))
        return [(acts[i], "commit" if j == 1 else "reject_or_abstain") for i, j in zip(r_.argmax(1).tolist(), a_.argmax(1).tolist())]

    best = None
    for epochs in (8, 25, 50, 100):
        torch.manual_seed(seed)
        model = TRM(X.shape[1])
        opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
        for _ in range(epochs):
            opt.zero_grad()
            r_, a_ = model(X)
            loss = nn.functional.cross_entropy(r_, yr) + nn.functional.cross_entropy(a_, ya)
            loss.backward()
            opt.step()
        joint = sum(p == (r["action"], r["target_action"]) for p, r in zip(predict(model, val), val)) / len(val)
        if best is None or joint > best[0]:
            best = (joint, epochs, model)
    joint, epochs, model = best
    preds = predict(model, eval_rows())
    out = [score(r, p[0], p[1], arm="trm", seed=seed) for r, p in zip(eval_rows(), preds)]
    return out, {"seed": seed, "epochs": epochs, "val_joint": joint, "params": sum(p.numel() for p in model.parameters())}


def run_cpu() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "cpu.lookup.jsonl").write_text("".join(__import__("json").dumps(r) + "\n" for r in lookup_arm()), encoding="utf-8")
    infos, trm_rows = [], []
    for seed in range(5):
        rs, info = trm_arm(seed)
        trm_rows += rs
        infos.append(info)
    (OUT / "cpu.trm.jsonl").write_text("".join(__import__("json").dumps(r) + "\n" for r in trm_rows), encoding="utf-8")
    write_json(OUT / "cpu.trm.info.json", infos)
    # Published rows, rescored for false commits and the always-commit decomposition.
    print("cpu arms written", infos, flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("llm", "cpu", "dry"))
    ap.add_argument("--arms", default=",".join(LLM_ARMS))
    args = ap.parse_args()
    if args.mode == "llm":
        run_llm(args.arms.split(","))
    elif args.mode == "cpu":
        run_cpu()
    else:
        for arm in LLM_ARMS:
            msgs, fixed, retrieved = messages_for(arm, eval_rows()[0])
            print("=====", arm, fixed, retrieved)
            print(msgs[0]["content"][:300])
            print(msgs[1]["content"][:900])
        print("train actions", train_actions())
        print("all actions", all_actions())
        print("eval rows", len(eval_rows()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
