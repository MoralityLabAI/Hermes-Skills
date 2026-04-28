# Prime/TRM Skill Imprint

## Corpus
- rows: 187
- bucket_counts: {"negative": 158, "exact_positive": 24, "weak_positive": 5}
- target_action_coverage: 0.1283

## Bench
- critic_bucket_accuracy: 0.7500
- retriever_exact_match_rate: 0.0625
- critic_gated_route_abstain_rate: 0.9062

## Skill Prompt Lines
- Use TRM mainly as a critic and verification layer first; held-out critic accuracy is 0.75 while retrieval exact match is only 0.06.
- When support is weak, stay on the plain skill path instead of forcing TRM escalation; target-action coverage is 0.13 and critic-gated abstention is 0.91.
- When the task specifies a tight answer format, prefer the minimal exact answer over explanatory prose.
- Current positive support is concentrated in psycho_bench, winogrande, antislop, math_env, lisanbench, boolq, simple_bench, truthfulqa; use this imprint as a control-plane prior, not a general reasoning substitute.

## Trainer Lines
- Promote critic and abstention gains first; do not treat the current corpus as strong action-imitation supervision.
- Grow the exact-positive bank before relaxing the router gate or widening TRM default routing.
- Keep collection focused on envs that can add completed exact-positive rows, especially outside the current narrow positive cluster.

## Top Positive Envs
- psycho_bench: exact_positive=4, avg_positive_reward=3.3233, models={"Qwen3.5-27B.Q4_K_M.gguf": 3, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 4}
- winogrande: exact_positive=4, avg_positive_reward=1.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 2, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 2}
- antislop: exact_positive=3, avg_positive_reward=12.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 2, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 1}
- math_env: exact_positive=3, avg_positive_reward=1.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 3, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 3}
- lisanbench: exact_positive=2, avg_positive_reward=2.045, models={"Qwen3.5-27B.Q4_K_M.gguf": 3, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 2}
- boolq: exact_positive=2, avg_positive_reward=1.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 2, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 1}
- simple_bench: exact_positive=2, avg_positive_reward=1.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 2, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 2}
- truthfulqa: exact_positive=2, avg_positive_reward=1.0, models={"Qwen3.5-27B.Q4_K_M.gguf": 3, "Qwen_Qwen3.5-9B-Q4_K_M.gguf": 2}

## Negative Output Statuses
- completed: 134
- openai_request_error: HTTP Error 400: Bad Request: 13
- openai_request_error: timed out: 10
- openai_request_error: <urlopen error [WinError 10060] Se produjo un error durante el intento de conexión ya que la parte conectada no respondió adecuadamente tras un periodo de tiempo, o bien se produjo un error en la conexión establecida ya que el host conectado no ha podido responder>: 1
