"""Build a more diverse Intellect-3-Math patch bank.

The first patch bank mostly varied verifier language.  This bank keeps the
same controls but adds solver-procedure variants intended to produce different
candidate answers: table construction, backward constraints, theorem routing,
modular valuations, coordinate geometry, and finite casework.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "research" / "studies" / "2026-04-22-metta-trm-hermes-pipeline" / "artifacts"
DEFAULT_SOURCE = ARTIFACTS / "intellect3_math_skill_patch_gym_20260502" / "patch_bank.json"
DEFAULT_OUT = ARTIFACTS / "intellect3_math_diverse_patch_bank_20260503"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Intellect-3-Math diverse patch bank.")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), type=Path)
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT), type=Path)
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def diverse_patches() -> list[dict[str, Any]]:
    return [
        {
            "patch_id": "codex_metta_theorem_router_v2",
            "source": "codex_diversity_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-MeTTa-Theorem-Router-v2. Use private theorem routing before calculation. "
                "If the problem is a locker/open-skip process, model the survivor/elimination order on powers of two. "
                "If it is a binomial ending-in-zeros problem, compute p-adic valuations rather than expanding. "
                "If it is a circle/sequence sign constraint, reduce to recurrence or alternating-block feasibility. "
                "If it is a grid connected-polyomino guarantee, use coloring/packing lower and upper bounds. "
                "If it is orthogonal-diagonal geometry, introduce coordinates and ratio variables. Return only the final integer."
            ),
            "metta_rules": [
                "(= (route locker-skip-process) josephus-elimination-invariant)",
                "(= (route binomial-trailing-zeroes) p-adic-valuation-search)",
                "(= (route circle-recurrence-positivity) alternating-block-bound)",
                "(= (route connected-polyomino-guarantee) coloring-packing-bound)",
                "(= (route perpendicular-diagonals-geometry) coordinate-ratio-solve)",
            ],
            "intended_failure_modes": ["missing_known_invariant", "wrong_domain_route", "fast_guess"],
        },
        {
            "patch_id": "codex_finite_table_builder_v2",
            "source": "codex_diversity_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Finite-Table-Builder-v2. For finite processes, privately build the first "
                "small instances and infer the invariant only after the table is consistent. Use this for lockers, "
                "sequences, grids, games, maximum counts, and all-possible wording. Prefer a verified recurrence or "
                "period over a direct guess. Commit only the final requested integer."
            ),
            "metta_rules": [
                "(= (finite-process ?p) build-small-instance-table)",
                "(= (commit ?answer) (and (matches-small-cases ?answer) (matches-requested-form ?answer)))",
                "(= (veto ?answer) first-plausible-pattern-without-table)",
            ],
            "intended_failure_modes": ["pattern_without_small_cases", "off_by_one", "wrong_requested_quantity"],
        },
        {
            "patch_id": "codex_backward_constraint_solver_v2",
            "source": "codex_diversity_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Backward-Constraint-Solver-v2. Start from the requested final quantity and "
                "work backward through the constraints. For maximum/minimum questions, prove both a construction and "
                "a blocking bound. For expressions m+n or a+b+c, solve the components first, then combine. For large "
                "constants in the prompt, do not copy them; use them only as constraints. Return only the final integer."
            ),
            "metta_rules": [
                "(= (requested maximum) require-upper-bound-and-construction)",
                "(= (requested component-sum) solve-components-before-sum)",
                "(= (large-constant-in-prompt) constraint-not-answer)",
                "(= (commit ?answer) bound-and-construction-agree)",
            ],
            "intended_failure_modes": ["copied_prompt_constant", "missing_bound", "component_sum_error"],
        },
        {
            "patch_id": "codex_modular_valuation_solver_v2",
            "source": "codex_diversity_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Modular-Valuation-Solver-v2. For divisibility, last digits, trailing zeroes, "
                "large exponents, binomial coefficients, and modular constraints, use valuations and residues. For "
                "trailing zeroes require enough factors of both 2 and 5; search n by inequalities before testing nearby "
                "values. Avoid decimal expansion. Return only the final integer."
            ),
            "metta_rules": [
                "(= (trailing-zeroes ?k) require-min-v2-v5-at-least-k)",
                "(= (binomial-coefficient) use-factorial-valuation-differences)",
                "(= (large-exponent) reduce-by-modulus-or-period)",
                "(= (commit ?n) nearby-values-checked)",
            ],
            "intended_failure_modes": ["decimal_expansion_guess", "missing_factor_five", "modular_period_error"],
        },
        {
            "patch_id": "codex_coordinate_geometry_solver_v2",
            "source": "codex_diversity_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Coordinate-Geometry-Solver-v2. For geometry with perpendicular, parallel, "
                "diagonal, trapezoid, circle, or ratio language, privately assign coordinates and variables. Translate "
                "orthogonality into dot products or slope products, simplify ratios symbolically, and only then compute "
                "the requested integer such as m+n. Return only the final integer."
            ),
            "metta_rules": [
                "(= (parallel-perpendicular-geometry) coordinate-system)",
                "(= (orthogonal-lines) dot-product-zero)",
                "(= (ratio-expression) symbolic-ratio-before-number)",
                "(= (fraction-answer m/n) output-m-plus-n)",
            ],
            "intended_failure_modes": ["diagram_guess", "ratio_inversion", "fraction_component_error"],
        },
        {
            "patch_id": "codex_extremal_construction_solver_v2",
            "source": "codex_diversity_seed",
            "status": "candidate_pending_live_eval",
            "task_prefix": (
                "Hermes/Intellect-3-Math-Extremal-Construction-Solver-v2. For largest, smallest, maximal, minimal, "
                "guarantee, or determine wording, solve as an extremal proof. First find a construction achieving the "
                "candidate value, then find the obstruction that forbids one more or one less. Prefer invariant bounds "
                "such as parity, coloring, pigeonhole, recurrence sign, and divisibility. Return only the final integer."
            ),
            "metta_rules": [
                "(= (extremal-problem) construction-plus-obstruction)",
                "(= (guarantee-problem) adversarial-bound)",
                "(= (circle-sequence) recurrence-sign-bound)",
                "(= (grid-connected-figure) coloring-or-packing-bound)",
            ],
            "intended_failure_modes": ["one_sided_extremal_proof", "guarantee_misread", "off_by_one"],
        },
    ]


def render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Intellect-3-Math Diverse Patch Bank",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        f"Source bank: `{payload['source_bank']}`",
        f"Total patches: `{len(payload['patch_bank'])}`",
        "",
        "## Added Patches",
        "",
        "| Patch | Purpose |",
        "| --- | --- |",
    ]
    for patch in payload["added_patches"]:
        lines.append(f"| `{patch['patch_id']}` | {', '.join(patch['intended_failure_modes'])} |")
    lines.extend(
        [
            "",
            "## Read",
            "",
            "This bank tests whether solver-procedure diversity creates more row-level exact candidates than verifier-only prompt variants.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    source_bank = load_json(args.source)
    patches = source_bank + diverse_patches()
    payload = {
        "generated_at_utc": utc_now(),
        "source_bank": str(args.source),
        "patch_bank": patches,
        "added_patches": diverse_patches(),
    }
    (args.out_dir / "patch_bank_v2.json").write_text(json.dumps(patches, indent=2), encoding="utf-8", newline="\n")
    (args.out_dir / "patch_bank_v2.results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8", newline="\n")
    (args.out_dir / "patch_bank_v2.results.md").write_text(render_md(payload), encoding="utf-8", newline="\n")
    print(args.out_dir / "patch_bank_v2.results.md")
    print(json.dumps([patch["patch_id"] for patch in patches], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
