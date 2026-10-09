"""Score every policy, run the registered tests, and write results/report.md and results/report.json.

usage: python report.py
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import campsite  # noqa: E402
import metta_schema  # noqa: E402
from common import RESULTS, head_jsonl, read_jsonl, write_json  # noqa: E402

MENU = list(metta_schema.load().menu)
FEAT = {n: i for i, n in enumerate(metta_schema.load().feature_names)}


# ---------------------------------------------------------------------------- statistics


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def mcnemar(b: int, c: int, sides: str = "two") -> float:
    """Exact binomial on discordant pairs. b = first arm only, c = second arm only. One-sided: H1 b > c."""
    n = b + c
    if n == 0:
        return 1.0
    if sides == "one":
        return min(1.0, sum(math.comb(n, i) for i in range(b, n + 1)) / 2 ** n)
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def holm(pvals: dict[str, float]) -> dict[str, float]:
    order = sorted(pvals, key=pvals.get)
    out, running = {}, 0.0
    for i, k in enumerate(order):
        running = max(running, min(1.0, (len(order) - i) * pvals[k]))
        out[k] = running
    return out


def paired(a: dict[str, int], b: dict[str, int], sides: str = "two") -> dict:
    keys = sorted(set(a) & set(b))
    only_a = sum(1 for k in keys if a[k] and not b[k])
    only_b = sum(1 for k in keys if b[k] and not a[k])
    return {"n": len(keys), "a": sum(a[k] for k in keys), "b": sum(b[k] for k in keys), "a_only": only_a, "b_only": only_b,
            "p": mcnemar(only_a, only_b, sides)}


def rate(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({100 * k / n:.0f}%, {100 * lo:.0f}-{100 * hi:.0f})" if n else "0/0"


# ---------------------------------------------------------------------------- Part G policies


def outcome(row: dict, action: str, verify_after: bool = False) -> dict:
    """success / unsafe / rejected, plus operator and verifier calls."""
    ops_called = verifier_calls = 0
    if action == "reject":
        grid = None
    elif action == "commit":
        grid = row["candidate"]
        ok = row["pass_as_written"]
    else:
        ops_called = 1
        o = row["ops"][action]
        if o["applied"]:
            grid, ok = o["grid"], o["passes"]
        else:
            grid, ok = row["candidate"], row["pass_as_written"]
    if grid is None:
        return {"success": 0, "unsafe": 0, "rejected": 1, "ops": ops_called, "verifier": verifier_calls}
    if verify_after:
        verifier_calls = 1
        if not ok:
            return {"success": 0, "unsafe": 0, "rejected": 1, "ops": ops_called, "verifier": verifier_calls}
    return {"success": int(ok), "unsafe": int(not ok), "rejected": 0, "ops": ops_called, "verifier": verifier_calls}


def verify_policy(row: dict) -> dict:
    if row["pass_as_written"]:
        return {"success": 1, "unsafe": 0, "rejected": 0, "ops": 0, "verifier": 1}
    verifier = 1  # the candidate itself is verified first
    for i, op in enumerate(MENU[1:-1], start=1):  # operators in menu order; each output is verified
        o = row["ops"][op]
        verifier += 1 if o["applied"] else 0
        if o["applied"] and o["passes"]:
            return {"success": 1, "unsafe": 0, "rejected": 0, "ops": i, "verifier": verifier}
    return {"success": 0, "unsafe": 0, "rejected": 1, "ops": len(MENU) - 2, "verifier": verifier}


_signature_cache: dict = {}


def signatures(row: dict) -> tuple[bool, bool]:
    """Hermes-Skills T and C signature passes (False when the candidate is not rectangular), as the
    published flow policies compute them."""
    key = row["row_id"]
    if key not in _signature_cache:
        task, gold = campsite.task_by_id(row["pool"])[row["puzzle_id"]]
        cand = row["candidate"]
        if not campsite.rectangular(task, cand):
            _signature_cache[key] = (False, False)
        else:
            s = campsite.skills()
            _signature_cache[key] = (s.signature_pass(cand, gold, "T"), s.signature_pass(cand, gold, "C"))
    return _signature_cache[key]


def fixed_policy_action(row: dict, name: str) -> str:
    t_ok, c_ok = signatures(row)
    if name == "as-written":
        return "commit"
    if name == "flow-c":
        return "commit" if c_ok else "c_repair"
    if name == "flow-dual":
        return "commit" if (t_ok and c_ok) else "dual_repair"
    if name == "static":
        if row["pass_as_written"]:
            return "commit"
        if row["typed"][FEAT["shape_match"]] < 0.5:
            return "reject"
        return "c_repair" if row["typed"][FEAT["trees_unchanged"]] > 0.5 else "dual_repair"
    if name == "menu-ceiling":
        return row["best_action"]
    raise ValueError(name)


def majority(actions: list[str]) -> str:
    counts = Counter(actions)
    top = max(counts.values())
    return next(a for a in MENU if counts.get(a) == top)


def summarize(outcomes: list[dict]) -> dict:
    n = len(outcomes)
    s = {k: sum(o[k] for o in outcomes) for k in ("success", "unsafe", "rejected", "ops", "verifier")}
    return {"n": n, **s, "success_rate": s["success"] / n if n else 0, "unsafe_rate": s["unsafe"] / n if n else 0,
            "ops_per_item": s["ops"] / n if n else 0, "verifier_per_item": s["verifier"] / n if n else 0}


def part_g() -> dict:
    cur = RESULTS / "curriculum"
    syn = read_jsonl(cur / "synthetic.jsonl")
    r8 = read_jsonl(cur / "real-Bonsai-8B.jsonl")
    r27 = read_jsonl(cur / "real-Bonsai-27B.jsonl")
    rq = read_jsonl(cur / "real-Qwen2.5-3B.jsonl")
    tests = {"TQ": [r for r in rq if r["pool"] == "test" and r["k"] == 0],
             "TQs": [r for r in rq if r["pool"] == "test" and r["k"] == 1],
             "T8": [r for r in r8 if r["pool"] == "test" and r["k"] == 0],
             "T8s": [r for r in r8 if r["pool"] == "test" and r["k"] == 1],
             "T27": [r for r in r27 if r["pool"] == "test" and r["k"] == 0],
             "synthetic": [r for r in syn if r["pool"] == "test"]}
    preds = read_jsonl(RESULTS / "gates" / "predictions.jsonl")
    configs: dict = defaultdict(list)
    for p in preds:
        configs[(p["source"], p["features"], str(p["n"]))].append(p)
    out: dict = {"curriculum": {}, "policies": {}, "curves": {}, "seeds": {}, "tests": {}}

    # curriculum description
    for name, rows in [("synthetic", syn), ("real-Bonsai-8B", r8), ("real-Bonsai-27B", r27), ("real-Qwen2.5-3B", rq)]:
        out["curriculum"][name] = {
            "rows": len(rows),
            "pool_bucket": {f"{p}|{b}": n for (p, b), n in sorted(Counter((r["pool"], r["bucket"]) for r in rows).items())},
            "pool_best": {f"{p}|{a}": n for (p, a), n in sorted(Counter((r["pool"], r["best_action"]) for r in rows).items())},
            "failed_gate_patterns": Counter("+".join(r["failed_gate_names"]) or "none" for r in rows).most_common(8),
            "unparsed": sum(1 for r in rows if r["candidate"] is None),
        }

    per_item: dict = {}
    for tname, rows in tests.items():
        if not rows:
            continue
        pol: dict = {}
        for name in ("as-written", "flow-c", "flow-dual", "static", "menu-ceiling"):
            pol[name] = [outcome(r, fixed_policy_action(r, name)) for r in rows]
        pol["verify"] = [verify_policy(r) for r in rows]
        pol["CSP"] = [{"success": 1, "unsafe": 0, "rejected": 0, "ops": 0, "verifier": 0} for _ in rows]
        for (source, features, n), recs in configs.items():
            if n != "all" or f"test:{tname}" not in recs[0]["predictions"]:
                continue
            acts = [majority([rec["predictions"][f"test:{tname}"][r["row_id"]] for rec in recs]) for r in rows]
            tag = f"TRM[{features},{source}]"
            pol[tag] = [outcome(r, a) for r, a in zip(rows, acts)]
            pol[tag + "+verify"] = [outcome(r, a, verify_after=True) for r, a in zip(rows, acts)]
            out["seeds"].setdefault(tname, {})[tag] = [
                summarize([outcome(r, rec["predictions"][f"test:{tname}"][r["row_id"]]) for r in rows]) for rec in recs]
        out["policies"][tname] = {k: summarize(v) for k, v in pol.items()}
        per_item[tname] = {k: {"success": {r["puzzle_id"]: o["success"] for r, o in zip(rows, v)},
                               "unsafe": {r["puzzle_id"]: o["unsafe"] for r, o in zip(rows, v)}} for k, v in pol.items()}
        # learning curves: mean and sd over seeds
        for (source, features, n), recs in configs.items():
            if f"test:{tname}" not in recs[0]["predictions"]:
                continue
            vals = [summarize([outcome(r, rec["predictions"][f"test:{tname}"][r["row_id"]]) for r in rows]) for rec in recs]
            out["curves"].setdefault(tname, {}).setdefault(f"{features}|{source}", {})[n] = {
                "success_mean": statistics.mean(v["success_rate"] for v in vals),
                "success_sd": statistics.pstdev(v["success_rate"] for v in vals),
                "unsafe_mean": statistics.mean(v["unsafe_rate"] for v in vals),
                "n_rows": statistics.mean(rec["n_rows"] for rec in recs),
                "val_acc_mean": statistics.mean(rec["val_accuracy"] for rec in recs)}

    # registered tests
    reg = {}
    if "T8" in per_item and "TRM[typed,real]" in per_item["T8"]:
        T8 = per_item["T8"]
        reg["G1"] = paired(T8["TRM[typed,real]"]["success"], T8["TRM[typed,synthetic]"]["success"], "two")
        reg["G2"] = paired(T8["TRM[typed,real]"]["success"], T8["TRM[raw,real]"]["success"], "two")
        # one-sided: TRM has fewer unsafe -> flow-dual-only unsafe exceeds TRM-only unsafe
        u = paired(T8["flow-dual"]["unsafe"], T8["TRM[typed,real]"]["unsafe"], "one")
        reg["G3"] = {**u, "note": "a = flow-dual unsafe, b = TRM unsafe; H1: a_only > b_only"}
    if "T27" in per_item and "TRM[typed,real]" in per_item.get("T27", {}):
        T27 = per_item["T27"]
        u = paired(T27["flow-dual"]["unsafe"], T27["TRM[typed,real]"]["unsafe"], "one")
        reg["G4"] = {**u, "note": "a = flow-dual unsafe, b = TRM unsafe; H1: a_only > b_only"}
    if reg:
        adj = holm({k: v["p"] for k, v in reg.items()})
        for k in reg:
            reg[k]["p_holm"] = adj[k]
    out["tests"] = reg
    # Qwen2.5-3B family (addendum A3), its own Holm correction
    regq = {}
    if "TQ" in per_item and "TRM[typed,realq]" in per_item["TQ"]:
        TQ = per_item["TQ"]
        regq["G1q"] = paired(TQ["TRM[typed,realq]"]["success"], TQ["TRM[typed,synthetic]"]["success"], "two")
        regq["G2q"] = paired(TQ["TRM[typed,realq]"]["success"], TQ["TRM[raw,realq]"]["success"], "two")
        regq["G3q"] = {**paired(TQ["flow-dual"]["unsafe"], TQ["TRM[typed,realq]"]["unsafe"], "one"),
                       "note": "a = flow-dual unsafe, b = TRM unsafe"}
        if "TRM[typed,realq]" in per_item.get("T8", {}):
            regq["G4q"] = {**paired(per_item["T8"]["flow-dual"]["unsafe"], per_item["T8"]["TRM[typed,realq]"]["unsafe"], "one"),
                           "note": "a = flow-dual unsafe, b = TRM unsafe, on Bonsai-8B answers"}
        adj = holm({k: v["p"] for k, v in regq.items()})
        for k in regq:
            regq[k]["p_holm"] = adj[k]
    out["tests_q"] = regq
    # cross-proposer matrix: typed gates by training source, on each real test set
    out["cross"] = {t: {s: {k: out["policies"][t][f"TRM[typed,{s}]"][k] for k in ("success", "unsafe", "rejected", "n")}
                        for s in ("real", "realq", "synthetic") if f"TRM[typed,{s}]" in out["policies"].get(t, {})}
                    for t in ("TQ", "T8", "T27") if t in out["policies"]}
    out["gate_info"] = {f"{s}|{f}": [{"val_accuracy": r["val_accuracy"], "steps": r["steps"], "params": r["params"]}
                                      for r in recs] for (s, f, n), recs in configs.items() if n == "all"}
    return out


# ---------------------------------------------------------------------------- Part R


def part_r() -> dict:
    d = RESULTS / "rudder"
    arms = {}
    for path in sorted(d.glob("bonsai8b.*.jsonl")):
        arms["Bonsai-8B " + path.stem.split(".", 1)[1]] = read_jsonl(path)
    arms["lookup"] = read_jsonl(d / "cpu.lookup.jsonl")
    trm = read_jsonl(d / "cpu.trm.jsonl")
    if trm:
        by_key = defaultdict(list)
        for r in trm:
            by_key[r["key"]].append(r)
        maj = []
        for k, rs in by_key.items():
            rep = Counter(r["pred_repair"] for r in rs).most_common(1)[0][0]
            act = Counter(r["pred_action"] for r in rs).most_common(1)[0][0]
            base = dict(rs[0])
            base.update(pred_repair=rep, pred_action=act, repair_ok=int(rep == base["target_repair"]),
                        action_ok=int(act == base["target_action"]),
                        joint_ok=int(rep == base["target_repair"] and act == base["target_action"]),
                        false_commit=int(base["target_action"] == "reject_or_abstain" and act == "commit"))
            maj.append(base)
        arms["TRM (5-seed vote)"] = maj
    # published rows, rescored
    pub = {"3B": "local_3b_repair_training_rudder_benchmark/local_3b_repair_training_rudder.rows.jsonl",
           "3B action-space": "local_3b_metta_action_space_rudder_benchmark/local_3b_repair_training_rudder.rows.jsonl",
           "9B": "remote_9b_repair_training_rudder_20260502T203509Z/remote_repair_training_rudder.rows.jsonl",
           "27B": "remote_27b_repair_training_rudder_20260502T204314Z/remote_repair_training_rudder.rows.jsonl"}
    base = "research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/"
    published = {}
    for label, path in pub.items():
        for r in head_jsonl(base + path):
            model = label.split()[0]
            key = f"{r['eval_split']}|{r['case_id']}"
            published.setdefault(f"published {model} {r['arm']}", []).append(
                {"key": key, "split": r["eval_split"], "joint_ok": r["joint_correct"], "repair_ok": r["repair_action_correct"],
                 "action_ok": r["target_action_correct"], "pred_action": r["predicted_target_action"],
                 "target_action": r["target_action"],
                 "false_commit": int(r["target_action"] == "reject_or_abstain" and r["predicted_target_action"] == "commit")})
    arms.update(published)
    table = {}
    for name, rs in arms.items():
        if not rs:
            continue
        n = len(rs)
        table[name] = {"n": n, "joint": sum(r["joint_ok"] for r in rs), "repair": sum(r["repair_ok"] for r in rs),
                       "action": sum(r["action_ok"] for r in rs), "false_commit": sum(r["false_commit"] for r in rs),
                       "commits": sum(r["pred_action"] == "commit" for r in rs),
                       "unseen_joint": sum(r["joint_ok"] for r in rs if r["split"] == "holdout_unseen_family"),
                       "seen_joint": sum(r["joint_ok"] for r in rs if r["split"] != "holdout_unseen_family")}
    tests = {}

    def jmap(name):
        return {r["key"]: r["joint_ok"] for r in arms.get(name, [])}

    if arms.get("Bonsai-8B retrieval-clean") and arms.get("Bonsai-8B raw"):
        tests["R1"] = paired(jmap("Bonsai-8B retrieval-clean"), jmap("Bonsai-8B raw"))
    if arms.get("Bonsai-8B retrieval-published") and arms.get("Bonsai-8B retrieval-clean"):
        tests["R2"] = paired(jmap("Bonsai-8B retrieval-published"), jmap("Bonsai-8B retrieval-clean"))
    if tests:
        adj = holm({k: v["p"] for k, v in tests.items()})
        for k in tests:
            tests[k]["p_holm"] = adj[k]
    return {"table": table, "tests": tests}


# ---------------------------------------------------------------------------- Part M


def part_m() -> dict:
    out: dict = {"table": {}, "families": {}, "tests": {}}
    for suite in ("heldout50", "hard30"):
        rows = read_jsonl(RESULTS / "mixed" / f"bonsai8b.{suite}.jsonl")
        if not rows:
            continue
        by_arm = defaultdict(dict)
        fam = defaultdict(lambda: defaultdict(lambda: [0, 0]))
        for r in rows:
            by_arm[r["arm"]][r["row_id"]] = int(r["exact_success"])
            fam[r["arm"]][r["env_family"]][0] += int(r["exact_success"])
            fam[r["arm"]][r["env_family"]][1] += 1
        out["table"][suite] = {a: {"n": len(v), "exact": sum(v.values()),
                                   "contract_valid": sum(int(r["contract_valid"]) for r in rows if r["arm"] == a)}
                               for a, v in by_arm.items()}
        out["families"][suite] = {a: {f: f"{k}/{n}" for f, (k, n) in v.items()} for a, v in fam.items()}
        if suite == "heldout50" and all(a in by_arm for a in ("baseline", "contract-neutral", "gate-wording", "repair-feedback", "repair-blind")):
            t = {"M1": paired(by_arm["contract-neutral"], by_arm["baseline"]),
                 "M2": paired(by_arm["gate-wording"], by_arm["contract-neutral"]),
                 "M3": paired(by_arm["repair-feedback"], by_arm["repair-blind"])}
            adj = holm({k: v["p"] for k, v in t.items()})
            for k in t:
                t[k]["p_holm"] = adj[k]
            out["tests"] = t
    # published 3B rows for the same suites, for comparison
    pubs = {"heldout50": "research/studies/2026-04-28-mixed-contract-compactification-heldout50/results/local_qwen25_3b_mixed_contract_heldout50/local_qwen25_3b_mixed_contract.results.json",
            "hard30": "research/studies/2026-04-28-mixed-contract-hard-ablation30/results/local_qwen25_3b_mixed_contract_hard_ablation30/local_qwen25_3b_mixed_contract.results.json"}
    from common import git_show

    out["published_3b"] = {}
    for suite, path in pubs.items():
        ev = json.loads(git_show(path))["evaluated"]
        out["published_3b"][suite] = dict(Counter(r["arm"] for r in ev if r["exact_success"]))
    return out


def part_q() -> dict:
    """Addendum A3: Qwen2.5-3B replication with the April runners, fidelity against the published 3B rows."""
    import json as _json
    from common import git_show

    q = RESULTS / "qwen3b"
    out: dict = {"R": {}, "M": {}, "C": {}}
    base = "research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/"
    pub = {}
    for path in ("local_3b_repair_training_rudder_benchmark/local_3b_repair_training_rudder.rows.jsonl",
                 "local_3b_metta_action_space_rudder_benchmark/local_3b_repair_training_rudder.rows.jsonl"):
        for r in head_jsonl(base + path):
            pub[(r["arm"], f"{r['eval_split']}|{r['case_id']}")] = r
    ours = read_jsonl(q / "rudder_published" / "local_3b_repair_training_rudder.rows.jsonl")
    arms: dict = defaultdict(dict)
    for r in ours:
        k = f"{r['eval_split']}|{r['case_id']}"
        arms[r["arm"]][k] = {"joint_ok": r["joint_correct"], "repair_ok": r["repair_action_correct"], "action_ok": r["target_action_correct"],
                             "pred": (r["predicted_repair_action"], r["predicted_target_action"]), "target_action": r["target_action"],
                             "split": r["eval_split"]}
    for arm in ("raw-fullvocab", "retrieval-clean"):
        for r in read_jsonl(q / f"rudder_extra.{arm}.jsonl"):
            arms[arm][r["key"]] = {"joint_ok": r["joint_ok"], "repair_ok": r["repair_ok"], "action_ok": r["action_ok"],
                                   "pred": (r["pred_repair"], r["pred_action"]), "target_action": r["target_action"], "split": r["split"]}
    table = {}
    for arm, rows in arms.items():
        agree = [rows[k]["pred"] == (pub[(arm, k)]["predicted_repair_action"], pub[(arm, k)]["predicted_target_action"])
                 for k in rows if (arm, k) in pub]
        pub_joint = sum(pub[(arm, k)]["joint_correct"] for k in rows if (arm, k) in pub)
        table[arm] = {"n": len(rows), "joint": sum(v["joint_ok"] for v in rows.values()), "repair": sum(v["repair_ok"] for v in rows.values()),
                      "action": sum(v["action_ok"] for v in rows.values()),
                      "commits": sum(v["pred"][1] == "commit" for v in rows.values()),
                      "false_commit": sum(v["pred"][1] == "commit" and v["target_action"] == "reject_or_abstain" for v in rows.values()),
                      "unseen_joint": sum(v["joint_ok"] for v in rows.values() if v["split"] == "holdout_unseen_family"),
                      "published_joint": pub_joint if agree else None,
                      "agreement": (sum(agree), len(agree)) if agree else None}
    out["R"]["table"] = table
    tests = {}
    jm = lambda a: {k: v["joint_ok"] for k, v in arms.get(a, {}).items()}  # noqa: E731
    if arms.get("retrieval-clean") and arms.get("raw_3b_rudder"):
        tests["R1q"] = paired(jm("retrieval-clean"), jm("raw_3b_rudder"))
    if arms.get("repair_training_rudder") and arms.get("retrieval-clean"):
        tests["R2q"] = paired(jm("repair_training_rudder"), jm("retrieval-clean"))
    if tests:
        adj = holm({k: v["p"] for k, v in tests.items()})
        for k in tests:
            tests[k]["p_holm"] = adj[k]
    out["R"]["tests"] = tests

    pubm = {"heldout50": "research/studies/2026-04-28-mixed-contract-compactification-heldout50/results/local_qwen25_3b_mixed_contract_heldout50/local_qwen25_3b_mixed_contract.results.json",
            "hard30": "research/studies/2026-04-28-mixed-contract-hard-ablation30/results/local_qwen25_3b_mixed_contract_hard_ablation30/local_qwen25_3b_mixed_contract.results.json"}
    for suite in ("heldout50", "hard30"):
        path = q / f"mixed_{suite}" / "local_qwen25_3b_mixed_contract.results.json"
        if not path.exists():
            continue
        ev = _json.loads(path.read_text(encoding="utf-8"))["evaluated"]
        pev = {(r["row_id"], r["arm"]): r for r in _json.loads(git_show(pubm[suite]))["evaluated"]}
        by = defaultdict(dict)
        tab = {}
        for r in ev:
            by[r["arm"]][r["row_id"]] = int(r["exact_success"])
        for r in read_jsonl(q / f"mixed_neutral.{suite}.jsonl"):
            by["contract-neutral"][r["row_id"]] = int(r["exact_success"])
        for arm, rows in by.items():
            same_exact = [rows[rid] == int(pev[(rid, arm)]["exact_success"]) for rid in rows if (rid, arm) in pev]
            same_text = [next(x for x in ev if x["row_id"] == rid and x["arm"] == arm)["output"].strip() == pev[(rid, arm)]["output"].strip()
                         for rid in rows if (rid, arm) in pev]
            tab[arm] = {"n": len(rows), "exact": sum(rows.values()),
                        "published_exact": sum(int(pev[(rid, arm)]["exact_success"]) for rid in rows if (rid, arm) in pev) if same_exact else None,
                        "same_verdict": (sum(same_exact), len(same_exact)) if same_exact else None,
                        "same_output": (sum(same_text), len(same_text)) if same_text else None}
        out["M"][suite] = tab
        if suite == "heldout50" and "contract-neutral" in by:
            mt = {"M1q": paired(by["contract-neutral"], by["baseline"]), "M2q": paired(by["metta_runtime"], by["contract-neutral"]),
                  "M3q": paired(by["metta_runtime_repair"], by["metta_runtime_blind_repair"])}
            adj = holm({k: v["p"] for k, v in mt.items()})
            for k in mt:
                mt[k]["p_holm"] = adj[k]
            out["M"]["tests"] = mt
    cpath = q / "campgate_noisy" / "local_qwen25_3b_constraint_extract.results.json"
    if cpath.exists():
        ev = _json.loads(cpath.read_text(encoding="utf-8"))["evaluated"]
        pubc = _json.loads(git_show("research/studies/2026-04-29-logic-signature-camp-gate-leakage-safe/results/local_qwen25_3b_noisy_graph_constraint_extract/local_qwen25_3b_constraint_extract.results.json"))["evaluated"]
        for name, rows in (("ours", ev), ("published", pubc)):
            c = defaultdict(lambda: [0, 0])
            for r in rows:
                c[r["arm"]][0] += int(r["repair_solve_exact"])
                c[r["arm"]][1] += 1
            out["C"][name] = {a: f"{k}/{n}" for a, (k, n) in c.items()}
    return out


def main() -> int:
    report = {"G": part_g(), "R": part_r(), "M": part_m(), "Q": part_q()}
    write_json(RESULTS / "report.json", report)
    lines = ["# Study report (generated by src/report.py)", ""]
    g = report["G"]
    for tname, pols in g["policies"].items():
        lines += [f"## Part G policies on {tname}", "", "| Policy | Success | Unsafe | Rejected | Ops/item | Verifier/item |",
                  "|---|---|---|---|---|---|"]
        for name, s in pols.items():
            lines.append(f"| {name} | {rate(s['success'], s['n'])} | {rate(s['unsafe'], s['n'])} | {s['rejected']} | "
                         f"{s['ops_per_item']:.2f} | {s['verifier_per_item']:.2f} |")
        lines.append("")
    lines += ["## Part G registered tests", "", "```", json.dumps(g["tests"], indent=1), "```", ""]
    lines += ["## Part G learning curves (success mean over seeds)", ""]
    for tname, curves in g["curves"].items():
        lines.append(f"### {tname}")
        for cfg, pts in sorted(curves.items()):
            seq = sorted(pts.items(), key=lambda kv: (kv[0] == "all", int(kv[0]) if kv[0] != "all" else 0))
            lines.append(f"- {cfg}: " + ", ".join(f"N={k} ({v['n_rows']:.0f} rows) {100 * v['success_mean']:.0f}%±{100 * v['success_sd']:.0f} "
                                                  f"unsafe {100 * v['unsafe_mean']:.0f}%" for k, v in seq))
        lines.append("")
    lines += ["## Curriculum", "", "```", json.dumps(g["curriculum"], indent=1), "```", ""]
    r = report["R"]
    lines += ["## Part R", "", "| Arm | Joint/88 | Repair | Action | Commits | False commits/22 | Seen joint/70 | Unseen joint/18 |",
              "|---|---|---|---|---|---|---|---|"]
    for name, s in r["table"].items():
        lines.append(f"| {name} | {s['joint']} | {s['repair']} | {s['action']} | {s['commits']} | {s['false_commit']} | "
                     f"{s['seen_joint']} | {s['unseen_joint']} |")
    lines += ["", "```", json.dumps(r["tests"], indent=1), "```", ""]
    m = report["M"]
    lines += ["## Part M", "", "```", json.dumps({k: m[k] for k in ("table", "tests", "published_3b")}, indent=1), "```", "",
              "```", json.dumps(m["families"], indent=1), "```"]
    (RESULTS / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:60]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
