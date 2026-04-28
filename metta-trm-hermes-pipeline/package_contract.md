# Package Contract

This file defines the minimum contract for a MeTTa package that is meant to compile into TRM artifacts for Hermes.

## Required Files

- `package.manifest.json`
- at least one `.metta` file in the package root

## Recommended Files

- `package.metta`
  - package identity, linked Hermes skill, target envs
- `contracts.metta`
  - output shapes, constraints, forbids, minimal examples
- `retrieval_policy.metta`
  - query cues, retrieval priorities, surface-routing hints
- `failure_modes.metta`
  - failure modes, repair hints, trace labels
- `examples/minimal_valid.json`
  - one known-good payload for the package

## Manifest Fields

`package.manifest.json` should include:

- `package_id`
- `title`
- `base_skill`
- `trm_overlay`
- `infusion_type`
- `target_envs`
- `bundle_outputs`
- `notes`

## Supported Atom Heads

The lightweight compiler currently recognizes these heads directly:

- `package-id`
- `base-skill`
- `overlay`
- `owner`
- `env`
- `goal`
- `answer-shape`
- `constraint`
- `forbid`
- `minimal-example`
- `example-status`
- `summary`
- `query-cue`
- `retrieval-priority`
- `validation-path`
- `validator-note`
- `verifier-caveat`
- `failure-mode`
- `repair-hint`
- `trace-label`
- `profile-summary`
- `profile-query-cue`
- `profile-constraint`
- `profile-forbid`
- `profile-minimal-example`
- `profile-repair-hint`
- `profile-trace-label`

## Atom Shape

Keep one atom per line:

```text
(answer-shape "ascii_tree" "ascii_formatted_tree")
(summary "ascii_tree" "Exact ASCII tree structure wrapped in <ascii_formatted> tags with no surrounding prose.")
(constraint "ascii_tree" "wrap answer in <ascii_formatted> tags")
(validation-path "pydantic_adherence" "extract_last_json -> model_validate_json")
(verifier-caveat "pydantic_adherence" "historical note about older scorer behavior")
(failure-mode "ascii_tree" "missing closing tag")
(profile-summary "if_summarize_judge" "one_comma" "Return one sentence containing exactly one comma.")
(profile-minimal-example "if_summarize_judge" "one_comma" "Castle ruins rose from Roman roots, and later wars left them broken.")
```

Quoted strings are recommended for all human-readable content.

Profile atoms are optional. Use them when one env contains multiple structural families and the runtime packet needs a profile sub-packet rather than one flat contract.

## Compiler Semantics

The compiler does not try to execute MeTTa. It does a deterministic extraction pass over top-level atoms and groups them into bundle artifacts.

That means this package contract is intentionally simple:

- MeTTa remains the symbolic authoring format
- the compiler remains stable and auditable
- TRM gets predictable JSON outputs

## Output Contract

Compiled bundles should be safe to hand to:

- retrieval overlays
- critic prompt builders
- trace labelers
- runtime packet compilers
- row builders
- deterministic repair passes
