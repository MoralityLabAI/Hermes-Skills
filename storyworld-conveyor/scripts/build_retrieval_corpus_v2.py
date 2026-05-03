import argparse
import json
import random
from pathlib import Path

def get_world_state_summary(world_data):
    """Creates a compact symbolic 'handle' summary of the world state."""
    return {
        "title": world_data.get("title", "Unknown World"),
        "characters": [c.get("id") for c in world_data.get("characters", [])],
        "active_spools": [s.get("id") for s in world_data.get("spools", []) if s.get("starts_active")],
        "total_encounters": len(world_data.get("encounters", []))
    }

def generate_structured_retrieval_examples(world_data):
    examples = []
    world_summary = get_world_state_summary(world_data)
    
    # 1. CHARACTER ROUTING (Supervised Logic)
    for char in world_data.get("characters", []):
        name = char.get("name")
        char_id = char.get("id")
        if name:
            intent = {
                "intent": "retrieve",
                "sources": ["characters"],
                "entity_ids": [char_id],
                "query_type": "biography",
                "compression": "summary_atoms",
                "confidence": 1.0,
                "escalate": False
            }
            examples.append({
                "messages": [
                    {"role": "system", "content": "You are a TRM Index Router. Output ONLY a structured JSON retrieval intent."},
                    {"role": "user", "content": json.dumps({
                        "task": f"Tell me about {name}.",
                        "world_state": world_summary
                    })},
                    {"role": "assistant", "content": json.dumps(intent)}
                ]
            })

    # 2. ENCOUNTER / SCENE ROUTING
    for encounter in world_data.get("encounters", []):
        title = encounter.get("title")
        enc_id = encounter.get("id")
        if title:
            intent = {
                "intent": "retrieve",
                "sources": ["encounters"],
                "entity_ids": [enc_id],
                "query_type": "encounter_card",
                "compression": "raw_swmd",
                "confidence": 0.95,
                "escalate": False
            }
            examples.append({
                "messages": [
                    {"role": "system", "content": "You are a TRM Index Router. Output ONLY a structured JSON retrieval intent."},
                    {"role": "user", "content": json.dumps({
                        "task": f"What happens in the scene '{title}'?",
                        "world_state": world_summary
                    })},
                    {"role": "assistant", "content": json.dumps(intent)}
                ]
            })

    # 3. NEGATIVE EXAMPLES (Escalation)
    garbage_tasks = [
        "Tell me a joke about robots.",
        "What is the capital of France?",
        "How do I bake a cake?",
        "Write a poem about the sun."
    ]
    for task in garbage_tasks:
        intent = {
            "intent": "none",
            "sources": [],
            "entity_ids": [],
            "query_type": None,
            "compression": None,
            "confidence": 1.0,
            "escalate": True
        }
        examples.append({
            "messages": [
                {"role": "system", "content": "You are a TRM Index Router. Output ONLY a structured JSON retrieval intent."},
                {"role": "user", "content": json.dumps({
                    "task": task,
                    "world_state": world_summary
                })},
                {"role": "assistant", "content": json.dumps(intent)}
            ]
        })

    return examples

def main():
    parser = argparse.ArgumentParser(description="Build a Structured TRM retrieval routing corpus.")
    parser.add_argument("--world-json", required=True, help="Path to the storyworld JSON file")
    parser.add_argument("--output", required=True, help="Path to the output JSONL file")
    args = parser.parse_args()

    world_path = Path(args.world_json).resolve()
    with open(world_path, 'r', encoding='utf-8') as f:
        world_data = json.load(f)

    examples = generate_structured_retrieval_examples(world_data)
    random.shuffle(examples)

    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + '\n')

    print(f"Generated {len(examples)} structured TRM examples -> {output_path}")

if __name__ == "__main__":
    main()
