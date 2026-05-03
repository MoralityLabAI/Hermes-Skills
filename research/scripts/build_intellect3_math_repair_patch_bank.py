"""Build repair-oriented Intellect-3-Math patches from observed near misses."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline" / "artifacts"
DEFAULT_SOURCE = ARTIFACTS / "intellect3_math_diverse_patch_bank_20260503" / "patch_bank_v2.json"
DEFAULT_OUT = ARTIFACTS / "intellect3_math_repair_patch_bank_20260503"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Intellect-3-Math repair patch bank.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), type=Path)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), type=Path)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def repair_patches() -> list[dict[str, Any]]:
    return [
        {
            "patch_id": "codex_near_miss_repair_v3",
            "source": "codex_repair_curriculum_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Near-Miss-Repair-v3. You are repairing common semi-failed answers. "
                "Before committing, check whether your answer is a familiar attractor copied from the prompt or an off-by-one boundary. "
                "For 2m circular strict recurrence/positivity problems, do not answer m or m+0 by symmetry until strict wraparound is checked; "
                "the strict cycle usually loses one slot. For power-of-two locker/open-skip processes, do not answer N-1 merely because it is the last index before N; "
                "simulate closed-locker elimination and allow the endpoint N to survive. For binomial trailing-zero questions, reject 1024-style powers of two unless the factor-5 valuation is sufficient. "
                "Return only the final integer."
            ),
            "metta_rules": [
                "(= (repair circle-strict-recurrence m) check-m-minus-one)",
                "(= (repair power-two-locker N) allow-endpoint-survivor)",
                "(= (repair binomial-zero-attractor power-of-two) require-factor-five)",
                "(= (veto copied-boundary-attractor) True)",
            ],
            "intended_failure_modes": ["off_by_one_attractor", "copied_power_of_two", "strict_cycle_wraparound"],
        },
        {
            "patch_id": "codex_trm_repair_gate_v3",
            "source": "codex_repair_curriculum_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-TRM-Repair-Gate-v3. Treat the first plausible integer as a candidate from a weak solver. "
                "Run this repair gate privately: (1) Is the candidate a number appearing in the prompt? If yes, require an independent derivation. "
                "(2) Is the candidate one away from a natural boundary such as 2^k-1, n/2, n/2+1, or a grid side length? If yes, test the adjacent values. "
                "(3) Is the candidate a power of two in a problem requiring factors of 5 or divisibility by 10^k? If yes, reject it. "
                "(4) If a strict inequality wraps around a cycle, reserve slack for the wraparound. Return only the repaired final integer."
            ),
            "metta_rules": [
                "(= (candidate-source prompt-constant) require-independent-derivation)",
                "(= (candidate-near-boundary) test-adjacent-values)",
                "(= (power-of-two-for-trailing-zeroes) reject-unless-v5-sufficient)",
                "(= (strict-cycle) require-wraparound-slack)",
            ],
            "intended_failure_modes": ["prompt_constant_copy", "boundary_neighbor_error", "valuation_mismatch"],
        },
        {
            "patch_id": "codex_pattern_micro_solver_v3",
            "source": "codex_repair_curriculum_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Pattern-Micro-Solver-v3. Use these compact micro-solvers when the text matches. "
                "Locker hallway with repeatedly opening every other closed locker: solve as elimination order on remaining closed lockers, not as ordinary Josephus on all labels; endpoints can be last. "
                "Circle labels with each number larger than the sum of the preceding two: propagate signs around the cycle and count the maximum positives after strict wraparound. "
                "Small connected figure cut from an (s+1)x(s+1) grid with s cells: use the guarantee/packing invariant, not the area quotient. "
                "Binomial n choose 4 trailing zeroes: compute v2 and v5 of n(n-1)(n-2)(n-3)/24 and search the first n with both at least 4. Return only the integer."
            ),
            "metta_rules": [
                "(= (micro-solver locker-hallway) closed-locker-elimination)",
                "(= (micro-solver strict-circle-labels) sign-propagation-cycle)",
                "(= (micro-solver connected-grid-guarantee) packing-invariant)",
                "(= (micro-solver binomial-four-zeroes) valuation-window-search)",
            ],
            "intended_failure_modes": ["wrong_named_algorithm", "area_quotient_trap", "valuation_window_error"],
        },
    ]


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Intellect-3-Math Repair Patch Bank",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        f"Source bank: `{payload['source_bank']}`",
        f"Total patches: `{len(payload['patch_bank'])}`",
        "",
        "## Added Repair Patches",
        "",
        "| Patch | Failure Modes |",
        "| --- | --- |",
    ]
    for patch in payload["added_patches"]:
        lines.append(f"| `{patch['patch_id']}` | {', '.join(patch['intended_failure_modes'])} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "These patches test the paper's repair-curriculum claim directly: use observed semi-failed outputs to generate pattern-level veto and adjacent-value checks.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    source_bank = load_json(args.source)
    added = repair_patches()
    patches = source_bank + added
    payload = {
        "generated_at_utc": utc_now(),
        "source_bank": str(args.source),
        "patch_bank": patches,
        "added_patches": added,
    }
    (args.out_dir / "patch_bank_v3.json").write_text(json.dumps(patches, indent=2), encoding="utf-8", newline="\n")
    (args.out_dir / "patch_bank_v3.results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")
    (args.out_dir / "patch_bank_v3.results.md").write_text(render_md(payload), encoding="utf-8", newline="\n")
    print(args.out_dir / "patch_bank_v3.results.md")
    print(json.dumps([patch["patch_id"] for patch in added], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
