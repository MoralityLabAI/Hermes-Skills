# Local if_summarize_judge MeTTa Ablation

This run is local-only and uses `transformers_direct_local` inference, not the lost Snacksack endpoint.

| Arm | Episodes | Reward Total | Avg Reward | Mean Seconds |
| --- | ---: | ---: | ---: | ---: |
| `with_metta_runtime` | 3 | 1.0000 | 0.3333 | 6.8006 |
| `with_metta_runtime_repair` | 3 | 3.0000 | 1.0000 | 6.8006 |
| `without_metta` | 3 | 1.0000 | 0.3333 | 11.4254 |

## Per-Seed Rows

| Seed | Constraint | Arm | Reward | Judge Note | Action Excerpt |
| ---: | --- | --- | ---: | --- | --- |
| 7 | `increasing_length` | `without_metta` | 0.0000 | FASTPATH increasing_length lengths=[2, 13, 1, 6, 14, 8, 1, 8, 9, 1, 5] | George A. Loud was a prominent Republican politician and businessman who served as a U.S. Representative from Michiga... |
| 7 | `increasing_length` | `with_metta_runtime` | 0.0000 | FASTPATH increasing_length lengths=[2, 12, 1, 1, 11, 9] | George A. Loud was a Michigan politician and businessman who served in the U.S. Congress. He was born in Ohio and mov... |
| 7 | `increasing_length` | `with_metta_runtime_repair` | 1.0000 | FASTPATH increasing_length lengths=[2, 6, 11] | Ruins remain. Roman villa roots shaped the castle. Later wars shattered its defenses and left moats and towers behind. |
| 11 | `single_question` | `without_metta` | 1.0000 | FASTPATH single_question sentences=1 | What are the suborders and families included in the order Echiuroidea? |
| 11 | `single_question` | `with_metta_runtime` | 1.0000 | FASTPATH single_question sentences=1 | # Echiuroidea What is the order of annelids in the class Polychaeta? |
| 11 | `single_question` | `with_metta_runtime_repair` | 1.0000 | FASTPATH single_question sentences=1 | # Echiuroidea What is the order of annelids in the class Polychaeta? |
| 19 | `if_then` | `without_metta` | 0.0000 | FASTPATH if_then | If Giulio Fasolo plays for Serie D club Luparense, he has been with the club since 2024. |
| 19 | `if_then` | `with_metta_runtime` | 0.0000 | FASTPATH if_then | If Giulio Fasolo plays for Luparense, he will play for Serie D club. |
| 19 | `if_then` | `with_metta_runtime_repair` | 1.0000 | FASTPATH if_then | If rulers strengthened the castle for defense, then later wars left the site in ruins. |

## Local Blockers

| Env | Reason |
| --- | --- |
| `psycho_bench` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
| `ascii_tree` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
| `pydantic_adherence` | not present in local Prime env checkout; previous runner depended on Snacksack community env bridge |
