# SPEC-R: does MeTTa framing of the training corpus help a repair TRM?

Registered 2026-10-08 (late evening), before any repair TRM was built or trained. Addenda go at the end.
CPU only.

## 0. Question

The earlier gates only chose among the skill's repair operators. A repair TRM writes the repair: given a
broken Campsite answer, it outputs the tent layout. The question is whether framing its training corpus
with the MeTTa package (declared per-cell verifier atoms, and declared rule symmetries) improves repair on
real held-out broken answers, and whether a MeTTa-framed repair TRM adds solved items beyond the skill's
operators inside the repair-then-verify pipeline.

## 1. Looked at before registration

- All results of SPEC.md (gates, operators, proposals).
- A probe of solution counts and distances: 461 of 506 study puzzles have one solution; real greedy test
  answers are a median of 6 cells from the nearest solution (Qwen2.5-3B: 15 of 148 have the wrong shape).
- No repair model of any kind has been built or trained.

## 2. Task, data, targets

- **Input**: a puzzle (trees, row and column tent targets) and a broken candidate grid.
- **Output**: a tent or no tent for each non-tree cell; trees are copied from the puzzle. The decoded grid is
  scored by the official verifier.
- **Target**: the valid solution nearest the candidate in Hamming distance (solutions enumerated by the
  hermes-lite CSP, up to 50); ties broken by the solver's order. A wrong-shape candidate counts every
  missing cell as a mismatch.
- **Training rows**: real broken answers from Qwen2.5-3B and Bonsai-8B on the train pool (1,800 rows, 300
  puzzles), plus answers from both models on a new pool `train2` (700 puzzles, disjoint by hash from every
  earlier pool, seed 20261111, one greedy and one sampled answer per puzzle per model), collected before
  training. Answers that already pass are kept (target = themselves). Validation: the val pool's real
  answers (both proposers). Tests: TQ, T8, T27 (greedy, 148 each); sampled sets descriptive.

## 3. Framings (the factor under test)

Same rows, same targets, same network, same training budget; only the per-cell input differs.

| Framing | Per-cell channels |
|---|---|
| raw | candidate one-hot (tree, empty, tent, missing), puzzle tree, valid cell, row target, column target (8) |
| atoms | raw plus the per-cell atoms declared in `metta/campsite_repair_cells.metta`: eligible (orthogonally next to a puzzle tree), row deficit, column deficit, row slack, column slack, touching tent, unmatched tent, tree mismatch (16 in all) |

A second factor, also declared in the package: **symmetry augmentation** (horizontal flip, vertical flip,
both; transposition where the padded grid allows) applied to training rows only. The four arms are
raw, raw+sym, atoms, atoms+sym.

## 4. Model and training

- TRM-style recursive network over the 36 cells of a padded 6x6 grid: cell embedding plus learned row and
  column embeddings; a 2-layer transformer block (width 64, 4 heads) applied recursively with a latent
  state z and an answer state y (3 outer cycles of 3 latent updates and 1 answer update); a per-cell tent
  logit read from y; padding cells masked.
- Loss: binary cross-entropy on non-tree valid cells. AdamW, batch 64, cosine schedule.
- Per arm, the same small grid is searched on validation: learning rate {1e-3, 3e-4} x epochs
  {20, 40, 80}; the selection metric is the share of validation answers whose decoded grid passes the
  verifier. 5 seeds of the selected setting. Decoding: tent where the logit > 0.
- A configuration's prediction for the registered tests is the per-cell majority over its 5 seeds.

## 5. Policies scored

- TRM standalone: commit the decoded grid (solved = passes the verifier).
- menu: the skill's repair-then-verify (candidate, c_repair, dual_repair, each verified; else reject).
- menu+TRM: menu, then the TRM's grid, verified; reject if it fails. Unsafe stays 0 by construction.
- CSP solver: descriptive endpoint.

## 6. Registered tests (exact McNemar on test puzzles, Holm over P1-P4, alpha 0.05)

| ID | Claim | Set | Sides |
|---|---|---|---|
| P1 | TRM[atoms] solves more than TRM[raw], standalone | TQ | two |
| P2 | the same | T8 | two |
| P3 | menu+TRM[atoms] solves more than menu | TQ | one |
| P4 | menu+TRM[atoms] vs menu+TRM[raw] | TQ | two |

