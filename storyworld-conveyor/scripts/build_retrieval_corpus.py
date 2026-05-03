import argparse
import json
import random
from pathlib import Path

def generate_structured_retrieval_examples(world_data):
    examples = []
    
    # Primitives for the TRM to use
    namespaces = ["lore", "characters", "encounters", "history", "mechanics"]
    compression_levels = ["full", "summary_atoms", "evidence_snippets"]

    # 1. Character Retrieval with "Search Policy"
    for char in world_data.get("characters", []):
        name = char.get("name")
        char_id = char.get("id")
        if name:
            examples.append({
                "messages": [
                    {"role": "system", "content": "You are a TRM Search Policy Router. Emit a compact JSON retrieval plan."},
                    {"role": "user", "content": f"Context: Scene start. Active: [{name}].\nQuery: 'Give me the background on {name}.'"},
                    {"role": "assistant", "content": json.dumps({
                        "intent": "retrieve",
                        "sources": ["characters"],
                        "entity_ids": [char_id],
                        "query_type": "biography",
                        "compression": "summary_atoms",
                        "confidence": 0.95
                    })}
                ]
            })

    # 2. Encounter Retrieval with "Hop Planning"
    for encounter in world_data.get("encounters", []):
        title = encounter.get("title")
        enc_id = encounter.get("id")
        if title:
            examples.append({
                "messages": [
                    {"role": "system", "content": "You are a TRM Search Policy Router. Emit a compact JSON retrieval plan."},
                    {"role": "user", "content": f"Context: Previous node complete. Decision pending.\nTask: 'Load the branching logic for {title}.'"},
                    {"role": "assistant", "content": json.dumps({
                        "intent": "retrieve",
                        "sources": ["encounters"],
                        "entity_ids": [enc_id],
                        "query_type": "branching_logic",
                        "compression": "full",
                        "confidence": 0.98
                    })}
                ]
            })

    # 3. Multi-source Retrieval (Lore + History)
    title = world_data.get("title", "this world")
    examples.append({
        "messages": [
            {"role": "system", "content": "You are a TRM Search Policy Router. Emit a compact JSON retrieval plan."},
            {"role": "user", "content": f"Query: 'What are the founding myths of {title}?'"},
            {"role": "assistant", "content": json.dumps({
                "intent": "retrieve",
                "sources": ["lore", "history"],
                "query_type": "founding_myths",
                "compression": "evidence_snippets",
                "confidence": 0.92
            })}
        ]
    })

    return examples

def main():
    parser = argparse.ArgumentParser(description="Build a Structured TRM Search Policy corpus.")
    parser.add_argument("--world-json", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.world_json, 'r', encoding='utf-8') as f:
        world_data = json.load(f)

    examples = generate_structured_retrieval_examples(world_data)
    random.shuffle(examples)

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    print(f"Generated {len(examples)} Structured Search Policy examples -> {output_path}")

if __name__ == "__main__":
    main()
