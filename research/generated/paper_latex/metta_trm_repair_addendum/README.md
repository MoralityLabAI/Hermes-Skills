# MeTTa/TRM Repair Addendum LaTeX Package

Generated: 2026-04-26

## Contents

- `main.tex`: provisional paper addendum.
- `references.bib`: bibliography including HRM, TRM, MeTTa, Hermes 3, and Prime Intellect references.
- `data_campaign_plan.md`: experiment plan for 9B/27B and trained TRM runs.
- `figures/`: generated PDF/PNG figures.
- `tables/`: generated CSV tables behind the figures and manuscript tables.

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

