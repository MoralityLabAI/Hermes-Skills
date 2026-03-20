# OSS Skill Bench

Use this bench when the goal is to test whether a local or API-routed OSS model can execute the PrimeLab skill pattern competently.

This bench is not the same thing as production training. It is a capability probe for the model-as-operator and model-as-trainee loop.

The default pattern is:

- run a small baseline eval on a real hub environment
- train a small QLoRA on a small exported slice from the same environment family
- record whether training starts cleanly, advances, and finishes
- record final loss and any obvious formatting or reasoning failures

Primary success signals:

- the model can complete the baseline environment call path
- the QLoRA trainer loads and runs without orchestration failure
- the training log shows decreasing or at least non-divergent loss
- the run produces an adapter and `run_meta.json`

Primary failure signals:

- the model cannot follow the environment response contract
- the trainer fails before useful steps begin
- the run finishes but produces no meaningful loss signal
- the adapter overfits into boilerplate or collapses formatting

Use these files:

- `default_qlora_spec.json`
- `default_hosted_eval.toml`
- `summarize_bench.py`

Machine-local note:

- on this machine, the Prime env code clone is at `C:/projects/prime-environments`
- the exported `gsm8k` parquet data used by the default bench lives at `D:/Research_Engine/prime_envs/gsm8k`

Always:

- keep the first run small
- compare models on the same spec before changing the task
- treat final loss as a coarse skill signal, not a publication-grade metric
- record whether the model needed reasoning enabled to orchestrate the run cleanly
