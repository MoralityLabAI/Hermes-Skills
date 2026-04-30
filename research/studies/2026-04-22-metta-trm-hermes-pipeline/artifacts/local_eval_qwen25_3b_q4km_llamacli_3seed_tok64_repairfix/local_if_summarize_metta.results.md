# Local if_summarize_judge MeTTa Ablation

This run is local-only and uses `llama_cli_external_cuda_gguf` inference, not the lost Snacksack endpoint.

| Arm | Episodes | Reward Total | Avg Reward | Mean Seconds |
| --- | ---: | ---: | ---: | ---: |
| `with_metta_runtime` | 3 | 0.0000 | 0.0000 | 4.0295 |
| `with_metta_runtime_repair` | 3 | 2.0000 | 0.6667 | 4.0295 |
| `without_metta` | 3 | 0.0000 | 0.0000 | 15.3771 |

## Per-Seed Rows

| Seed | Constraint | Arm | Reward | Judge Note | Action Excerpt |
| ---: | --- | --- | ---: | --- | --- |
| 7 | `increasing_length` | `without_metta` | 0.0000 | FASTPATH increasing_length lengths=[25, 8, 1, 3] | Colonel George Alvin Loud, born on June 18, 1852, in Bainbridge Township, Geauga County, Ohio, moved to Au Sable, Mic... |
| 7 | `increasing_length` | `with_metta_runtime` | 0.0000 | FASTPATH increasing_length lengths=[3, 19, 5, 1, 11, 11] | Colonel George A. Loud, born in Bainbridge Township, Ohio, moved to Michigan and became a prominent figure in both po... |
| 7 | `increasing_length` | `with_metta_runtime_repair` | 1.0000 | FASTPATH increasing_length lengths=[2, 6, 11] | Ruins remain. Roman villa roots shaped the castle. Later wars shattered its defenses and left moats and towers behind. |
| 11 | `single_question` | `without_metta` | 0.0000 | FASTPATH single_question sentences=2 | What are the main components and suborders of the Echiuroidea order in the Polychaeta class? [end of text] |
| 11 | `single_question` | `with_metta_runtime` | 0.0000 | FASTPATH single_question sentences=2 | What are the main suborders and families within the Echiuroidea order? [end of text] |
| 11 | `single_question` | `with_metta_runtime_repair` | 1.0000 | FASTPATH single_question sentences=1 | How did a Roman villa become castle ruins? |
| 19 | `if_then` | `without_metta` | 0.0000 | FASTPATH if_then | If Giulio Fasolo made his Serie B debut for Cittadella in a game against Virtus Entella on 18 May 2017, then he is cu... |
| 19 | `if_then` | `with_metta_runtime` | 0.0000 | FASTPATH if_then | If Giulio Fasolo made his Serie B debut for Cittadella in 2017, then he signed with Pro Sesto in the summer of 2020. ... |
| 19 | `if_then` | `with_metta_runtime_repair` | 0.0000 | FASTPATH if_then | If Giulio Fasolo made his Serie B debut for Cittadella in 2017, then he signed with Pro Sesto in the summer of 2020. ... |

## Local Blockers

| Env | Reason |
| --- | --- |
| `psycho_bench` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
| `ascii_tree` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
| `pydantic_adherence` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
