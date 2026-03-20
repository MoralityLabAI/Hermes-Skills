# PrimeLab Hermes Starter

A minimal starter repo for combining:

- **Prime Intellect Lab** for environments, evaluations, hosted RL, and pod-based QLoRA adapter work
- **Hermes skills** for operator workflows
- **Local sanity checks** before spending time or credits on bigger runs
- **Structured Prime Environments / Verifiers-style signal work** before larger training
- **A resumable QLoRA conveyor** that a small controller model can orchestrate from manifests and receipts

This repo is intentionally small. The goal is to make it easy to:

1. scaffold a Prime/Hermes workflow,
2. define or inspect an environment,
3. run a cheap baseline evaluation,
4. inspect failures and rollout traces,
5. then graduate to larger evals, hosted RL, or pod-based adapter runs.

## Repo layout

```text
primelab-hermes/
|-- README.md
|-- AGENTS.md
|-- pyproject.toml
|-- .env.example
|-- .gitignore
|-- skills/
|   `-- primelab.md
|-- configs/
|   |-- base_eval.yaml
|   |-- base_rl.yaml
|   |-- hosted_gsm8k_training.example.toml
|   |-- hosted_env_training.example.toml
|   `-- qlora_conveyor.example.json
|-- environments/
|   `-- toy_env/
|       |-- __init__.py
|       |-- env.py
|       |-- dataset.jsonl
|       `-- rubric.py
|-- scripts/
|   |-- build_qlora_dataset.py
|   |-- exfiltrate_prime_qlora_run.sh
|   |-- remote_qlora_conveyor.py
|   |-- inspect_rollouts.py
|   |-- run_eval.sh
|   |-- run_prime_qlora_conveyor.sh
|   |-- run_rl.sh
|   |-- stage_qlora_bundle.py
|   `-- train_qlora_sft.py
|-- requirements/
|   `-- qlora.txt
|-- runs/
|   `-- qlora_conveyor/
|-- data/
|   `-- qlora_conveyor/
|-- src/
|   `-- primelab_hermes/
|       |-- __init__.py
|       |-- local_eval.py
|       |-- qlora_conveyor.py
|       `-- trainer_compat.py
`-- notebooks/
    `-- debug_env.ipynb
```

There is also a dedicated benchmark lane under [bench/oss_skill_bench](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/bench/oss_skill_bench/README.md) for testing whether small local or API-routed OSS models can actually execute this skill pattern.

## Setup

### 1) Python environment

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

### 2) Prime CLI

```bash
uv tool install -U prime
prime login
prime lab setup
```

### 2.5) QLoRA extras

The pod and dataset scripts need the heavier training dependencies in addition to the base starter install.

```bash
uv pip install -r requirements/qlora.txt
```

### 3) Run a local sanity check

This runs a tiny fake-model local evaluator so you can validate the dataset and rubric loop even before wiring in a real hosted or local model.

```bash
python -m primelab_hermes.local_eval \
  --dataset environments/toy_env/dataset.jsonl \
  --output rollouts.json
```

Then inspect results:

```bash
python scripts/inspect_rollouts.py rollouts.json
```

## Prime workflow

The intended loop is:

1. **Define environment or pod lane**
2. **Run baseline eval or smoke check**
3. **Inspect failures**
4. **Tighten harness / rubric / task design**
5. **Only then run RL or adapter training**

If the platform exposes a structured environment UI or hosted-environment billing path, treat that cost center separately from pod spend and confirm it before scaling.
For QLoRA runs, prefer a stage machine with explicit receipts over a single opaque launch script so a controller model can resume or redirect safely.

### Example Prime commands

```bash
prime eval run toy_env -m qwen-9b -n 10 -r 2
prime rl run configs/base_rl.yaml
prime rl logs <run_id> -f
bash scripts/run_prime_qlora_conveyor.sh .
RUN_ROOT_LOCAL=runs/qlora_conveyor/<run_id> bash scripts/exfiltrate_prime_qlora_run.sh .
```

You will likely need to adapt the config and environment registration details to the current Prime CLI/API version you are using.

## Design principles

