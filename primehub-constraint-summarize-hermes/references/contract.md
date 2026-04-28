# Primehub Constraint Summarize Contract

This skill targets tasks where the model must infer a structural summary family from the instruction and then satisfy that family exactly.

Primary current contract families:

- exact word-count summaries
- exact sentence-count summaries
- punctuation-sensitive summaries such as `one comma`
- wrapper-sensitive outputs such as hashtags, bullets, or XML word tags
- role-shaped summaries such as a single question, question-answer pair, or newspaper headline

Failure modes this skill targets:

- correct topic, wrong structural family
- right family, wrong count or delimiter
- valid sentence but extra explanation around it
- missing wrapper tags or wrong casing
- empty output or fallback action on a structure-only task

Verification priorities:

1. correct family selection from the literal instruction
2. exact counts, punctuation, wrappers, and casing
3. no extra prose outside the required output shape
4. only then, reasonable topic relevance
