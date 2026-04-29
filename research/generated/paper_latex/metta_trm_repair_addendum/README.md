# MeTTa/TRM Repair Addendum LaTeX Package

Generated: 2026-04-29

## Contents

- `main.tex`: provisional paper addendum.
- `references.bib`: bibliography including HRM, TRM, MeTTa, Hermes 3, and Prime Intellect references.
- `data_campaign_plan.md`: experiment plan for 9B/27B and trained TRM runs.
- `figures/`: generated PDF/PNG figures.
- `tables/`: generated CSV tables behind the figures and manuscript tables.
- `tables/mixed_contract_*_summary.csv`: April 28 compactification positive/boundary tables.
- `figures/fig_task_graph_allocation_schema.*`: April 29 task-graph allocation diagram.
- `figures/fig_camp_gate_task_allocation.*`: noisy camp-gate task-allocation ladder.
- `tables/camp_gate_noisy_task_allocation.csv`: source counts for the noisy camp-gate figure.

## April 28 Compactification Addendum

The package now includes the mixed-contract heldout and hard-ablation local 3B evidence:

- `mixed_contract_heldout50`: baseline `23/50`, MeTTa runtime `32/50`, feedback repair `37/50`.
- `mixed_contract_hard_ablation30`: baseline `12/30`, MeTTa runtime `9/30`, blind repair `12/30`, feedback repair `13/30`.

Use this as an environment-dependent compactification section, not as trained TRM lift.

## April 29 Task-Graph Allocation Addendum

The package now includes the leakage-safe noisy camp-gate follow-up:

- Baseline extraction: `0/12` repaired solves.
- MeTTa schema extraction: `6/12` repaired solves.
- MeTTa graph extraction: `9/12` repaired solves.
- Script-owned graph router: `12/12` solves using prompt-visible constraints only.

Use this as evidence for control-plane task allocation: scripts own stable gates, TRMs target uncertain verifier-facing gates, symbolic solvers own closure, and the LLM remains a proposal or ambiguity-resolution component.

## Compile

No local TeX compiler was found on PATH during generation. Once TeX is installed:

```powershell
cd "C:\projects\Hermes-Skills\Hermes Skills\research\generated\paper_latex\metta_trm_repair_addendum"
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

or:

```powershell
latexmk -pdf main.tex
```

## Regenerate Figures

```powershell
python research\scripts\build_metta_trm_paper_figures.py
```

Run that command from `C:\projects\Hermes-Skills\Hermes Skills`.
