import argparse
import json
import random
from pathlib import Path

def generate_precision_examples(world_data):
    examples = []
    world_id = world_data.get("IFID", "unknown_world")
    
    # Primitives for compression/routing
    COMPRESSION_MODES = ["summary_atoms", "raw_snippet", "evidence_snippets"]
    
    # 1. Encounter-based routing
    for encounter in world_data.get("encounters", []):
        enc_id = encounter.get("id")
        title = encounter.get("title")
        text = encounter.get("text_script", {}).get("value", "")
        
        # Scenario: Need to know what happens in a specific scene
        examples.append({
            "messages": [
                {
                    "role": "user",
                    "content": f"TASK: 'What are the stakes in the {title}?'\nWORLD: '{world_id}'\nCONTEXT: {{\"focus\": \"plot_progression\", \"depth\": \"local\"}}"
                },
                {
                    "role": "assistant",
                    "content": json.dumps({
                        "intent": "retrieve",
                        "source": "encounter_index",
                        "keys": [enc_id],
                        "compression": random.choice(COMPRESSION_MODES),
                        "escalate": False
                    })
                }
            ]
        })

    # 2. Character-based routing
    for char in world_data.get("characters", []):
        char_id = char.get("id")
        name = char.get("name")
        
        examples.append({
            "messages": [
                {
                    "role": "user",
                    "content": f"TASK: 'How does {name} feel about the current law?'\nWORLD: '{world_id}'\nCONTEXT: {{\"focus\": \"relationships\", \"character_id\": \"{char_id}\"}}"
                },
                {
                    "role": "assistant",
                    "content": json.dumps({
                        "intent": "retrieve",
                        "source": "character_state",
                        "keys": [char_id, "world_bible_laws"],
                        "query_type": "disposition",
                        "compression": "evidence_snippets",
                        "escalate": False
                    })
                }
            ]
        })

    # 3. Escalation examples (when query is outside index)
    examples.append({
        "messages": [
            {
                "role": "user",
                "content": f"TASK: 'Write a poem about the ash fields.'\nWORLD: '{world_id}'\nCONTEXT: {{\"focus\": \"creative_writing\"}}"
            },
            {
                "role": "assistant",
                "content": json.dumps({
                    "intent": "escalate",
                    "reason": "out_of_index_creative_task",
                    "confidence": 0.95,
                    "escalate": True
                })
            }
        ]
    })

    return examples

def main():
    parser = argparse.ArgumentParser(description="Build a high-precision TRM routing corpus.")
    parser.add_argument("--world-json", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.world_json, 'r', encoding='utf-8') as f:
        world_data = json.load(f)

    examples = generate_precision_examples(world_data)
    random.shuffle(examples)

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    print(f"Generated {len(examples)} precision routing examples -> {output_path}")

if __name__ == "__main__":
    main()
