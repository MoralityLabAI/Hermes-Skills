# Revision notes: April 29 version to October 2026 version

Scope set by the author on 2026-10-08: keep the original title, keep the paper to its own Hermes Skills
material (no BitAgent section, no May LoRA material), fix the methodology, and actually run the MeTTa-curated
training and the benches on this PC's CPU and RAM. The April source is untouched in `../metta_trm_repair_addendum/`.

The new experiments are registered and implemented in
`research/studies/2026-10-08-metta-curated-campsite-curriculum/` (SPEC.md, src/, results/). Every result
table in the paper is generated from `results/report.json` by `src/paper_tables.py` into `generated/`.

## Methodology problems in the April version

1. **"TRM" meant two things.** The April 16-22 baseline's "TRM" is a task-representation memory (a bank of
   replayed rows); the abstract and motivation mean tiny recursive models. Now defined in Section 2.
2. **The title's training run never happened.** No TRM was trained on the curriculum. Now done (Section 6).
3. **The curriculum could not support training.** The Campsite rows carry no candidate content
   (`candidate_excerpt` = `arm=logic_skill_trm transform=original`), and two state fields (reward, exact vs
   wrong-cell label) are computed against the answer key. A content-bearing curriculum was built.
4. **The rudder benchmark's retrieval arm leaked the label** (query tokens include its own bucket, action and
   target; bucket bonus). Rerun with pre-repair fields only.
5. **The unseen-family split was unreachable** (gold actions absent from the allowed list). Rerun with the
   full action vocabulary.
6. **The "static-gate rudder" model share is an always-commit policy**, and the May "saturation" rules read
   the label. Stated.
7. **"Pure TRM" and "MeTTa runtime" arms differ only in system-prompt wording**, with the same contract text.
   Renamed, and a contract-with-baseline-prompt arm added in the rerun.
8. **No-model target definitions were presented as results** (C-signature sweep, nine-family matrix, closure
   suite). Moved to one section, labelled as target definitions reading answer-derived state.
9. **Statistics.** Four-decimal accuracies on 88 rows (44 problems), no intervals, no paired tests, one seed.
   Now counts, Wilson intervals, exact McNemar on discordant pairs, Holm across registered tests, five seeds
   for every trained gate with per-item majority votes for the registered tests.
10. **The 33/109 flow-policy baseline** came from an arm that routes on exact constraint signatures matched
    against a support set; overlap with the evaluated puzzles was never audited. Reported as historical.
11. **Positioning.** Added the prior art for "the model proposes, a verifier decides" (LLM-Modulo,
    AlphaGeometry, verifiers and PRMs, self-repair and self-correction results).
12. **Prose.** Lab-notebook date narration, "paper-facing claim" phrasing, undefined internal names, and the
    garbled matplotlib tick labels are gone; figures are redrawn in TikZ/pgfplots from the data.

## What the author still owns

