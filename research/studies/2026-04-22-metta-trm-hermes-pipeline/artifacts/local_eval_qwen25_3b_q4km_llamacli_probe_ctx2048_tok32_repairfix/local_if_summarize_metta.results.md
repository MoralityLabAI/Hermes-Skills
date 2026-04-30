# Local if_summarize_judge MeTTa Ablation

This run is local-only and uses `llama_cli_external_cuda_gguf` inference, not the lost Snacksack endpoint.

| Arm | Episodes | Reward Total | Avg Reward | Mean Seconds |
| --- | ---: | ---: | ---: | ---: |
| `with_metta_runtime` | 1 | 0.0000 | 0.0000 | 12.0998 |
| `with_metta_runtime_repair` | 1 | 1.0000 | 1.0000 | 12.0998 |
| `without_metta` | 1 | 0.0000 | 0.0000 | 48.1857 |

## Per-Seed Rows

| Seed | Constraint | Arm | Reward | Judge Note | Action Excerpt |
| ---: | --- | --- | ---: | --- | --- |
| 7 | `increasing_length` | `without_metta` | 0.0000 | FASTPATH increasing_length lengths=[16] | Colonel George Alvin Loud, born on June 18, 1852, in Bainbridge Township, Geauga County, Ohio, moved |
| 7 | `increasing_length` | `with_metta_runtime` | 0.0000 | FASTPATH increasing_length lengths=[3, 19, 3] | Colonel George A. Loud, born in Bainbridge Township, Ohio, moved to Michigan and became a prominent figure in both po... |
| 7 | `increasing_length` | `with_metta_runtime_repair` | 1.0000 | FASTPATH increasing_length lengths=[2, 6, 11] | Ruins remain. Roman villa roots shaped the castle. Later wars shattered its defenses and left moats and towers behind. |

## Local Blockers

| Env | Reason |
| --- | --- |
| `psycho_bench` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
| `ascii_tree` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
| `pydantic_adherence` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
