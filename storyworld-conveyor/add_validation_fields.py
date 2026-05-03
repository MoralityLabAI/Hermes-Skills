#!/usr/bin/env python3
import json
import sys

# Add missing fields to storyworld
def add_missing_fields(filename, verbose=False):
    try:
        text = open(filename, 'r').read()
        world = json.loads(text)
        
        # Add required fields only when missing
        world.setdefault("css_theme", "classic")
        world.setdefault("debug_mode", False)
        world.setdefault("display_mode", "desktop")
        world.setdefault("authored_properties", [])

        # Convert chars to characters format if needed
        if "characters" not in world and "chars" in world:
            world['characters'] = world['chars']
            del world['chars']

        # Add minimum authored properties structure
        existing_property_ids = {item.get("id") for item in world["authored_properties"] if isinstance(item, dict)}
        for char in world.get("characters", []):
            char_id = str(char.get("id")) if isinstance(char, dict) and char.get("id") is not None else ""
            if not char_id:
                continue
            prop_id = f"Embodiment_Virtuality_{char_id}"
            if prop_id in existing_property_ids:
                continue
            world["authored_properties"].append({
                "id": prop_id,
                "default_value": 0,
                "depth": 0,
                "affected_characters": [char_id],
            })
    
        # Write back
        with open(filename, 'w') as f:
            json.dump(world, f, indent=2)
            
        if verbose:
            print(f"Added missing fields to {filename}")
        return world
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_validation_fields.py <storyworld_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    success = add_missing_fields(filename, verbose=True)
    sys.exit(0 if success else 1)