Descriptive: the symmetry factor; learning curves (25%, 50%, 100% of training puzzles); T27 and sampled
sets; repair success by distance to the nearest solution; solved items no operator could fix.

## 7. Limits stated now

Campsite has an exact solver, so a repair TRM is never the cheapest way to a solved grid here; the study
measures whether corpus framing changes what a small recursive network learns. Per-cell atoms are
deterministic functions of the raw input, so any benefit is data efficiency or inductive help, not new
information. The MeTTa layer is a declaration compiled to features; no interpreter runs.

## Addenda

**R-A1 (2026-10-08, before any registered training run).**
- Development only so far: one 2-epoch smoke run (atoms+sym, train pool only, 1,845 rows) to check the code
  and timing; validation solved 0.159; no test prediction was written or looked at.
- `train2` holds 682 puzzles after the hash dedup (18 were in earlier pools).
- Timing forces a cheaper selection with the same grid: for each learning rate, one 80-epoch run with the
  cosine schedule over 80 epochs, evaluated on validation at epochs 20, 40 and 80; the best (learning rate,
  checkpoint) is selected. Seed runs repeat the same schedule and stop at the selected epoch (identical to
  taking that checkpoint). The same procedure applies to every arm.
- Order: the raw and atoms arms (all registered tests) run first, in two parallel 4-thread processes; the
  symmetry arms follow and stay descriptive. Learning curves use 3 seeds.

**R-A2 (2026-10-09 02:55, after the seed-0 selection runs on validation, before any test-set prediction
was read; changes no registered test).**
- Seen so far, validation only (seed 0): raw solves 0.168 / 0.272 / 0.366 at epochs 20 / 40 / 80 with
  learning rate 1e-3, and 0.078 / 0.052 / 0.095 at 3e-4; atoms solves 0.263 / 0.272 / 0.310 and
  0.207 / 0.259 / 0.276. Both arms selected 1e-3, 80 epochs.
- The pattern (atoms ahead early and at the lower learning rate, raw ahead at the end) suggests the
  framing helps when the network has less to learn from. A separate confirmatory family is registered now,
  its own Holm correction at 0.05:
  - P5: at 25% of training puzzles (3 seeds, per-cell majority), TRM[atoms] vs TRM[raw], standalone
    solved on TQ, two-sided.
  - P6: the same at 50% of training puzzles.
- Descriptive, also fixed now: the learning-rate robustness of each arm (validation solved at 3e-4) is
  reported as observed above; no test predictions exist for the 3e-4 runs beyond seed 0 and they are not
  used in any test.

**R-A3 (2026-10-09 05:25, POST HOC motivation, registered before any of the runs it describes).**
- Results of P1-P4 (5-seed majority ensembles): P1 78 vs 73 (Holm p = 1.0), P2 81 vs 71 (p = 0.23),
  P3 93 vs 63 (p < 0.001, supported), P4 93 vs 90 (p = 1.0).
- Observed after reading them (test sets, so a hypothesis, not a result): every single atoms model beat
  every single raw model on TQ (68-84 vs 60-67), T8 (72-85 vs 60-67) and T27 (69-83 vs 62-67); majority
  voting narrowed the gap because it helped raw more.
- Confirmation on fresh data, registered now:
  - A fresh test pool `test2` (150 puzzles, seed 20261112, disjoint by hash from every earlier pool) with
    one greedy answer per puzzle from Qwen2.5-3B (TQ2) and from Bonsai-8B (T82), collected after this
    addendum.
  - Five new seeds (5-9) per arm with the selected setting (learning rate 1e-3, 80 epochs) and the same
    training rows; no reselection.
  - C1: single models, TRM[atoms] solves more TQ2 answers than TRM[raw] (5 vs 5 models, exact one-sided
    permutation test on the difference in mean solved; smallest attainable p = 1/252).
  - C2: the same on T82. Holm over C1-C2 at 0.05.
  - Descriptive: the same models on the old test sets; their 5-seed ensembles on TQ2 and T82.
- `test2` holds 141 puzzles after the hash dedup (9 were in earlier pools), so TQ2 and T82 have 141 rows.
