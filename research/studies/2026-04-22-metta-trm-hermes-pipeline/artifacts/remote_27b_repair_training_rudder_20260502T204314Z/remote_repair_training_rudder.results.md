# Remote repair-training rudder benchmark

- generated_at_utc: `2026-05-02T20:50:03.365262+00:00`
- model_scale: `27b`
- model_name: `Qwen3.5-27B.Q4_K_M.gguf`
- base_url: `http://snacksack-ms-7d32.tail3156cd.ts.net:8081/v1`
- split_dir: `C:\projects\Hermes-Skills\Hermes Skills\research\generated\near_miss_repair_curriculum\splits`
- max_cases: `0`
- shots: `4`

| arm | n | target_action_accuracy | repair_action_accuracy | joint_accuracy | json_parse_rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `metta_action_space_rudder` | 88 | 0.8068 | 1.0000 | 0.8068 | 1.0000 |
| `metta_static_gate_rudder` | 88 | 0.9432 | 1.0000 | 0.9432 | 1.0000 |
| `raw_3b_rudder` | 88 | 0.7614 | 0.5341 | 0.4886 | 1.0000 |
| `repair_training_rudder` | 88 | 0.9318 | 0.7955 | 0.7955 | 1.0000 |
