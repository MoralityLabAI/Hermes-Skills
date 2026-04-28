# Intellect-3 Logic Hermes Skill Contract

This document defines the current Hermes skill contract for the Campsite and
`Intellect-3-Logic` family.

## Skill name

- `Hermes/Intellect-3-Logic-v1`

## Purpose

Solve Campsite-style logic grids with a routed internal flow that can call TRM
components as contractual helpers.

## Input contract

Each instance provides:

- a Campsite grid observation
- row constraints
- column constraints
- the original puzzle dimensions
- an answer-only output contract

## Output contract

Return only the completed Python-style 2D list using `T`, `X`, and `C`.
No prose, no explanation, no tags, no markdown.

## Internal stages

1. `parse`
   - read the grid and the row / column signatures
2. `candidate`
   - form an initial completion hypothesis
3. `verify`
   - check tent adjacency, row counts, column counts, and tree pairing
4. `commit`
   - emit the final grid or repair the candidate before emission

## TRM helpers

The skill may call the following contractual TRM helpers:

- `TRM-parse-check`
- `TRM-candidate-grader`
- `TRM-failure-archetype`
- `TRM-repair-hint`
- `TRM-commit-gate`

## Current routing contract

The strongest local signal is the exact `(row_constraints, col_constraints)`
signature.

Treat a row as eligible for the TRM-augmented path when the full signature
matches the positive support set learned from held rows.
Do not infer TRM eligibility from vague puzzle shape or prompt wording.
When working locally, use `scripts/check_signature_gate.py` to make the route
decision deterministically from the exact constraints.

## Canonical artifacts

- `references/logic_hybrid_200.summary.json`
- `references/logic_router_200.summary.json`
- `references/learnings-3-27.md`
