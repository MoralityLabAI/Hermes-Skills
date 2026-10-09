"""POST HOC (addendum A2): is the pre-repair gate limited by the TRM or by the information in the state?
Fits standard classifiers on the same train rows and scores them on T8 with the same outcome function."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
import gates, report
from common import RESULTS, write_json

data = gates.load()
out = {}
for src, tests in (("real", ("T8", "T8s")), ("realq", ("TQ", "TQs"))):
  for feats in ("typed", "raw", "typed+raw"):
    Xtr = np.array([gates.vec(r, feats) for r in data[f"train:{src}"]]); ytr = [r["best_action"] for r in data[f"train:{src}"]]
    for name, clf in (("logistic", LogisticRegression(max_iter=4000, C=1.0)),
                      ("gradient-boosting", HistGradientBoostingClassifier(random_state=0))):
        clf.fit(Xtr, ytr)
        for tname in tests:
            rows = data[f"test:{tname}"]
            X = np.array([gates.vec(r, feats) for r in rows])
            acts = clf.predict(X)
            s = report.summarize([report.outcome(r, a) for r, a in zip(rows, acts)])
            # binary repairability AUC: P(not reject)
            classes = list(clf.classes_)
            p_rep = 1 - clf.predict_proba(X)[:, classes.index("reject")]
            y = [int(r["best_action"] != "reject") for r in rows]
            out[f"{src}|{tname}|{feats}|{name}"] = {"success": s["success"], "unsafe": s["unsafe"], "rejected": s["rejected"],
                                               "auc_repairable": round(roc_auc_score(y, p_rep), 3),
                                               "label_accuracy": round(float(np.mean([a == r["best_action"] for a, r in zip(acts, rows)])), 3)}
# TRM label accuracy and AUC-free comparison
preds = [p for p in __import__("common").read_jsonl(RESULTS / "gates" / "predictions.jsonl") if p["n"] == "all" and p["source"] == "real"]
for feats in ("typed", "raw", "typed+raw"):
    recs = [p for p in preds if p["features"] == feats]
    for tname in ("T8", "T8s"):
        rows = data[f"test:{tname}"]
        accs = [np.mean([rec["predictions"][f"test:{tname}"][r["row_id"]] == r["best_action"] for r in rows]) for rec in recs]
        out[f"{tname}|{feats}|TRM(seeds)"] = {"label_accuracy_mean": round(float(np.mean(accs)), 3)}
base = {t: round(float(np.mean([r["best_action"] == "reject" for r in data[f"test:{t}"]])), 3) for t in ("T8", "T8s")}
out["majority_reject_rate"] = base
write_json(RESULTS / "posthoc_ceiling.json", out)
for k, v in out.items(): print(k, v)
