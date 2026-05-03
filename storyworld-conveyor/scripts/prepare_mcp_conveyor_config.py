from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict


SKILL_ROOT = Path(__file__).resolve().parents[1]
HERMES_REPO_ROOT = Path(__file__).resolve().parents[2]


def _find_storyworld_repo_root() -> Path:
    candidates = []
    env_root = str(__import__("os").environ.get("GPTSTORYWORLD_ROOT", "") or "").strip()
    if env_root:
        candidates.append(Path(env_root))
    candidates.extend([HERMES_REPO_ROOT, Path(r"C:\projects\GPTStoryworld")])
    for root in candidates:
        tool = root / "codex-skills" / "storyworld-building" / "scripts" / "json_to_swmd.py"
        if tool.exists():
            return root.resolve()
    return HERMES_REPO_ROOT.resolve()


STORYWORLD_REPO_ROOT = _find_storyworld_repo_root()
JSON_TO_SWMD = STORYWORLD_REPO_ROOT / "codex-skills" / "storyworld-building" / "scripts" / "json_to_swmd.py"


def _default_run_id(source: Path) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in source.stem).strip("_")
    return f"{safe[:60]}_mcp_conveyor_{int(time.time())}"


def _resolve_python(value: str) -> str:
    return str(Path(value).resolve()) if value else sys.executable


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


def _prepare_swmd(source: Path, out_dir: Path, python_bin: str) -> Path:
    suffix = source.suffix.lower()
    if suffix in {".md", ".swmd"} or source.name.endswith(".swmd.min.md"):
        return source.resolve()
    if suffix != ".json":
        raise ValueError(f"unsupported storyworld source extension: {source.suffix}")
    out_path = out_dir / f"{source.stem}.swmd.min.md"
    cmd = [python_bin, str(JSON_TO_SWMD), str(source.resolve()), str(out_path), "--mode", "minified"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "json_to_swmd conversion failed").strip())
    return out_path.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare an MCP-default Hermes storyworld conveyor config from JSON or SWMD-min."
    )
    parser.add_argument("--storyworld", required=True, help="Input SweepWeave JSON or SWMD-min path.")
    parser.add_argument("--out-config", required=True, help="Output small-model port config JSON.")
    parser.add_argument(
        "--artifact-root",
        default=str(SKILL_ROOT / "context_port_runs"),
    )
    parser.add_argument("--run-id", default="")
    parser.add_argument("--python-bin", default="")
    parser.add_argument("--model-path", default="")
    parser.add_argument("--adapter-path", default="")
    parser.add_argument("--trm-advice-json", default="")
    parser.add_argument("--qlora-examples-jsonl", default="")
    parser.add_argument("--world-json", default="", help="Optional original JSON path for operation fallback.")
    parser.add_argument("--max-encounters", type=int, default=12)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--neighbor-hops", type=int, default=1)
    parser.add_argument("--context-budget-tokens", type=int, default=6144)
    parser.add_argument("--reserve-output-tokens", type=int, default=768)
    parser.add_argument("--planning-card-tokens", type=int, default=700)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--max-input-output-ratio", type=float, default=24.0)
    parser.add_argument("--phases", default="plan,characterize,encounter_build,act_complete")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--fewshot-count", type=int, default=0)
    parser.add_argument("--repair-mode", default="phase_then_operation_fallback")
    parser.add_argument("--repair-build-output", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    source = Path(args.storyworld).resolve()
    if not source.exists():
        raise FileNotFoundError(str(source))
    out_config = Path(args.out_config).resolve()
    run_id = args.run_id or _default_run_id(source)
    python_bin = _resolve_python(args.python_bin)
    swmd_dir = out_config.parent / "mcp_sources" / run_id
    swmd_path = _prepare_swmd(source, swmd_dir, python_bin)

    model_path = args.model_path.strip()
    if not model_path:
        model_path = (
            r"D:\Research_Engine\Qwen_Storyworld\cache\models--Qwen--Qwen2.5-3B-Instruct"
            r"\snapshots\aa8e72537993ba99e69dfaafa59ed015b17504d1"
        )

    world_json = args.world_json.strip()
    if not world_json and source.suffix.lower() == ".json":
        world_json = str(source)

    config: Dict[str, Any] = {
        "artifact_root": str(Path(args.artifact_root).resolve()),
        "run_id": run_id,
        "python_bin": python_bin,
        "swmd": str(swmd_path),
        "world_json": str(Path(world_json).resolve()) if world_json else "",
        "model_path": str(Path(model_path).resolve()),
        "adapter_path": str(Path(args.adapter_path).resolve()) if args.adapter_path else "",
        "trm_advice_json": str(Path(args.trm_advice_json).resolve()) if args.trm_advice_json else "",
        "qlora_examples_jsonl": str(Path(args.qlora_examples_jsonl).resolve()) if args.qlora_examples_jsonl else "",
        "phases": args.phases,
        "max_encounters": int(args.max_encounters),
        "start_index": int(args.start_index),
        "neighbor_hops": int(args.neighbor_hops),
        "context_budget_tokens": int(args.context_budget_tokens),
        "reserve_output_tokens": int(args.reserve_output_tokens),
        "planning_card_tokens": int(args.planning_card_tokens),
        "max_new_tokens": int(args.max_new_tokens),
        "max_input_output_ratio": float(args.max_input_output_ratio),
        "temperature": float(args.temperature),
        "fewshot_count": int(args.fewshot_count),
        "repair_mode": args.repair_mode,
        "repair_build_output": bool(args.repair_build_output),
        "apply": bool(args.apply),
        "mcp_default": True,
        "mcp_budget_preflight": True,
        "allow_mcp_budget_overflow": False,
        "memory_mode": "encounter_packet_only",
        "prompt_policy": {
            "never_inline_full_storyworld_after_conversion": True,
            "packet_contract": "world_card + target encounter + neighbor encounters + TRM constraints + ledger summary",
            "abort_on_budget_overflow": True,
        },
        "hardware_profile": {
            "gpu_vram_mb": 4000,
            "effective_model_budget_mb": 3900,
        },
    }

    _write_json(out_config, config)
    print(str(out_config))
    print(str(swmd_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
