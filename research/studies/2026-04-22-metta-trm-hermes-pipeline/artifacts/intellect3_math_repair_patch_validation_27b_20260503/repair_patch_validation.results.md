# Intellect-3-Math Repair Patch Validation

Generated: `2026-05-03`

## Shards

| Shard | Rows | Incumbent | Near-Miss Repair | Fixes vs Incumbent | Regressions vs Incumbent | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `offset40` | 10 | 1 | 2 | 2 | 1 | `row_level_signal_only` |
| `offset50` | 10 | 2 | 0 | 0 | 2 | `reject_global_patch` |

## Read

The near-miss repair patch fixed two typed semi-failures on the shard that
inspired it: `1009 -> 1008` for a strict circular recurrence/positivity row and
`1023 -> 1024` for a locker elimination row.  On the next held-out shard it
regressed two incumbent hits and added no fixes.

This is evidence for repair-curriculum data generation, not evidence for global
prompt adoption.  The correct training target is a per-row TRM commit/veto gate
that recognizes when the repair patch is applicable.
