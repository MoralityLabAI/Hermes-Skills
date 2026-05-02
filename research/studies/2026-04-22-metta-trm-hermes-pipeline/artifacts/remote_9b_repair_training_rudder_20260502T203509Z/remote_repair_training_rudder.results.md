# Remote repair-training rudder benchmark

- generated_at_utc: `2026-05-02T20:39:50.596363+00:00`
- model_scale: `9b`
- model_name: `Qwen_Qwen3.5-9B-Q4_K_M.gguf`
- base_url: `http://snacksack-ms-7d32.tail3156cd.ts.net:8084/v1`
- split_dir: `C:\projects\Hermes-Skills\Hermes Skills\research\generated\near_miss_repair_curriculum\splits`
- max_cases: `0`
- shots: `4`

| arm | n | target_action_accuracy | repair_action_accuracy | joint_accuracy | json_parse_rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `metta_action_space_rudder` | 88 | 0.7500 | 1.0000 | 0.7500 | 1.0000 |
| `metta_static_gate_rudder` | 88 | 0.9545 | 1.0000 | 0.9545 | 1.0000 |
| `raw_3b_rudder` | 88 | 0.7273 | 0.4091 | 0.3636 | 1.0000 |
| `repair_training_rudder` | 88 | 0.9659 | 0.7955 | 0.7955 | 1.0000 |
