# Static Gate Saturation Note

Date: 2026-05-02

After analyzing the residual 9B/27B MeTTa static-gate misses, the deterministic
gate was extended with two verifier-visible rules:

```text
if bucket in {repair_success, partial_repair_improvement}:
    commit

if failure_label == c_signature_fail
and bucket == repair_failure_or_no_gain:
    reject_or_abstain
```

These are not prompt tricks. They are typed control-plane rules extracted from
post-repair verifier evidence:

- reward delta
- exactness after repair
- repair success bucket
- c-signature repair status
- no-gain repair status

## Result

The patched `metta_static_gate_rudder` saturates the 88-row non-train benchmark
slice:

| arm | n | target action | repair action | joint | JSON parse |
| --- | ---: | ---: | ---: | ---: | ---: |
| `metta_static_gate_rudder` | 88 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| `metta_validator_gate` | 88 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

Artifact:

- `local_static_gate_saturated_20260502/local_3b_repair_training_rudder.results.md`
- `local_static_gate_saturated_20260502/local_3b_repair_training_rudder.results.json`
- `local_static_gate_saturated_20260502/local_3b_repair_training_rudder.rows.jsonl`

## Architectural Implication

This benchmark slice is now solved by a skill-level TRM/MeTTa control plane, not
by scaling the LLM rudder. The LLM is useful for proposing alternatives,
describing failure hypotheses, and drafting candidate traces, but the decisive
execution policy is:

1. route to the relevant skill/TRM family;
2. choose or generate a repair operator;
3. run verifier-visible post-repair checks;
4. map typed verifier evidence to commit/veto;
5. mine residual errors into new control-plane rules or TRM training rows.

This suggests a self-standing architecture:

```text
LLM generativity -> candidate repairs / hypotheses / trace drafts
TRM maze         -> specialized repair, verifier, retrieval, commit modules
MeTTa plane      -> typed composition, routing, veto, curriculum generation
Skill shell      -> exposes the whole loop as a reusable Hermes skill
```

The research question becomes less "which LLM size is enough?" and more "how
far can verifier-grounded TRM control planes compress the LLM's role into a
proposal/rudder function while preserving or improving task performance?"

## Next Replication Targets

Apply the same loop to additional benchmark families:

- detect residual failures;
- classify them by verifier-visible defect;
- add only justified MeTTa rules or synthesize paired TRM rows;
- rerun 3B/9B/27B rudders;
- report whether the saturated score is invariant to LLM size.

The key negative-control requirement is to keep train/test splits strict: each
new rule must be justified by a typed invariant, not by memorizing case IDs.
