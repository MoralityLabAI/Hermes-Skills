"""Write LaTeX fragments for the paper from results/report.json (numbers are never copied by hand).

usage: python paper_tables.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import HERMES_SKILLS, RESULTS  # noqa: E402

OUT = HERMES_SKILLS / "research" / "generated" / "paper_latex" / "metta_trm_repair_v2" / "generated"


def pct(k, n):
    return f"{100 * k / n:.0f}" if n else "--"


def pval(p):
    """The whole comparison, e.g. "$p = 0.34$" or "$p < 0.001$"."""
    if p < 0.001:
        return "$p < 0.001$"
    return f"$p = {p:.3f}$" if p < 0.1 else f"$p = {p:.2f}$"


def tex_escape(s: str) -> str:
    return s.replace("_", r"\_").replace("&", r"\&")


def policies_table(G: dict) -> str:
    sets = [t for t in ("TQ", "T8", "T27") if t in G["policies"]]
    order = [("as-written", "Commit as written"), ("flow-c", "Published \\texttt{c\\_repair} flow"),
             ("flow-dual", "Published \\texttt{dual\\_repair} flow"), ("static", "Static rule on typed atoms"),
             ("TRM[typed,synthetic]", "TRM, typed, synthetic curriculum"), ("TRM[raw,real]", "TRM, raw cells, Bonsai-8B curriculum"),
             ("TRM[typed+raw,real]", "TRM, typed and raw, Bonsai-8B curriculum"), ("TRM[typed,real]", "TRM, typed, Bonsai-8B curriculum"),
             ("TRM[raw,realq]", "TRM, raw cells, Qwen curriculum"), ("TRM[typed,realq]", "TRM, typed, Qwen curriculum"),
             ("verify", "Repair, then verify"), ("TRM[typed,real]+verify", "TRM typed Bonsai-8B, then verify"),
             ("TRM[typed,realq]+verify", "TRM typed Qwen, then verify"),
             ("menu-ceiling", "Menu ceiling (label)"), ("CSP", "CSP solver")]
    cols = "l" + "rrrr" * len(sets)
    names = {"TQ": "Qwen2.5-3B answers", "T8": "Bonsai-8B answers", "T27": "Bonsai-27B answers"}
    head = " & ".join(f"\\multicolumn{{4}}{{c}}{{{names[t]}, of {G['policies'][t]['as-written']['n']}}}" for t in sets)
    cmid = " ".join(f"\\cmidrule(lr){{{2 + 4 * i}-{5 + 4 * i}}}" for i in range(len(sets)))
    sub = " & ".join(["Solved & Unsafe & Rejected & Calls"] * len(sets))
    lines = [f"\\begin{{tabular}}{{{cols}}}", "\\toprule", f" & {head} \\\\", cmid, f"Policy & {sub} \\\\", "\\midrule"]
    for key, label in order:
        cells = []
        for t in sets:
            s = G["policies"][t].get(key)
            if not s:
                cells += ["--"] * 4
                continue
            calls = s["ops_per_item"] + s["verifier_per_item"]
            cells += [str(s["success"]), str(s["unsafe"]), str(s["rejected"]), f"{calls:.1f}"]
        lines.append(f"{label} & " + " & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def curves_figure(G: dict, test: str, metric: str, ylabel: str, legend: bool, reference: float | None, real: str = "real", real_label: str = "Bonsai-8B") -> str:
    curves = G["curves"].get(test, {})
    styles = {f"typed|{real}": ("blue!70!black, mark=*", f"typed atoms, {real_label} failures"),
              f"raw|{real}": ("orange!80!black, mark=square*", f"raw cells, {real_label} failures"),
              "typed|synthetic": ("red!70!black, dashed, mark=o", "typed atoms, synthetic")}
    plots = []
    for cfg, (style, label) in styles.items():
        pts = curves.get(cfg)
        if not pts:
            continue
        coords = sorted((v["n_rows"], 100 * v[metric]) for v in pts.values())
        plots.append(r"\addplot[" + style + r", thick] coordinates {" + " ".join(f"({x:.0f},{y:.1f})" for x, y in coords) + "};")
        if legend:
            plots.append(r"\addlegendentry{" + label + "}")
    if reference is not None:
        plots.append(r"\addplot[black, densely dotted, thick, domain=20:2600, samples=2] {" + f"{reference:.1f}" + "};")
        if legend:
            plots.append(r"\addlegendentry{repair, then verify}")
    legend_opt = r"legend style={font=\scriptsize, at={(0.02,0.98)}, anchor=north west}, legend cell align=left," if legend else ""
    return "\n".join([
        r"\begin{tikzpicture}",
        r"\begin{axis}[width=0.47\linewidth, height=5.0cm, xmode=log, log basis x=2, xlabel={training rows}, ylabel={" + ylabel + "},",
        r"  ymin=0, ymax=100, ymajorgrids, grid style={gray!25}, " + legend_opt,
        r"  tick label style={font=\small}, label style={font=\small}]",
        *plots, r"\end{axis}", r"\end{tikzpicture}"])


def rudder_qwen_table(Q: dict) -> str:
    order = [("raw_3b_rudder", "Raw, six train actions"), ("raw-fullvocab", "Raw, all twelve actions"),
             ("repair_training_rudder", "Retrieval, published (leaks the label)"), ("retrieval-clean", "Retrieval, pre-repair fields only"),
             ("metta_action_space_rudder", "Action-space"), ("metta_action_space_training_rudder", "Action-space with retrieval"),
             ("metta_static_gate_rudder", "Static gate (April rules)"), ("metta_validator_gate", "Post-repair oracle (no model)")]
    lines = ["\\begin{tabular}{lrrrrr}", "\\toprule",
             "Arm & Joint, April & Joint, rerun & Same answers as April & False commits & Unseen-family joint \\\\",
             "& of 88 & of 88 & rows & of 22 & of 18 \\\\", "\\midrule"]
    for key, label in order:
        s = Q["R"]["table"].get(key)
        if not s:
            continue
        april = str(s["published_joint"]) if s["published_joint"] is not None else "--"
        agree = f"{s['agreement'][0]}/{s['agreement'][1]}" if s["agreement"] else "new arm"
        lines.append(f"{label} & {april} & {s['joint']} & {agree} & {s['false_commit']} & {s['unseen_joint']} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def mixed_qwen_table(M: dict, Q: dict) -> str:
    order = [("baseline", "baseline", "Baseline"), ("contract-neutral", "contract-neutral", "Contract, baseline system prompt"),
             ("pure_trm", "skill-wording", "Contract, skill wording (April: pure TRM)"),
             ("metta_runtime", "gate-wording", "Contract, gate wording (April: MeTTa runtime)"),
             ("metta_runtime_blind_repair", "repair-blind", "Gate wording, then blind repair"),
             ("metta_runtime_repair", "repair-feedback", "Gate wording, then validator-feedback repair")]
    lines = ["\\begin{tabular}{lrrrrrr}", "\\toprule",
             " & \\multicolumn{3}{c}{Held-out, of 50} & \\multicolumn{3}{c}{Hard, of 30} \\\\",
             "\\cmidrule(lr){2-4} \\cmidrule(lr){5-7}",
             "Arm & 3B, April & 3B, rerun & Bonsai-8B & 3B, April & 3B, rerun & Bonsai-8B \\\\", "\\midrule"]
    for qkey, bkey, label in order:
        cells = []
        for suite in ("heldout50", "hard30"):
            qs = Q["M"].get(suite, {}).get(qkey)
            april = qs["published_exact"] if qs and qs.get("published_exact") is not None else None
            ours = M.get("table", {}).get(suite, {}).get(bkey)
            cells += [str(april) if april is not None else "--", str(qs["exact"]) if qs else "--", str(ours["exact"]) if ours else "--"]
        lines.append(f"{label} & " + " & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def cross_table(G: dict) -> str:
    cross = G.get("cross", {})
    sets = [t for t in ("TQ", "T8", "T27") if t in cross]
    names = {"TQ": "Qwen2.5-3B", "T8": "Bonsai-8B", "T27": "Bonsai-27B"}
    lines = ["\\begin{tabular}{l" + "rr" * len(sets) + "}", "\\toprule",
             "Typed gate trained on & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{names[t]} answers}}" for t in sets) + " \\\\",
             " ".join(f"\\cmidrule(lr){{{2 + 2 * i}-{3 + 2 * i}}}" for i in range(len(sets))),
             " & " + " & ".join(["Solved & Unsafe"] * len(sets)) + " \\\\", "\\midrule"]
    for s, label in (("realq", "Qwen2.5-3B failures"), ("real", "Bonsai-8B failures"), ("synthetic", "Synthetic defects")):
        cells = []
        for tname in sets:
            c = cross[tname].get(s)
            cells += [str(c["success"]), str(c["unsafe"])] if c else ["--", "--"]
        lines.append(f"{label} & " + " & ".join(cells) + " \\\\")
    ver = [G["policies"][tname]["verify"] for tname in sets]
    lines.append("Repair, then verify & " + " & ".join(f"{v['success']} & {v['unsafe']}" for v in ver) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def repair_table(RR: dict) -> str:
    sets = [s for s in ("TQ", "T8", "T27") if s in RR["policies"]]
    names = {"TQ": "Qwen2.5-3B", "T8": "Bonsai-8B", "T27": "Bonsai-27B"}
    rows = [("menu", "Skill operators, then verify"), ("TRM[raw]", "Repair TRM, raw corpus"),
            ("TRM[atoms]", "Repair TRM, MeTTa-atoms corpus"), ("menu+TRM[raw]", "Operators, then raw TRM, then verify"),
            ("menu+TRM[atoms]", "Operators, then atoms TRM, then verify"), ("CSP", "CSP solver")]
    lines = ["\\begin{tabular}{l" + "r" * len(sets) + "}", "\\toprule",
             "Policy & " + " & ".join(names[s] for s in sets) + " \\\\", "\\midrule"]
    for key, label in rows:
        lines.append(label + " & " + " & ".join(str(RR["policies"][s][key]["solved"]) for s in sets) + " \\\\")
    lines.append("\\midrule")
    for tag, label in (("raw", "Single raw TRMs (5 seeds), range"), ("atoms", "Single atoms TRMs (5 seeds), range")):
        cells = []
        for s in sets:
            v = RR["seed_spread"][s][tag]
            cells.append(f"{min(v)}--{max(v)}")
        lines.append(label + " & " + " & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def repair_curves(RR: dict, test: str, ylabel: str, legend: bool) -> str:
    c = RR["curves"][test]
    styles = {"atoms": ("blue!70!black, mark=*", "MeTTa-atoms corpus"), "raw": ("orange!80!black, mark=square*", "raw corpus")}
    plots = []
    for tag, (style, label) in styles.items():
        pts = sorted((v["train_rows"], 100 * v["mean"]) for v in c[tag].values())
        plots.append(r"\addplot[" + style + r", thick] coordinates {" + " ".join(f"({x:.0f},{y:.1f})" for x, y in pts) + "};")
        if legend:
            plots.append(r"\addlegendentry{" + label + "}")
    menu = RR["policies"][test]["menu"]
    plots.append(r"\addplot[black, densely dotted, thick, domain=900:5000, samples=2] {" + f"{100 * menu['solved'] / menu['n']:.1f}" + "};")
    if legend:
        plots.append(r"\addlegendentry{skill operators}")
    legend_opt = r"legend style={font=\scriptsize, at={(0.02,0.98)}, anchor=north west}, legend cell align=left," if legend else ""
    return "\n".join([r"\begin{tikzpicture}",
                      r"\begin{axis}[width=0.47\linewidth, height=5.0cm, xmode=log, log basis x=2, xlabel={training rows}, ylabel={" + ylabel + "},",
                      r"  ymin=0, ymax=80, ymajorgrids, grid style={gray!25}, " + legend_opt,
                      r"  tick label style={font=\small}, label style={font=\small}]", *plots, r"\end{axis}", r"\end{tikzpicture}"])


def repair_macros(RR: dict) -> list[str]:
    out = []
    words = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six"}
    tests = {**RR.get("tests", {}), **RR.get("tests_low_data", {})}
    for i in "123456":
        t_ = tests.get(f"P{i}")
        text = (f"{t_['a_only']} against {t_['b_only']} discordant, Holm {pval(t_['p_holm'])}" if t_ else "\\pending{P" + i + "}")
        out.append("\\newcommand{\\testP" + words[i] + "}{" + text + "}")
    conf = RR.get("confirmation", {})
    for i, cid in (("one", "C1"), ("two", "C2")):
        c = conf.get(cid)
        text = (f"atoms {min(c['atoms_models'])}--{max(c['atoms_models'])} against raw {min(c['raw_models'])}--{max(c['raw_models'])} "
                f"of {c['n_items']}, exact permutation Holm {pval(c['p_holm'])}" if c else "\\pending{" + cid + "}")
        out.append("\\newcommand{\\testC" + i + "}{" + text + "}")
    return out


def rudder_table(R: dict) -> str:
    order = [("Bonsai-8B raw", "Raw, six train actions"), ("Bonsai-8B raw-fullvocab", "Raw, all twelve actions"),
             ("Bonsai-8B retrieval-published", "Retrieval, published (leaks the label)"),
             ("Bonsai-8B retrieval-clean", "Retrieval, pre-repair fields only"), ("Bonsai-8B action-space", "Action-space"),
             ("lookup", "Lookup, train majority (no model)"), ("TRM (5-seed vote)", "Two-head TRM, 4.3M parameters (no LLM)")]
    lines = ["\\begin{tabular}{lrrrrrr}", "\\toprule",
             "Arm & Joint & Repair & Commit/reject & Commits & False commits & Unseen-family joint \\\\",
             "& of 88 & of 88 & of 88 & of 88 & of 22 & of 18 \\\\", "\\midrule"]
    for key, label in order:
        s = R["table"].get(key)
        if s:
            lines.append(f"{label} & {s['joint']} & {s['repair']} & {s['action']} & {s['commits']} & {s['false_commit']} & {s['unseen_joint']} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def mixed_table(M: dict) -> str:
    order = [("baseline", "Baseline"), ("contract-neutral", "Contract, baseline system prompt"),
             ("skill-wording", "Contract, skill wording (April: pure TRM)"), ("gate-wording", "Contract, gate wording (April: MeTTa runtime)"),
             ("repair-blind", "Gate wording, then blind repair"), ("repair-feedback", "Gate wording, then validator-feedback repair")]
    pub_key = {"baseline": "baseline", "skill-wording": "pure_trm", "gate-wording": "metta_runtime",
               "repair-blind": "metta_runtime_blind_repair", "repair-feedback": "metta_runtime_repair"}
    lines = ["\\begin{tabular}{lrrrr}", "\\toprule",
             " & \\multicolumn{2}{c}{Held-out, of 50} & \\multicolumn{2}{c}{Hard, of 30} \\\\",
             "\\cmidrule(lr){2-3} \\cmidrule(lr){4-5}", "Arm & Qwen2.5-3B & Bonsai-8B & Qwen2.5-3B & Bonsai-8B \\\\", "\\midrule"]
    for key, label in order:
        cells = []
        for suite in ("heldout50", "hard30"):
            pk = pub_key.get(key)
            pub = M.get("published_3b", {}).get(suite, {})
            published = str(pub.get(pk, 0)) if pk and (suite == "hard30" or pk != "metta_runtime_blind_repair") else "--"
            ours = M.get("table", {}).get(suite, {}).get(key)
            cells += [published, str(ours["exact"]) if ours else "--"]
        lines.append(f"{label} & " + " & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def curriculum_table(G: dict) -> str:
    cur = G["curriculum"]
    rows = []
    for name, label in (("real-Qwen2.5-3B", "Qwen2.5-3B"), ("real-Bonsai-8B", "Bonsai-8B"), ("real-Bonsai-27B", "Bonsai-27B"),
                        ("synthetic", "Synthetic")):
        c = cur.get(name)
        if not c:
            continue
        for pool in ("train", "val", "test"):
            best = {k.split("|")[1]: v for k, v in c["pool_best"].items() if k.startswith(pool + "|")}
            n = sum(best.values())
            if not n:
                continue
            rows.append(f"{label} & {pool} & {n} & {best.get('commit', 0)} & {best.get('c_repair', 0)} & "
                        f"{best.get('dual_repair', 0)} & {best.get('reject', 0)} \\\\")
    return "\n".join(["\\begin{tabular}{llrrrrr}", "\\toprule",
                      "Candidates & Pool & Rows & Commit & \\texttt{c\\_repair} & \\texttt{dual\\_repair} & Reject \\\\", "\\midrule",
                      *rows, "\\bottomrule", "\\end{tabular}"])


WORDS = {"1": "one", "2": "two", "3": "three", "4": "four"}


def macros(report: dict) -> str:
    """\\testGone etc. (LaTeX command names cannot contain digits). Every registered test gets a macro;
    a test not yet computed prints a red placeholder."""
    out = []
    registered = {"G": "1234", "R": "12", "M": "123"}
    qtests = {"G": report["G"].get("tests_q", {}), "R": report.get("Q", {}).get("R", {}).get("tests", {}),
              "M": report.get("Q", {}).get("M", {}).get("tests", {})}
    for part, ids in registered.items():
        for i in ids:
            t = qtests[part].get(f"{part}{i}q")
            name = "\\test" + part + WORDS[i] + "q"
            text = (f"{t['a_only']} against {t['b_only']} discordant, Holm {pval(t['p_holm'])}" if t
                    else "\\pending{" + f"{part}{i}q not yet computed" + "}")
            out.append("\\newcommand{" + name + "}{" + text + "}")
    for part, ids in registered.items():
        tests = report[part].get("tests", {})
        for i in ids:
            name = f"\\test{part}{WORDS[i]}"
            t = tests.get(f"{part}{i}")
            text = (f"{t['a_only']} against {t['b_only']} discordant, Holm {pval(t['p_holm'])}" if t
                    else f"\\pending{{{part}{i} not yet computed}}")
            out.append(f"\\newcommand{{{name}}}{{{text}}}")
    return "\n".join(out)


def main() -> int:
    report = json.loads((RESULTS / "report.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    G = report["G"]
    files = {"tab_policies.tex": policies_table(G), "tab_curriculum.tex": curriculum_table(G),
             "tab_rudder_rerun.tex": rudder_table(report["R"]), "tab_mixed.tex": mixed_table(report["M"]),
             "macros.tex": macros(report), "tab_cross.tex": cross_table(G)}
    if report.get("Q", {}).get("R", {}).get("table"):
        files["tab_rudder_qwen.tex"] = rudder_qwen_table(report["Q"])
    if report.get("Q", {}).get("M", {}).get("heldout50"):
        files["tab_mixed_qwen.tex"] = mixed_qwen_table(report["M"], report["Q"])
    if "T8" in G["curves"]:
        ver = G["policies"]["T8"]["verify"]
        files["fig_curves_success.tex"] = curves_figure(G, "T8", "success_mean", r"solved, \% of Bonsai-8B answers", True,
                                                        100 * ver["success"] / ver["n"])
        files["fig_curves_unsafe.tex"] = curves_figure(G, "T8", "unsafe_mean", r"unsafe commits, \% of T8", False,
                                                       100 * ver["unsafe"] / ver["n"])
    if "TQ" in G["curves"]:
        verq = G["policies"]["TQ"]["verify"]
        files["fig_curves_q_success.tex"] = curves_figure(G, "TQ", "success_mean", r"solved, \% of Qwen2.5-3B answers", True,
                                                          100 * verq["success"] / verq["n"], real="realq", real_label="Qwen2.5-3B")
    rr_path = RESULTS / "repair_report.json"
    if rr_path.exists():
        RR = json.loads(rr_path.read_text(encoding="utf-8"))
        if RR.get("policies") and "atoms" in RR.get("seed_spread", {}).get("TQ", {}):
            files["tab_repair.tex"] = repair_table(RR)
            files["fig_repair_curves_q.tex"] = repair_curves(RR, "TQ", r"solved, \% of Qwen2.5-3B answers", True)
            files["fig_repair_curves_8.tex"] = repair_curves(RR, "T8", r"solved, \% of Bonsai-8B answers", False)
            files["macros.tex"] = files["macros.tex"] + "\n" + "\n".join(repair_macros(RR))
    for name, text in files.items():
        (OUT / name).write_text(text + "\n", encoding="utf-8")
    print("wrote", sorted(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
