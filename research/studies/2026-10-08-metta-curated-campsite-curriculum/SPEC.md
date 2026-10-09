# SPEC: MeTTa-curated near-miss curriculum, trained TRM gates, and corrected benches

Registered 2026-10-08, before any model call or TRM training in this study. Changes after
registration go in dated addenda at the end. Everything runs on this PC's CPU and RAM; the GPU
is not used.

## 0. Why this study exists

The April 29 paper "MeTTa-Scaffolded Repair Curricula for TRM-Infused Hermes Skills" proposes
that MeTTa-typed verifier state turns semi-failed outputs into training rows for small recursive
gates (TRMs). It never trains one. Its curriculum rows for the main environment carry no
candidate content (`candidate_excerpt` is `arm=logic_skill_trm transform=original`), and its
rudder benchmark has two measurement defects found on 2026-10-08:

- the retrieval arm scores examples on the eval row's own `bucket`, `action` and `target_action`;
- the 18 unseen-family rows need repair actions absent from the allowed-action list.

This study supplies the missing training run on a curriculum with content, and reruns the
paper's two LLM benches without those defects.

## 1. Looked at before registration

- The published row-level results of the rudder benchmark (3B, 9B, 27B) and of the two
  mixed-contract suites (3B).
- jev-qwen SPEC-U3/U4/U5 reports (2026-10-07): a leak-free rerun of the rudder benchmark, and
  Campsite repair tests with synthetic defects and with real proposals. Their finding that a
  gate trained on synthetic defects does not transfer to real proposals motivates H1.
- A tabulation of 117 standard-size Bonsai-8B Campsite proposals from jev-qwen U5: 0 pass as
  written, `dual_repair` fixes 62, `c_repair` fixes 34. No proposal from this study's puzzles
  has been generated or inspected.

## 2. Components

**Environment.** hermes-lite `agent.intellect3_logic` (read-only import): Campsite puzzle
generator, official verifier (public rules only: syntax, shape, trees unchanged, row and column
tent counts, no touching tents, perfect tree-tent matching) and CSP solver. The generator does
not guarantee a unique solution, so success means "passes the official verifier", never
"equals a stored grid".

**Repair operators.** Hermes-Skills HEAD
`research/scripts/run_intellect3_camp_gate_micro_env.py`: `c_only_projection` (`c_repair`) and
`dual_signature_projection` (`dual_repair`), executed unchanged from `git show HEAD`. They read
the expected grid only for its shape and T/C row and column counts; the code asserts these equal
the public puzzle before any use.

**MeTTa package.** `metta/campsite_curriculum.metta` declares the curriculum schema: the
verifier atoms, the count atoms, the repair operators with preconditions, the action menu and
the bucket rules. `src/metta_schema.py` parses it; the typed feature vector of every row is
exactly the declared atoms, in declared order. No MeTTa interpreter runs at inference.

**Puzzles** (`generate_unseen_tasks`, sizes 3x5 to 5x5 plus a 6x6 share; pools disjoint by
puzzle hash, checked):

| Pool | Puzzles | Seed | Use |
|---|---|---|---|
| shots | 4 | 20261107 | three few-shot examples for proposals |
| train | 300 | 20261108 | curriculum training rows |
| val | 60 | 20261109 | epoch selection only |
| test | 150 | 20261110 | registered tests |

**Proposers** (PrismML llama-server, CPU only, `-ngl 0`, 8 threads, reasoning off, 1-bit Q1_0):

| Proposer | Pools | Per puzzle |
|---|---|---|
| Bonsai-8B | train, val, test | 1 greedy + 2 sampled on train; 1 greedy + 1 sampled on val and test |
| Bonsai-27B | test | 1 greedy |

Sampling: temperature 0.7, top-p 0.95, seed from (pool, puzzle, k). Prompt: rules, three solved
shots, the puzzle; the grid is parsed with the U4/U5 parser.

**Synthetic near-misses.** The eight jev-qwen U4 defect types (correct, drop_tent, extra_tent,
move_in_row, move_any, swap_rect, tree_mutation, bad_shape) on train puzzles (one per type per
puzzle where constructible) and on test puzzles (descriptive only).

## 3. Curriculum rows

Each candidate (real or synthetic) becomes one row:
- typed state: the MeTTa-declared atoms of the candidate;
- raw state: the candidate grid, the puzzle trees and the row and column targets as padded
  one-hot cells (no derived atom);
- for each operator: its output, the output's atoms, and whether the output passes;
- bucket: `exact_positive` (passes as written), `repair_success` (cheapest operator that
  passes), `partial_improvement` (an operator lowers the failed-gate count without passing),
  `no_gain`;
- label `best_action`: the first of commit, c_repair, dual_repair that yields a passing grid,
  else reject (the U4 menu order).

## 4. Part G: TRM gates

**Gate.** A pre-repair action gate: from the candidate's state, choose commit, c_repair,
dual_repair or reject. Structure: hermes-lite `TinyRecursivePolicy` (input projection, a
recurrent update on [h, x] repeated 4 times, action head), hidden 64. Trained with cross-entropy
on train rows; epochs chosen from {50, 100, 200, 400} by val accuracy; 5 seeds.

