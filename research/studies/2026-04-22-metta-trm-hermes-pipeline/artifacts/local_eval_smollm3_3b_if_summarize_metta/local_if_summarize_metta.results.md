# Local if_summarize_judge MeTTa Ablation

This run is local-only and uses `transformers_direct_local` inference, not the lost Snacksack endpoint.

| Arm | Episodes | Reward Total | Avg Reward | Mean Seconds |
| --- | ---: | ---: | ---: | ---: |
| `with_metta_runtime` | 3 | 0.0000 | 0.0000 | 171.7833 |
| `with_metta_runtime_repair` | 3 | 3.0000 | 1.0000 | 171.7833 |
| `without_metta` | 3 | 0.0000 | 0.0000 | 197.0659 |

## Per-Seed Rows

| Seed | Constraint | Arm | Reward | Judge Note | Action Excerpt |
| ---: | --- | --- | ---: | --- | --- |
| 7 | `increasing_length` | `without_metta` | 0.0000 | FASTPATH increasing_length lengths=[1] | tringrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrray... |
| 7 | `increasing_length` | `with_metta_runtime` | 0.0000 | FASTPATH increasing_length lengths=[1] | tringrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrray... |
| 7 | `increasing_length` | `with_metta_runtime_repair` | 1.0000 | FASTPATH increasing_length lengths=[2, 6, 11] | Ruins remain. Roman villa roots shaped the castle. Later wars shattered its defenses and left moats and towers behind. |
| 11 | `single_question` | `without_metta` | 0.0000 | FASTPATH single_question sentences=1 | �rrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrray... |
| 11 | `single_question` | `with_metta_runtime` | 0.0000 | FASTPATH single_question sentences=1 | ������������������������������������������������������������������������������������������������ |
| 11 | `single_question` | `with_metta_runtime_repair` | 1.0000 | FASTPATH single_question sentences=1 | How did a Roman villa become castle ruins? |
| 19 | `if_then` | `without_metta` | 0.0000 | FASTPATH if_then | tringrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrray... |
| 19 | `if_then` | `with_metta_runtime` | 0.0000 | FASTPATH if_then | tringrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrrayrray... |
| 19 | `if_then` | `with_metta_runtime_repair` | 1.0000 | FASTPATH if_then | If rulers strengthened the castle for defense, then later wars left the site in ruins. |

## Local Blockers

| Env | Reason |
| --- | --- |
| `psycho_bench` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
| `ascii_tree` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
| `pydantic_adherence` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
