import argparse
import json
import random
from pathlib import Path

def generate_structured_retrieval_examples(world_data):
    examples = []
    
    # 1. CHARACTER MOTIVATION ROUTING
    for char in world_data.get("characters", []):
        name = char.get("name")
        char_id = char.get("id")
        if name:
            examples.append({
                "messages": [
                    {"role": "system", "content": "You are a TRM Index Router. Output ONLY a structured JSON retrieval action."},
                    {"role": "user", "content": f"What is {name}'s underlying motivation right now?"},
                    {"role": "assistant", "content": json.dumps({
                        "intent": "retrieve",
                        "sources": ["character_lore", "personality_matrix"],
                        "entity_ids": [char_id],
                        "query_type": "motivation_state",
                        "depth": 1,
                        "compression": "summary_atoms"
                    })}
                ]
            })

    # 2. LEGAL/LORE PRECEDENT ROUTING
    # Assuming 'encounters' often contain legal/social conflict
    for encounter in world_data.get("encounters", []):
        title = encounter.get("title")
        enc_id = encounter.get("id")
        if "Trial" in title or "Law" in title or "Charter" in title:
            examples.append({
                "messages": [
                    {"role": "system", "content": "You are a TRM Index Router. Output ONLY a structured JSON retrieval action."},
                    {"role": "user", "content": f"I need the legal context for the events in {title}."},
                    {"role": "assistant", "content": json.dumps({
                        "intent": "retrieve",
                        "sources": ["world_bible", "legal_code"],
                        "entity_ids": [enc_id, "charter_record"],
                        "query_type": "precedent_lookup",
                        "hop_plan": ["node_requirements", "historical_context"],
                        "escalate": False
                    })}
                ]
            })

    # 3. STATE-BASED CONSEQUENCE ROUTING
    for spool in world_data.get("spools", []):
        name = spool.get("spool_name")
        spool_id = spool.get("id")
        if name:
            examples.append({
                "messages": [
                    {"role": "system", "content": "You are a TRM Index Router. Output ONLY a structured JSON retrieval action."},
                    {"role": "user", "content": f"Predict the impact of the current state on {name}."},
                    {"role": "assistant", "content": json.dumps({
                        "intent": "analyze_state",
                        "sources": ["current_variables", "spool_logic"],
                        "entity_ids": [spool_id],
                        "query_type": "consequence_projection",
                        "confidence": 0.92
                    })}
                ]
            })

    return examples

def main():
    parser = argparse.ArgumentParser(description="Build a Structured TRM retrieval corpus.")
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

    print(f"Generated {len(examples)} Structured TRM examples -> {output_path}")

if __name__ == "__main__":
    main()
