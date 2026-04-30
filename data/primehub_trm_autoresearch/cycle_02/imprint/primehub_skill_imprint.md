# Prime/TRM Skill Imprint

## Corpus
- rows: 127
- bucket_counts: {"negative": 106, "exact_positive": 17, "weak_positive": 4}
- target_action_coverage: 0.1339

## Bench
- critic_bucket_accuracy: 0.7619
- retriever_exact_match_rate: 0.0476
- critic_gated_route_abstain_rate: 0.9048

## Skill Prompt Lines
- Use TRM mainly as a critic and verification layer first; held-out critic accuracy is 0.76 while retrieval exact match is only 0.05.
- When support is weak, stay on the plain skill path instead of forcing TRM escalation; target-action coverage is 0.13 and critic-gated abstention is 0.90.
- When the task specifies a tight answer format, prefer the minimal exact answer over explanatory prose.
- Current positive support is concentrated in psycho_bench, antislop, lisanbench, math_env, winogrande, arc, boolq, hellaswag; use this imprint as a control-plane prior, not a general reasoning substitute.

## Trainer Lines
- Promote critic and abstention gains first; do not treat the current corpus as strong action-imitation supervision.
- Grow the exact-positive bank before relaxing the router gate or widening TRM default routing.
- Keep collection focused on envs that can add completed exact-positive rows, especially outside the current narrow positive cluster.

## Top Positive Envs
- psycho_bench: exact_positive=4, avg_positive_reward=3.3233, models={"Qwen3.5-27B.Q4_K_M.gguf": 2, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 4}
- antislop: exact_positive=2, avg_positive_reward=12.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 1, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 1}
- lisanbench: exact_positive=2, avg_positive_reward=2.045, models={"Qwen3.5-27B.Q4_K_M.gguf": 2, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 2}
- math_env: exact_positive=2, avg_positive_reward=1.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 3, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 2}
- winogrande: exact_positive=2, avg_positive_reward=1.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 1, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 1}
- arc: exact_positive=1, avg_positive_reward=1.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 1, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 1}
- boolq: exact_positive=1, avg_positive_reward=1.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 1, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 1}
- hellaswag: exact_positive=1, avg_positive_reward=1.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 1, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 1}

## Negative Output Statuses
- completed: 87
- openai_request_error: timed out: 10
- openai_request_error: HTTP Error 400: Bad Request: 8
- openai_request_error: <urlopen error [WinError 10060] Se produjo un error durante el intento de conexión ya que la parte conectada no respondió adecuadamente tras un periodo de tiempo, o bien se produjo un error en la conexión establecida ya que el host conectado no ha podido responder>: 1