**Factors.**
- features: `typed` (MeTTa atoms), `raw` (one-hot cells), `typed+raw`;
- curriculum source: `real` (Bonsai-8B train proposals), `synthetic` (U4 defects on the same
  train puzzles);
- training size N: 25, 50, 100, 200, 400 and all rows, drawn by puzzle.

**Policies scored end to end** on test items (committed grid = the action's output; success =
the committed grid passes; unsafe = a committed grid fails; reject = nothing committed):

| Policy | Definition |
|---|---|
| as-written | commit the proposal |
| flow-c, flow-dual | the published skill policies `c_repair_if_c_fail`, `dual_repair_if_any_sig_fail` (never reject) |
| static | commit if it passes; reject if the shape is wrong; c_repair if trees are unchanged; else dual_repair |
| TRM[f, s, N] | the gate's action |
| verify | c_repair then verify; else dual_repair then verify; else reject |
| TRM+verify | the gate's action, then reject if the output fails the verifier |
| menu ceiling | best_action |
| CSP | the solver's grid (closure endpoint, descriptive) |

For registered tests a TRM configuration is the per-item majority vote of its 5 seeds, so the
unit is the test puzzle. Per-seed spread is reported.

**Test sets.** T8: Bonsai-8B greedy proposals on the 150 test puzzles. T27: Bonsai-27B greedy
proposals on the same puzzles. The sampled test proposals are descriptive.

**Registered tests** (exact McNemar on discordant test puzzles, Holm over G1-G4 at 0.05):

| ID | Claim | Set | Metric | Sides |
|---|---|---|---|---|
| G1 | TRM[typed, real, all] vs TRM[typed, synthetic, all] | T8 | success | two |
| G2 | TRM[typed, real, all] vs TRM[raw, real, all] | T8 | success | two |
| G3 | TRM[typed, real, all] has fewer unsafe commits than flow-dual | T8 | unsafe | one |
| G4 | TRM[typed, real, all] has fewer unsafe commits than flow-dual | T27 | unsafe | one |

Descriptive: learning curves; every policy's success, unsafe and reject rates with Wilson
intervals; operator and verifier calls per item; the curriculum's bucket and atom-pattern
counts.

## 5. Part R: rudder benchmark rerun

The 88 non-train rows of `near_miss_repair_curriculum/splits`, the published prompt builders,
Bonsai-8B via the chat endpoint at temperature 0, 64 tokens.

| Arm | Change from the published arm |
|---|---|
| raw | none (allowed actions: the six seen in train) |
| raw-fullvocab | allowed actions: every action in any split (unseen-family actions reachable) |
| retrieval-published | none (leaky; kept to measure the leak) |
| retrieval-clean | query tokens and bonuses use pre-repair fields only (no bucket, action, target) |
| action-space | none (MeTTa table fixes the repair action) |

CPU arms: a two-head TRM on the published features (as jev-qwen U3) and a train-majority lookup.

**Registered tests** (joint accuracy, 88 rows, exact McNemar, Holm over R1-R2):
- R1: retrieval-clean vs raw (two-sided).
- R2: retrieval-published vs retrieval-clean (two-sided).

Descriptive: false commits; the always-commit decomposition of action-space; the published
3B/9B/27B rows rescored.

## 6. Part M: mixed-contract rerun

The published 50-row held-out and 30-row hard suites, frozen validators and prompts from HEAD,
Bonsai-8B at temperature 0, 64 tokens. One arm is added so that contract and wording separate:

| Arm | System prompt | Contract shown |
|---|---|---|
| baseline | published baseline | no |
| contract-neutral | published baseline | yes (new) |
| skill-wording | published `pure_trm` | yes |
| gate-wording | published `metta_runtime` | yes |
| repair-feedback | published repair after gate-wording | yes, plus validator feedback |
| repair-blind | published blind repair after gate-wording | yes |

**Registered tests** (exact success, held-out 50, exact McNemar, Holm over M1-M3):
- M1: contract-neutral vs baseline.
- M2: gate-wording vs contract-neutral.
- M3: repair-feedback vs repair-blind.

The hard suite is descriptive.

## 7. Order and limits

Order: CPU preparation; Bonsai-8B proposals (test, train, val); Bonsai-27B test proposals;
Part R; Part M; TRM training and scoring; report. One model server at a time, 8 threads,
below-normal priority.

Limits stated now: Campsite has a millisecond CSP solver, so repair is never the cheapest path
to a solved grid here; the study measures the curriculum and gate methodology, not the best way
to solve Campsite. Bonsai-8B and Bonsai-27B are 1-bit models, not the paper's Qwen2.5-3B, which
is not on this PC. One proposer family supplies all real training rows.

## Addenda

