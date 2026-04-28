# Intellect-3 Math Hermes Skill Contract

This document defines the current Hermes skill contract for the
`Intellect-3-Math` family.

## Skill name

- `Hermes/Intellect-3-Math-v1`

## Purpose

Solve arithmetic reasoning tasks with a routed internal flow that can call TRM
components as contractual helpers.

## Input contract

Each instance provides:

- a math / reasoning prompt
- any observed support pattern or row signature
- the original task wording
- an answer-only output contract

## Output contract

Return only the final integer answer string.
No prose, no explanation, no tags, no markdown.

## Internal stages

1. `parse`
   - read the givens and constraints
2. `candidate`
   - form a short solution path
3. `verify`
   - check arithmetic consistency
4. `commit`
   - emit the final answer or repair the candidate before emission

## TRM helpers

The skill may call the following contractual TRM helpers:

- `TRM-parse-check`
- `TRM-candidate-grader`
- `TRM-failure-archetype`
- `TRM-repair-hint`
- `TRM-commit-gate`

## Current routing contract

Treat TRM signals as advisory evidence inside the skill workspace.
Default to the plain math path unless an explicit support pattern from the
current benchmark artifacts says TRM is helpful.
Do not infer TRM eligibility from vague thematic similarity.

## Canonical artifacts

- `references/math_hybrid_200.summary.json`
- `references/math_router_100.summary.json`
- `references/learnings-3-27.md`
