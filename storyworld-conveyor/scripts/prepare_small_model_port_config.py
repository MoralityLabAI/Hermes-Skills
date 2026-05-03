from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare a Hermes small-model context-port config after adapter training."
    )
    parser.add_argument("--base-config", required=True, help="Base JSON config path.")
    parser.add_argument("--out-config", required=True, help="Output JSON config path.")
    parser.add_argument("--adapter-path", default="", help="Trained adapter path to inject.")
    parser.add_argument("--trm-advice-json", default="", help="Optional TRM advice JSON path.")
    parser.add_argument("--run-id", default="", help="Optional run id override.")
    parser.add_argument("--apply", action="store_true", help="Enable in-place SWMD apply during the phase loop.")
    args = parser.parse_args()

    base_path = Path(args.base_config).resolve()
    out_path = Path(args.out_config).resolve()
    config = json.loads(base_path.read_text(encoding="utf-8"))

    if args.adapter_path:
        config["adapter_path"] = str(Path(args.adapter_path).resolve())
    if args.trm_advice_json:
        config["trm_advice_json"] = str(Path(args.trm_advice_json).resolve())
    if args.run_id:
        config["run_id"] = str(args.run_id)
    config["apply"] = bool(args.apply)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