- **Environment quality > model size**
- **Baseline eval before RL**
- **Adapter runs and structured-env runs are different tools**
- **Pod runs should emit receipts that a small controller can read**
- **Hosted Training only works for listed supported models**
- **One change per experiment**
- **Inspect trajectories, not just aggregate reward**
- **Keep the first loop cheap**

## Hosted Training

The formal Environments Hub training path is:

- install or select an environment from the hub
- run a baseline with `prime eval run`
- create a `.toml` config with `[[env]].id = "owner/env-name"`
- launch with `prime rl run <config>`

This path is stricter than the pod path:

- the model must be supported by Hosted Training
- the environment should come from the Environments Hub or be packaged as a proper Verifiers environment
- the training feature and its billing are separate from raw pod rentals

The current Prime docs say Hosted Training supports:

- `Qwen/Qwen3-4B-Instruct-2507`
- `Qwen/Qwen3-4B-Thinking-2507`
- `Qwen/Qwen3-30B-Instruct-2507`
- `Qwen/Qwen3-30B-Thinking-2507`
- `Qwen/Qwen3-235B-Instruct-2507`
- `Qwen/Qwen3-235B-Thinking-2507`
- `PrimeIntellect/INTELLECT-3`

Use [hosted_env_training.example.toml](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/configs/hosted_env_training.example.toml) as the starter config for this lane.
Use [hosted_gsm8k_training.example.toml](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/configs/hosted_gsm8k_training.example.toml) when you want the concrete `gsm8k` version of the same lane.

Important constraint:

- local endpoint aliases such as `trinity-mini` in a lab workspace may work for eval or inference, but they are not proof of Hosted Training support
- if the model is not returned by `prime rl models`, route it to the pod / QLoRA conveyor instead
- Qwen3 thinking models need extra care in multi-turn training because the Prime docs note that Qwen3 chat templates can remove prior `<think>` blocks

Minimal `gsm8k` hosted flow:

```bash
prime eval run primeintellect/gsm8k -m Qwen/Qwen3-30B-A3B-Instruct-2507 -n 16 -r 1
prime rl run configs/hosted_gsm8k_training.example.toml
prime rl logs <run_id> -f
```

## QLoRA conveyor

The starter now includes a generalized QLoRA runner derived from the working Prime pod scripts:

- edit [qlora_conveyor.example.json](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/configs/qlora_conveyor.example.json)
- build training JSONL with [build_qlora_dataset.py](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/scripts/build_qlora_dataset.py)
- stage the runnable pod bundle with [stage_qlora_bundle.py](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/scripts/stage_qlora_bundle.py)
- launch the pod conveyor with [run_prime_qlora_conveyor.sh](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/scripts/run_prime_qlora_conveyor.sh)
- pull artifacts and terminate the pod with [exfiltrate_prime_qlora_run.sh](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/scripts/exfiltrate_prime_qlora_run.sh)
- remote sequential training is handled by [remote_qlora_conveyor.py](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/scripts/remote_qlora_conveyor.py)
- stage state and receipts are handled by [qlora_conveyor.py](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/src/primelab_hermes/qlora_conveyor.py)

The default contract is intentionally conservative:

- Qwen 27B
- 4-bit QLoRA
- explicit stage-state receipts
- sequential env training
- small-action orchestration suitable for a Qwen 9B controller with reasoning enabled

## OSS skill bench

Use [bench/oss_skill_bench](C:/projects/Hermes-Skills/Hermes%20Skills/primelab/primelab-hermes/bench/oss_skill_bench/README.md) when you want to compare OSS models by:

- whether they can complete a small real-environment baseline
- whether they can produce stable QLoRA training signal on a small exported slice
- what final loss they reach on the default tiny run

This is meant as a practical competence probe for candidate operator models, including smaller local Qwen variants and API-routed OSS models.

## Extending this repo

Natural next steps:

- replace the toy environment with a real tool-using environment
- add a local model adapter instead of the fake model in `local_eval.py`
- add richer reward components
- add multi-turn state transitions
- add traces for routing / controller analysis

## Suggested Git init

```bash
git init
git add .
git commit -m "Initial PrimeLab Hermes starter"
```
