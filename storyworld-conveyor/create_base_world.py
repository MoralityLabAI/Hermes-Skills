#!/usr/bin/env python3
import json
import os

base_world = {
    "title": "The Usual Suspects: Criminal Masterminds",
    "about": "A complex puzzle of criminal masterminds and deception",
    "motif": "noir, deception, mystery",
    "theme": "outsmarting the system",
    "genre": "noir, crime, mystery",
    "question": "What really happened at the docks that night?",
    "description": "In a shadowy world of criminals and deception, a mastermind manipulates events from the shadows. Players must navigate lies, alliances, and double-crosses to uncover the truth behind a mysterious crime syndicate.",
    "chars": [
        {
            "id": "keyser_soze", 
            "name": "Keyser Söze", 
            "role": "The mythical crime lord",
            "teaser": "A whisper, a shadow, an urban legend"
        },
        {
            "id": "verbal_kint", 
            "name": "Verbal Kint", 
            "role": "The crippled con artist",
            "teaser": "The small-time crook with a story to tell"
        },
        {
            "id": "mcmanus", 
            "name": "Agent McManus", 
            "role": "The persistent detective",
            "teaser": "Someone knows more than they let on"
        }
    ],
    "encounters": [
        {
            "id": "police_interrogation",
            "title": "The Police Interrogation Room",
            "description": "You sit across from Agent McManus as the lights flicker. The smell of stale coffee fills the room. Your story could set you free... or condemn you to a life behind bars."
        }
    ],
    "worldpedia": {
        "docks": "A decrepit pier where shady deals go down",
        "lineup": "The infamous police lineup of the usual suspects",
        "keyser_söze": "The mythical crime lord everyone fears but no one has seen",
        "redfoot": "A notoriously lax prison"
    }
}

output_file = '/mnt/c/projects/GPTStoryworld/hermes-skills/storyworld-conveyor/working_worlds/the_usual_suspects_base.json'

with open(output_file, 'w') as f:
    json.dump(base_world, f, indent=2)

print("Base world created successfully!")

# Validate the world
print("Validating...")
try:
    with open(output_file, 'r') as f:
        json.load(f)
    print("Validation successful - JSON is valid!")
except Exception as e:
    print(f"Validation failed: {e}")
    print("Content of the file:")
    with open(output_file, 'r') as f:
        print(f.read())
EOF; __hermes_rc=$?; printf '__HERMES_FENCE_a9f7b3__'; exit $__hermes_rc