**A1 (2026-10-08, before any TRM training or any curriculum statistics beyond the smoke test).**
- Pool sizes after the hash dedup: val 58 puzzles, test 148 (two of each were in earlier pools).
- Unregistered training details, fixed now: AdamW, learning rate 5e-3, weight decay 1e-4, full
  batch; the four registered step counts are checkpoints of one run, and the best by val accuracy
  is kept.
- An operator whose precondition fails (wrong shape or symbols) returns nothing; a policy that
  chose it commits the candidate unchanged, as in jev-qwen U4. The `verify` policy also verifies
  the candidate as written before repairing.
- The smoke test looked at the synthetic train rows' best-action counts and at 168 Bonsai-8B test
  proposals' buckets (96 repairable, 72 not, 0 exact). No gate was trained before this addendum.

**A2 (2026-10-08, POST HOC, after G1-G3 were computed; changes no registered test).**
- To tell a weak gate from missing information, `src/posthoc_ceiling.py` fits logistic regression
  and gradient-boosted trees (scikit-learn defaults) on the same real train rows and scores them on
  T8 and T8s with the same outcome function, plus the AUC for "some operator fixes it".
- Result: label accuracy 0.66-0.74 (TRM typed: 0.70), repairability AUC 0.74-0.84, solved 35-52
  of 148 with 16-26 unsafe commits. The TRM is not the bottleneck; the pre-repair state is.

**A3 (2026-10-08, registered before any Qwen2.5-3B call; the author approved the download).**
The April model is now on this PC: `Qwen/Qwen2.5-3B-Instruct-GGUF` file `qwen2.5-3b-instruct-q4_k_m.gguf`,
revision 7dabda4d, SHA-256 626b4a66…c62d (matches the Hugging Face LFS record). It runs on CPU with
the PrismML llama.cpp build (`-ngl 0`); the April runs used a CUDA build (b8922), so greedy outputs may
differ on a few rows. Threads and batch sizes are raised (8 threads, batch and micro-batch 512) for
speed; temperature 0, top-p 1, 8-bit KV cache, context and token caps stay as in April.

- **Q-R (replication of the published rudder arms).** The April 28 runner (`ef17a7fd`, the last version
  before the May rules that read the bucket) is executed unchanged from git on the HEAD splits for all
  six published arms. Row-level agreement with the published 3B rows is reported per arm (fidelity
  check, descriptive). The new arms (raw-fullvocab, retrieval-clean) use the same runner's prompt
  builders and `run_llama_completion`. Registered: R1q (retrieval-clean vs raw), R2q
  (retrieval-published vs retrieval-clean), joint accuracy on 88 rows, exact McNemar, Holm over the two.
- **Q-M (replication of the output-contract suites).** The HEAD mixed-contract runner is executed
  unchanged on both suites with `--include-blind-repair`; the contract-neutral arm uses its
  `arm_prompt` and `run_llama_completion`. Fidelity: agreement with the published 3B rows. Registered:
  M1q (contract-neutral vs baseline), M2q (gate-wording vs contract-neutral), M3q (feedback vs blind
  repair), held-out 50, Holm over the three.
- **Q-C (constraint extraction).** The HEAD noisy constraint-extraction runner is executed unchanged on
  the 12 noisy rows; descriptive only.
- **Q-G (Qwen2.5-3B as proposer).** Same pools and plan as Bonsai-8B (1 greedy + 2 sampled per train
  puzzle; 1 + 1 on val and test), same prompt and parser, llama-server on CPU. The curriculum and gates
  are rebuilt with a third source `real-Qwen2.5-3B`. New test sets TQ (greedy) and TQs (sampled).
  Registered, Holm over G1q-G4q: G1q TRM[typed, Qwen real, all] vs TRM[typed, synthetic, all] on TQ
  (success, two-sided); G2q TRM[typed, Qwen real] vs TRM[raw, Qwen real] on TQ (success, two-sided);
  G3q TRM[typed, Qwen real] fewer unsafe than flow-dual on TQ (one-sided); G4q the same gate fewer
  unsafe than flow-dual on T8, Bonsai-8B's answers (unseen proposer, one-sided). Descriptive: the
  cross-proposer matrix (gates trained on each real source, tested on TQ, T8, T27).
- The Bonsai results and tests G1-G4, R1-R2, M1-M3 stand unchanged; the Qwen tests are a separate
  family with their own Holm correction.

**A4 (2026-10-08, POST HOC, after G1q-G4q were computed; changes no registered test).**
- The A2 classifier check was extended to the Qwen2.5-3B curriculum (TQ, TQs). Logistic regression and
  gradient-boosted trees solve 34-47 of 148 with 19-32 unsafe commits (repairability AUC 0.72-0.83),
  against 48 and 24 for the typed TRM gate. The information limit holds for the April model's failures.
- Replication notes: the leaky retrieval arm of the rudder benchmark scores 17 here against 28 in April;
  all 15 differing rows flip `dual_repair` to `c_repair` with identical retrieved examples and identical
  commit decisions. The constraint-extraction rows path exceeded Windows' path limit inside the extracted
  tree, so the committed file was copied to a short path (same bytes) and the job rerun.
