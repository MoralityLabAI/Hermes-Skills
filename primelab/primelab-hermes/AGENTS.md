# Agents

## primelab

Use the `primelab` skill for:

- pod / QLoRA adapter runs
- QLoRA conveyor / stage-machine orchestration
- structured Prime Environments / Verifiers-style runs
- OSS model skill benchmarking under `bench/oss_skill_bench/`
- environment setup
- baseline evaluation
- RL config preparation
- rollout inspection
- result triage

Always:

- verify workspace state first
- run a baseline eval before RL
- inspect failures before proposing more training
- change one major variable at a time
- keep pod billing and structured-environment billing separate when the platform exposes both
- inspect rubrics, datasets, and rollout traces before scaling weak signal
- prefer resumable manifests and receipts over ad hoc one-off scripts for QLoRA runs
- prefer the packaged conveyor entrypoint `scripts/run_prime_qlora_conveyor.sh` and its JSON spec over free-form pod launches
- treat Hosted Training models as an explicit allowlist from `prime rl models`, not from local inference endpoint aliases
- capture hosted runs into `runs/hosted_training/<run_id>/receipt.json` with `scripts/capture_hosted_run.py` instead of relying on the dashboard alone
- use `scripts/hosted_run_menu.py` to render controller-readable ASCII tables when comparing hosted runs
- use `bench/oss_skill_bench/` when the goal is to compare local or OpenRouter models by baseline environment behavior plus small-run QLoRA loss
