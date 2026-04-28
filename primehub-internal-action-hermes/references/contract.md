# Primehub Internal Action Contract

This skill targets cases where the environment distinguishes between:

- visible content emission
- internal continuation / hidden work

Primary current action token:

- `inspect_and_continue`

Failure modes this skill targets:

- emitting visible text when the env expects internal continuation
- choosing a generic answer token instead of the internal action token

Verification priorities:

1. visible-vs-internal contract
2. exact action token
3. no extra wrapper text