- The April model was downloaded with your go-ahead: `qwen2.5-3b-instruct-q4_k_m.gguf`, Qwen/Qwen2.5-3B-Instruct-GGUF
  revision 7dabda4d, SHA-256 626b4a66...c62d, stored under `Documents\Codex\models\Qwen2.5-3B-Instruct-GGUF\`.
- The D: drive artifacts are not needed: they belonged to the May LoRA draft, which this paper no longer includes.
- Nothing is committed in Hermes-Skills; that checkout's index still shows the pre-existing staged deletions.

## Replication with the April model (Qwen2.5-3B, April runners executed unchanged from git, CPU)

| Bench | April | Rerun | Same answers as April |
|---|---|---|---|
| Rudder raw | 32/88 | 32/88 | 84/88 |
| Rudder action-space | 66 | 66 | 88/88 |
| Rudder static gate (April rules) | 84 | 84 | 88/88 |
| Rudder action-space + retrieval | 61 | 60 | 85/88 |
| Rudder leaky retrieval | 28 | 17 | 73/88 (15 rows flip dual_repair to c_repair; commits identical) |
| Contracts held-out: baseline / skill / gate / feedback repair | 23 / 27 / 32 / 37 | 24 / 28 / 34 / 39 | verdict 48-50 of 50 |
| Contracts hard: baseline / skill / gate / blind / feedback | 12 / 11 / 9 / 12 / 13 | 9 / 11 / 8 / 13 / 13 | verdict 27-30 of 30 |
| Constraint extraction: plain / schema / gate-named / scripts | 0 / 6 / 9 / 12 | 0 / 6 / 8 / 12 | |

## What the new runs found (all CPU, 2026-10-08)

| Result, 148 greedy test answers each | Qwen2.5-3B | Bonsai-8B |
|---|---|---|
| Fixable by the skill's operators (none pass as written) | 63 | 69 |
| Repair, then verify: solved / unsafe | 63 / 0 | 69 / 0 |
| Published dual_repair flow: solved / unsafe | 62 / 86 | 69 / 79 |
| TRM gate, typed, own failures | 48 / 24 | 45 / 20 |
| TRM gate, raw cells, own failures | 37 / 32 | 45 / 22 |
| TRM gate, typed, synthetic defects | 21 / 66 | 37 / 58 |
| Post-hoc classifiers (logistic, boosted trees) | 34-47 / 19-32 | 35-52 / 16-26 |

Other results: on Bonsai-27B's answers repair-then-verify solves 66 with 0 unsafe; the Qwen gate solves 54 with 39
unsafe and the Bonsai-8B gate 38 with 32. Rudder, Qwen 3B: clean retrieval 17 against raw 32, leaky 17, all actions
listed 1 (template echo on 60 rows). Contracts, Qwen 3B held-out: baseline 24, contract only 35, gate wording 34,
blind repair 36, feedback repair 39.

Registered tests:
- Qwen family: G1q supported (29 vs 2, Holm p < 0.001), G2q supported (14 vs 3, p = 0.013), G3q and G4q supported
  (p < 0.001), R1q significant in the opposite direction to the April claim (clean retrieval hurts: 0 vs 15,
  p < 0.001), R2q not supported, M1q supported (12 vs 1, p = 0.010), M2q and M3q not supported.
- Bonsai family: G1 and G2 not supported, G3 and G4 supported, R1 and R2 not supported, M1 to M3 not supported.

## Repair TRM trained on a MeTTa-framed corpus (Section 7, CPU, 2026-10-09)

Registered in `SPEC-repair-trm.md` (study directory) before any repair model was built; addenda R-A1 (cheaper
selection procedure, 682 extra training puzzles), R-A2 (low-data tests P5/P6, registered after validation runs and
before any test prediction was read) and R-A3 (fresh-pool confirmation C1/C2, registered after the first test results).
Results in `results/repair_report.json`, computed by `src/repair_report.py`.

A ~69k-parameter TRM-style recursive network writes the repair (tent or no tent per cell) from a puzzle and a broken
answer; trained on 4,528 real broken answers from Qwen2.5-3B and Bonsai-8B. The raw arm sees 8 per-cell channels; the
atoms arm adds the 8 cell atoms declared in `metta/campsite_repair_cells.metta` (deterministic functions of the raw
channels). Five seeds per arm; registered tests use the per-cell majority.

| Solved of 148 greedy test answers | Qwen2.5-3B | Bonsai-8B | Bonsai-27B |
|---|---|---|---|
| Skill operators, then verify | 63 | 69 | 66 |
| Repair TRM, raw corpus | 73 | 71 | 73 |
| Repair TRM, MeTTa-atoms corpus | 78 | 81 | 77 |
| Operators, then raw TRM, then verify | 90 | 86 | 86 |
| Operators, then atoms TRM, then verify | 93 | 94 | 93 |
| Single models (seeds 0-4), raw / atoms | 60-67 / 68-84 | 60-67 / 72-85 | 62-67 / 69-83 |

Registered tests (exact McNemar on discordant pairs, Holm):
- P1 atoms vs raw ensemble, Qwen answers: 20 vs 15, Holm p = 1.00, not supported.
- P2 same, Bonsai-8B answers: 18 vs 8, Holm p = 0.23, not supported.
- P3 operators+atoms TRM vs operators alone: 30 vs 0, Holm p < 0.001, supported (no broken commit).
- P4 operators+atoms TRM vs operators+raw TRM: 11 vs 8, Holm p = 1.00, not supported.
- P5 quarter of the training puzzles: atoms 57 vs raw 26, 37 vs 6, Holm p < 0.001, supported.
- P6 half of the training puzzles: atoms 62 vs raw 39, 32 vs 9, Holm p < 0.001, supported.
- C1 fresh pool (141 puzzles, seeds 5-9), single models, Qwen answers: atoms 55-78 vs raw 50-58, mean +9.2,
  exact permutation Holm p = 0.024, supported. Fresh ensembles 68 vs 60; operators 62.
- C2 same, Bonsai-8B answers: atoms 59-79 vs raw 54-60, mean +10.0, Holm p = 0.024, supported. Ensembles 71 vs 61;
  operators 68.

Descriptive: seed-mean learning curves on Qwen answers, atoms 38/41/50% vs raw 14/25/43% at a quarter/half/all of
the corpus; at the lower learning rate raw reaches 9.5% on validation and atoms 27.6%. Seeds 5-9 on the original test
sets overlap (Qwen answers atoms 68-87 vs raw 56-70), atoms ahead by 9 to 13 on average across proposers. The
registered symmetry-augmentation arms (raw+sym, atoms+sym) started 2026-10-09 07:51 and are not in this revision.

Reading: the MeTTa framing of the corpus gives a real benchmark benefit for a repair TRM (data efficiency, learning-rate
robustness, single-model accuracy), which shrinks as the raw network gets enough data; a framed repair TRM behind the
verifier adds 30 solved answers to the skill.
