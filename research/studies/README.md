# Hermes Studies

This folder turns the generated TRM queue into concrete study packets.

Each study folder should contain:

- `README.md`
  - one-page overview of the pairing, benchmark slice, and expected outputs
- `skill_research_brief.md`
  - the formal hypothesis, promotion rule, and failure gates
- `experiment_log.md`
  - the current run record, even when the study is still only staged

## Shared Baseline Spine

Use these generated files as the repo-wide TRM benchmark baseline before making per-study claims:

- [trm_infused_baseline_summary_table.md](C:/projects/Hermes Skills/research/generated/trm_infused_baseline_summary_table.md)
- [trm_infused_baseline_crossref.md](C:/projects/Hermes Skills/research/generated/trm_infused_baseline_crossref.md)
- [trm_infused_baseline_crossref.json](C:/projects/Hermes Skills/research/generated/trm_infused_baseline_crossref.json)
- [metta_third_column_crossref.md](C:/projects/Hermes Skills/research/generated/metta_third_column_crossref.md)
- [metta_third_column_crossref.json](C:/projects/Hermes Skills/research/generated/metta_third_column_crossref.json)

## Naming Rule

Use `YYYY-MM-DD-short-study-name` so the folder path itself preserves chronology.

## Active Studies

| Study | Status | Focus | Folder |
| --- | --- | --- | --- |
| Intellect3 logic public trace | staged | Test whether bounded public rationale improves Campsite accuracy without breaking the final grid contract. | [2026-04-22-intellect3-logic-public-trace](C:/projects/Hermes Skills/research/studies/2026-04-22-intellect3-logic-public-trace/README.md) |
| Intellect3 math public trace | staged | Test whether bounded public rationale helps arithmetic reasoning on rationale-allowed evals without hurting final integer formatting. | [2026-04-22-intellect3-math-public-trace](C:/projects/Hermes Skills/research/studies/2026-04-22-intellect3-math-public-trace/README.md) |
| MeTTa TRM Hermes pipeline | promoted (narrow) | The MeTTa package contract compiles, drives live eval arms, emits a compact runtime packet, offline TRM rows, deterministic repair probes, multi-signal scorecards, and now actual trainer-policy bundles that the local TRM harness can train and bench. The study now also has a concrete broader-slice curation: `psycho_bench + if_summarize_judge` as core, `allenai_ifeval` as support, and `clbench` as the blocked high-value follow-on. The first profile-aware nuanced-env lane is built too: `if_summarize_judge` now has a real Hermes skill, a `17`-profile MeTTa bundle, `72` synthesized rows, `446` trainer-policy targets, a replay-grounded repair receipt, a corrected seeded live benchmark, and a local trainer rollup with `0.8605` critic bucket accuracy. The latest corrected Primehub comparisons now show a full progression: trainer-policy bundles help the merged synthetic corpus but not original holdout transfer, transfer-oriented overlay rows stay flat on the untouched external holdout, the train-only external abstraction bundle lifts retrieval but not gated routing, the follow-up critic-support bundle converts that into a real untouched-holdout gated-router win (`0.0000 -> 0.1562`, focus slice `0.0000 -> 0.6250`), the `allenai_ifeval` next-family lane delivers a full untouched contract-holdout win (`0.0000 -> 1.0000`), and the `aime2026` lane delivers a full untouched boxed-exact numeric win (`0.0000 -> 1.0000`). The fresh family-router pass shows the critic drop is not unrelated-family poisoning on the current holdout: unrelated critic and gated metrics stay flat while target-family contracts improve, so the next issue is target-adjusted labels rather than more router complexity. | [2026-04-22-metta-trm-hermes-pipeline](C:/projects/Hermes Skills/research/studies/2026-04-22-metta-trm-hermes-pipeline/README.md) |
| Primehub structured-map retrieval ablation | promoted (scoped) | TRM-MCP retrieval is promoted for exact-structure-sensitive Primehub lanes. The live scorer bug in `pydantic_adherence` is fixed, and retrieval shows live uplifts on `ascii_tree` and `pydantic_adherence` while staying near baseline on `psycho_bench`. | [2026-04-22-primehub-structured-map-retrieval](C:/projects/Hermes Skills/research/studies/2026-04-22-primehub-structured-map-retrieval/README.md) |
| Primehub observability pack | staged | Build the common rollup and cluster matrix needed before extra overlays are promoted across Primehub skills. | [2026-04-22-primehub-observability-pack](C:/projects/Hermes Skills/research/studies/2026-04-22-primehub-observability-pack/README.md) |

## Operating Rule

Start with a staged packet, run the smallest defensible benchmark slice, and only then widen the study or stack more TRM layers.
