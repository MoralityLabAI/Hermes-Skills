"""SPEC-R report: registered tests P1-P4 and descriptives for the repair TRM corpus-framing study.

usage: python repair_report.py
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import campsite  # noqa: E402
import repair_cells as rc  # noqa: E402
import repair_trm as rt  # noqa: E402
import report  # noqa: E402
from common import RESULTS, read_jsonl, write_json  # noqa: E402

OUT = RESULTS / "repair_trm"
ARMS = ("raw", "atoms", "raw+sym", "atoms+sym")


def load_arm(tag: str):
    sel_path = OUT / f"selected.{tag}.json"
    if not sel_path.exists():
        return None
    sel = json.loads(sel_path.read_text(encoding="utf-8"))
    runs = read_jsonl(OUT / f"runs.{tag}.jsonl")
    seeds = [r for r in runs if r["lr"] == sel["lr"] and r["epochs"] == sel["epochs"] and r["frac"] == 1.0 and r["seed"] < 5]
    confirm = [r for r in runs if r["lr"] == sel["lr"] and r["epochs"] == sel["epochs"] and r["frac"] == 1.0 and 5 <= r["seed"] < 10]
    curves = defaultdict(list)
    for r in runs:
        if r["lr"] == sel["lr"] and r["epochs"] == sel["epochs"]:
            curves[r["frac"]].append(r)
    return {"selected": sel, "seeds": seeds, "curves": curves, "confirm": confirm}


def passes(e, logits) -> int:
    task, _ = campsite.task_by_id(e["pool"])[e["puzzle_id"]]
    return int(campsite.passes(task, rc.decode(e["trees"], logits)))


def ensemble(seeds, name, eid):
    """Per-cell majority over seeds, expressed as +1/-1 logits."""
    votes = [s["logits"][name][eid] for s in seeds]
    return [1.0 if sum(v[i] > 0 for v in votes) * 2 > len(votes) else -1.0 for i in range(len(votes[0]))]


def main() -> int:
    arms = {tag: load_arm(tag) for tag in ARMS}
    arms = {k: v for k, v in arms.items() if v and len(v["seeds"]) == 5}
    cur = {}
    for prop in ("Qwen2.5-3B", "Bonsai-8B", "Bonsai-27B"):
        for r in read_jsonl(RESULTS / "curriculum" / f"real-{prop}.jsonl"):
            cur[r["row_id"]] = r
    out = {"selected": {k: v["selected"] for k, v in arms.items()}, "policies": {}, "seed_spread": {}, "curves": {}, "by_distance": {},
           "beyond_operators": {}, "tests": {}}
    per_item = {}
    for name in rt.TESTS:
        exs = rt.examples(name)
        menu = {e["puzzle_id"]: report.verify_policy(cur[e["id"]])["success"] for e in exs}
        pol = {"menu": menu, "CSP": {e["puzzle_id"]: 1 for e in exs}}
        dist = {}
        for e in exs:
            sols = rc.solutions(e["pool"], e["puzzle_id"])
            dist[e["puzzle_id"]] = min(sum(x != y for ra, rb in zip(s, e["cand"]) for x, y in zip(ra, rb)) for s in sols)
        for tag, a in arms.items():
            trm = {e["puzzle_id"]: passes(e, ensemble(a["seeds"], name, e["id"])) for e in exs}
            pol[f"TRM[{tag}]"] = trm
            pol[f"menu+TRM[{tag}]"] = {k: int(menu[k] or trm[k]) for k in menu}
            out["seed_spread"].setdefault(name, {})[tag] = [sum(passes(e, s["logits"][name][e["id"]]) for e in exs) for s in a["seeds"]]
            out["beyond_operators"].setdefault(name, {})[tag] = sum(1 for k in menu if trm[k] and not menu[k])
            bins = defaultdict(lambda: [0, 0])
            for e in exs:
                b = "0-3" if dist[e["puzzle_id"]] <= 3 else ("4-6" if dist[e["puzzle_id"]] <= 6 else ("7-9" if dist[e["puzzle_id"]] <= 9 else "10+"))
                bins[b][0] += trm[e["puzzle_id"]]
                bins[b][1] += 1
            out["by_distance"].setdefault(name, {})[tag] = {b: f"{k}/{n}" for b, (k, n) in sorted(bins.items())}
            if name in ("TQ", "T8"):
                pts = {}
                for frac, recs in sorted(a["curves"].items()):
                    vals = [sum(passes(e, r["logits"][name][e["id"]]) for e in exs) / len(exs) for r in recs]
                    pts[str(frac)] = {"mean": statistics.mean(vals), "sd": statistics.pstdev(vals), "n_seeds": len(vals),
                                      "train_rows": statistics.mean(r["train_rows"] for r in recs)}
                out["curves"].setdefault(name, {})[tag] = pts
        out["policies"][name] = {k: {"solved": sum(v.values()), "n": len(v)} for k, v in pol.items()}
        per_item[name] = pol
    if "atoms" in arms and "raw" in arms:
        TQ, T8 = per_item["TQ"], per_item["T8"]
        t = {"P1": report.paired(TQ["TRM[atoms]"], TQ["TRM[raw]"], "two"),
             "P2": report.paired(T8["TRM[atoms]"], T8["TRM[raw]"], "two"),
             "P3": report.paired(TQ["menu+TRM[atoms]"], TQ["menu"], "one"),
             "P4": report.paired(TQ["menu+TRM[atoms]"], TQ["menu+TRM[raw]"], "two")}
        adj = report.holm({k: v["p"] for k, v in t.items()})
        for k in t:
            t[k]["p_holm"] = adj[k]
        out["tests"] = t
        # R-A2 family: low-data comparisons, 3-seed per-cell majority, own Holm correction
        exs = rt.examples("TQ")
        low = {}
        for pid, frac in (("P5", 0.25), ("P6", 0.5)):
            ra, rr = arms["atoms"]["curves"].get(frac, []), arms["raw"]["curves"].get(frac, [])
            if len(ra) == 3 and len(rr) == 3:
                sa = {e["puzzle_id"]: passes(e, ensemble(ra, "TQ", e["id"])) for e in exs}
                sr = {e["puzzle_id"]: passes(e, ensemble(rr, "TQ", e["id"])) for e in exs}
                low[pid] = report.paired(sa, sr, "two")
        if low:
            adj = report.holm({k: v["p"] for k, v in low.items()})
            for k in low:
                low[k]["p_holm"] = adj[k]
        out["tests_low_data"] = low
    # R-A3 confirmation: seeds 5-9, single models, exact one-sided permutation test, fresh TQ2 / T82
    import itertools
    conf = {}
    if "atoms" in arms and "raw" in arms and len(arms["atoms"]["confirm"]) == 5 and len(arms["raw"]["confirm"]) == 5:
        for cid, name in (("C1", "TQ2"), ("C2", "T82")):
            exs = rt.examples(name)
            sa = [sum(passes(e, r["logits"][name][e["id"]]) for e in exs) for r in arms["atoms"]["confirm"]]
            sr = [sum(passes(e, r["logits"][name][e["id"]]) for e in exs) for r in arms["raw"]["confirm"]]
            pooled, obs = sa + sr, statistics.mean(sa) - statistics.mean(sr)
            diffs = []
            for idx in itertools.combinations(range(10), 5):
                g = [pooled[i] for i in idx]
                h = [pooled[i] for i in range(10) if i not in idx]
                diffs.append(statistics.mean(g) - statistics.mean(h))
            pval = sum(d >= obs - 1e-12 for d in diffs) / len(diffs)
            ens = {}
            for tag in ("atoms", "raw"):
                ens[tag] = sum(passes(e, ensemble(arms[tag]["confirm"], name, e["id"])) for e in exs)
            menu = sum(report.verify_policy(cur[e["id"]])["success"] for e in exs) if all(e["id"] in cur for e in exs) else None
            conf[cid] = {"set": name, "n_items": len(exs), "atoms_models": sa, "raw_models": sr, "mean_difference": obs, "p": pval,
                         "ensemble_solved": ens, "menu_solved": menu}
        adj = report.holm({k: v["p"] for k, v in conf.items()})
        for k in conf:
            conf[k]["p_holm"] = adj[k]
        for name in ("TQ", "T8", "T27"):
            exs = rt.examples(name)
            conf.setdefault("old_sets", {})[name] = {tag: [sum(passes(e, r["logits"][name][e["id"]]) for e in exs) for r in arms[tag]["confirm"]]
                                                       for tag in ("atoms", "raw")}
    out["confirmation"] = conf
    write_json(RESULTS / "repair_report.json", out)
    lines = ["# SPEC-R repair TRM report", "", "## Selected settings", "```", json.dumps(out["selected"], indent=1), "```", ""]
    for name, pols in out["policies"].items():
        lines.append(f"## {name}: solved of {next(iter(pols.values()))['n']}")
        lines += [f"- {k}: {v['solved']}" for k, v in pols.items()]
        lines.append("")
    lines += ["## Registered tests", "```", json.dumps(out["tests"], indent=1), "```", "",
              "## Low-data tests (R-A2)", "```", json.dumps(out.get("tests_low_data", {}), indent=1), "```", "",
              "## Confirmation (R-A3)", "```", json.dumps(out.get("confirmation", {}), indent=1), "```", "",
              "## Seed spread (standalone solved per seed)", "```", json.dumps(out["seed_spread"], indent=1), "```", "",
              "## Learning curves", "```", json.dumps(out["curves"], indent=1), "```", "",
              "## Solved by distance to nearest solution", "```", json.dumps(out["by_distance"], indent=1), "```", "",
              "## Solved that no operator could fix", "```", json.dumps(out["beyond_operators"], indent=1), "```"]
    (RESULTS / "repair_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:60]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
