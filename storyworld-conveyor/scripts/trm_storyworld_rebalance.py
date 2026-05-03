#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storyworld_conveyor.factory import load_factory_config  # noqa: E402
from storyworld_conveyor.trm import StoryworldRebalanceAdvisorTRM, TRMContext  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a TRM rebalance packet and patched config for Macbeth loops.")
    parser.add_argument("--base-config", required=True)
    parser.add_argument("--factory-runs-root", required=True)
    parser.add_argument("--log-root", required=True)
    parser.add_argument("--out-advice", required=True)
    parser.add_argument("--out-config", required=True)
    parser.add_argument("--task", default="Rebalance Macbeth ending topology using historical factory and loop data.")
    parser.add_argument("--target-ending-id", action="append", dest="target_ending_ids", default=None)
    args = parser.parse_args()

    config = load_factory_config(Path(args.base_config))
    context = TRMContext(
        task=args.task,
        artifacts=[args.base_config, args.factory_runs_root, args.log_root],
        metadata={"overlay_source": "hermes-trm-overlay", "mode": "storyworld_rebalance"},
    )
    advisor = StoryworldRebalanceAdvisorTRM()
    result = advisor.run(
        context,
        config=config,
        factory_runs_root=args.factory_runs_root,
        log_root=args.log_root,
        target_ending_ids=args.target_ending_ids,
    )

    out_advice = Path(args.out_advice)
    out_config = Path(args.out_config)
    out_advice.parent.mkdir(parents=True, exist_ok=True)
    out_config.parent.mkdir(parents=True, exist_ok=True)

    advice_payload = {
        "tool": advisor.name,
        "action": result.action,
        "confidence": result.confidence,
        "notes": result.notes,
        "payload": result.payload,
    }
    out_advice.write_text(json.dumps(advice_payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    out_config.write_text(json.dumps(result.payload["patched_config"], indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    print(out_advice)
    print(out_config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
