# Local if_summarize_judge MeTTa Ablation

This run is local-only and uses `llama_cli_external_cuda_gguf` inference, not the lost Snacksack endpoint.

| Arm | Episodes | Reward Total | Avg Reward | Mean Seconds |
| --- | ---: | ---: | ---: | ---: |
| `with_metta_runtime` | 1 | 0.0000 | 0.0000 | 4.0564 |
| `with_metta_runtime_repair` | 1 | 1.0000 | 1.0000 | 4.0564 |
| `without_metta` | 1 | 0.0000 | 0.0000 | 12.0495 |

## Per-Seed Rows

| Seed | Constraint | Arm | Reward | Judge Note | Action Excerpt |
| ---: | --- | --- | ---: | --- | --- |
| 7 | `increasing_length` | `without_metta` | 0.0000 | FASTPATH increasing_length lengths=[12, 4, 4, 44, 13, 9, 7, 3, 5, 5, 5, 5, 11, 1, 10, 1, 1, 4, 5, 4, 1] | --no-conversation is not supported by llama-cli please use llama-completion instead Loading model... ▄▄ ▄▄ ██ ██ ██ █... |
| 7 | `increasing_length` | `with_metta_runtime` | 0.0000 | FASTPATH increasing_length lengths=[12, 4, 4, 47, 10, 13, 7, 27, 17, 5, 4, 1] | --no-conversation is not supported by llama-cli please use llama-completion instead Loading model... ▄▄ ▄▄ ██ ██ ██ █... |
| 7 | `increasing_length` | `with_metta_runtime_repair` | 1.0000 | FASTPATH increasing_length lengths=[2, 6, 11] | Ruins remain. Roman villa roots shaped the castle. Later wars shattered its defenses and left moats and towers behind. |

## Local Blockers

| Env | Reason |
| --- | --- |
| `psycho_bench` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
| `ascii_tree` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
| `pydantic_adherence` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
