# Intellect-3-Math MeTTa Self-Improvement Smoke

Generated: `2026-05-02T22:42:05.148852+00:00`
Model endpoint: `http://snacksack-ms-7d32.tail3156cd.ts.net:8081/v1`
Held-out rows: `10`

## Live Result

| Arm | Exact | Exact Rate | Avg Latency | Common Actions |
| --- | ---: | ---: | ---: | --- |
| `baseline` | 0/10 | 0.0000 | 1.42s | 10:2, 2014:1, 12:1, 144:1, 15:1, 2018:1, 20:1, 4:1 |
| `current_skill` | 3/10 | 0.3000 | 1.52s | 10:2, 1023:1, 1:1, 17:1, 176:1, 2:1, 1009:1, 10201:1 |
| `metta_self_improved` | 2/10 | 0.2000 | 1.70s | 10:6, 1007:1, 108:1, 1009:1, 100:1 |

## MeTTa Patch

Skill: `Intellect-3-Math-Auditor`

Recovered usable fields from a truncated 27B JSON patch.

Rules:
- (rule math-audit-magnitude (if (and (is-problem-type ?p small-scale) (> ?answer 1000)) (reject-answer ?answer)))
- (rule math-audit-consistency (if (not (satisfies-constraints ?problem ?answer)) (reject-answer ?answer)))
- (rule math-route-decision (if (contains-keyword ?prompt "find a+b+c") (use-strict-integer-mode)))

## Transition Read

{
  "fixed_by_metta": 1,
  "same_outcome": 2,
  "regressed_by_metta": 2,
  "changed_wrong_answer": 5
}

## Commit Gate

{
  "decision": "reject_patch_keep_current_skill",
  "current_exact": 3,
  "metta_exact": 2,
  "fixed_by_metta": 1,
  "regressed_by_metta": 2,
  "rule": "Adopt only when held-out exact improves and fixes are at least regressions."
}

This is a bounded live smoke.  It tests whether a model-drafted skill contract changes held-out behavior; it is not a full benchmark column until rerun over the frozen 200-row slice.
