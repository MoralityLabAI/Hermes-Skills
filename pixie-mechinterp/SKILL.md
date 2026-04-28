---
name: pixie-mechinterp
description: "Use for Pixie / fae mechinterp and tiny-LoRA ablation work, including overnight sweep status, constitution runs, and trigger-vs-drift reporting."
---

# Pixie Mechinterp

Use this skill for Pixie / fae mechinterp work. Keep the loop receipts-first and prefer the existing study roots over fresh long reruns.

## Local references

- `references/paths.md`

## Workflow

1. Read `references/paths.md` to locate the harness, source data, study roots, and useful outputs.
2. Inspect the latest existing study root or matrix receipt before launching anything new.
3. Use the narrowest script that matches the request:
   - `run_fae_ablation_matrix.py` for trigger-vs-drift matrix comparisons
   - `run_fae_overnight_sweep.py` for overnight parameter sweeps
   - `run_fae_constitution_matrix.py` for constitution-conditioned studies
   - `auto_research_tinylora_loop.py` only when explicitly continuing the autoresearch loop
4. Summarize results with concrete artifact paths, top trigger-vs-drift deltas, and any obvious regressions.
5. If receipts are incomplete, stale, or missing, state that before recommending a rerun.

## Rules

- Prefer current study roots and packaged outputs over fresh long runs.
- Do not invent paths; use the packaged path list in `references/paths.md`.
- Keep reports grounded in concrete outputs such as matrix indexes and bench receipts.
- If a required path is missing locally, stop and report the missing dependency.
