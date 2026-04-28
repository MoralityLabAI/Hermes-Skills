# Primehub Structured Map Contract

This skill targets tasks where the output is a plain-text structure rather than freeform prose.

Primary current contract families:

- indexed mapping lines such as `31: 3`
- plain ASCII structures
- strict JSON-like adherence without extra commentary

Failure modes this skill targets:

- correct content, wrong line format
- extra prose around an otherwise valid structure
- missing or duplicated indices

Verification priorities:

1. allowed line pattern
2. allowed value range
3. no extra wrapper text
4. stable ordering
