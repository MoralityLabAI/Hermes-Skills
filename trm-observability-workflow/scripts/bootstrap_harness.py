from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "references" / "snapshot_manifest.json"


def main() -> None:
    harness_root = os.environ.get("TRM_HARNESS_ROOT", "").strip()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    print(f"TRM_HARNESS_ROOT={harness_root or '<unset>'}")
    print(f"snapshot_root={manifest['snapshot_root']}")
    print("next_steps:")
    print("  - verify the harness root has scripts/run_eval.py and scripts/build_trm_train_rows.py")
    print("  - point the teacher collector at the chosen env config")
    print("  - summarize the replay JSONL before training")


if __name__ == "__main__":
    main()
