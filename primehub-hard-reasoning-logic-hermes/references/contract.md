# Primehub Hard Reasoning Logic Contract

Use this skill on tasks where the answer is recovered by constraint tracking rather than long free-form discussion.

Failure modes this skill targets:

- losing entity-role bindings
- forgetting an earlier constraint
- selecting a plausible option without explicit elimination

Preferred reasoning order:

1. list the decision target
2. track the minimum state needed to evaluate candidates
3. eliminate conflicts and unsupported branches
4. compare the survivor to the task wording
5. emit the minimal exact answer token
