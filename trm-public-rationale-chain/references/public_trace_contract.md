# Public Trace Contract

## Purpose

This contract creates an observable reasoning trace for experiments. It is not a method for extracting hidden chain-of-thought.

## Stage order

1. `TRM_PARSE`
2. `TRM_CRITIC`
3. `TRM_COMPRESS`
4. `FINAL`

## Stage semantics

- `TRM_PARSE`
  - Restate the task and answer format.
  - One short line.
- `TRM_CRITIC`
  - State the main check, failure mode, or uncertainty.
  - One short line.
- `TRM_COMPRESS`
  - Give the smallest public rationale that still supports the answer.
  - One short line.
- `FINAL`
  - Emit the exact answer payload for the task family.

## Output formats

### Tagged

```text
TRM_PARSE: ...
TRM_CRITIC: ...
TRM_COMPRESS: ...
FINAL: ...
```

### Compact JSON

```json
{
  "trm_parse": "...",
  "trm_critic": "...",
  "trm_compress": "...",
  "final": "..."
}
```

## Constraints

- Max public rationale lines before `FINAL`: `3`
- Recommended max chars per rationale line: `96`
- No markdown fences unless the calling task explicitly requests them
- No claims about exposing hidden chain-of-thought
- No generic filler like "I will think step by step"

## Family notes

### Logic

- Keep the underlying flow `parse -> candidate -> verify -> commit`
- Final payload should still be the completed grid

### Math

- Keep the underlying flow `parse -> candidate -> verify -> commit`
- Final payload should still be the final answer string

### Generic

- Use the final line to match the explicit task contract exactly

## Good uses

- Small-model benchmarking where visible traces are permitted
- Collecting short rationale supervision for later TRM row building
- Comparing answer-only vs public-trace variants

## Bad uses

- Tasks that require answer-only output
- Claims that the model has revealed hidden internal reasoning
- Long freeform essays masquerading as traces
