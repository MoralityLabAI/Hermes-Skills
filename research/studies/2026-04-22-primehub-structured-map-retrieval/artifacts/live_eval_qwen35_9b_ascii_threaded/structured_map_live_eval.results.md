# Structured-Map Live Eval

| Env | Arm | Status | Reward | Visible Output | Action Type | Action Excerpt |
| --- | --- | --- | ---: | --- | --- | --- |
| ascii_tree | baseline | success | 0.0 | True | direct_answer | <ascii_formatted> packaging +--brew +--linux-arch +--linux-centos +--linux-debian +--linux-fedora +--mac-ports +--snapcraft +--windows-chocolatey `--tools ``` |
| ascii_tree | plain_structured_map | success | 0.0 | True | direct_answer | <ascii_formatted> packaging +--brew +--linux-arch +--linux-centos +--linux-debian +--linux-fedora +--mac-ports +--snapcraft +--windows-chocolatey `--tools ``` |
| ascii_tree | retrieval_assisted | success | 0.7999999999999999 | True | direct_answer | <ascii_formatted> packaging +--brew +--linux-arch +--linux-centos +--linux-debian +--linux-fedora +--mac-ports +--snapcraft +--windows-chocolatey +--tools </ascii_formatted> |

## Notes

- `baseline`: no Hermes structured-map prompt.
- `plain_structured_map`: base `primehub-structured-map-hermes` prompt only.
- `retrieval_assisted`: base structured-map prompt plus Primehub schema memory from `primehub_schema_pack`.

