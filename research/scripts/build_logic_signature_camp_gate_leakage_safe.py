"""Build the leakage-safe logic signature camp-gate study."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import logic_signature_camp_gate_core as core  # noqa: E402


STUDY = ROOT / "research" / "studies" / "2026-04-29-logic-signature-camp-gate-leakage-safe"
ROWS_DIR = STUDY / "rows"
VALIDATORS_DIR = STUDY / "validators"
CONFIGS_DIR = STUDY / "configs"
RESULTS_DIR = STUDY / "results"

ROWS_PATH = ROWS_DIR / "logic_signature_camp_gate_rows.jsonl"
VALIDATOR_PATH = VALIDATORS_DIR / "validate_logic_signature_camp_gate.py"
CONFIG_PATH = CONFIGS_DIR / "logic_signature_camp_gate_suite.json"
TIER_RESULTS_DIR = RESULTS_DIR / "proposal_tier_smoke"
TIER_CANDIDATES_PATH = TIER_RESULTS_DIR / "proposal_tier_candidates.jsonl"
TIER_RESULTS_JSON = TIER_RESULTS_DIR / "proposal_tier_smoke.results.json"
TIER_RESULTS_MD = TIER_RESULTS_DIR / "proposal_tier_smoke.results.md"
LOCAL_RESULTS_DIR = RESULTS_DIR / "local_qwen25_3b_logic_signature_camp_gate"
LOCAL_RESULTS_JSON = LOCAL_RESULTS_DIR / "local_qwen25_3b_logic_signature_camp_gate.results.json"
LOCAL_JOBCAP_SUMMARY = LOCAL_RESULTS_DIR / "jobcap.summary.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def family_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = f"{row['validator']['height']}x{row['validator']['width']}"
        counts[key] = counts.get(key, 0) + 1
    return counts


def local_summary_context() -> dict[str, Any] | None:
    if not LOCAL_RESULTS_JSON.exists() or not LOCAL_JOBCAP_SUMMARY.exists():
        return None
    return {
        "result": json.loads(LOCAL_RESULTS_JSON.read_text(encoding="utf-8-sig")),
        "jobcap": json.loads(LOCAL_JOBCAP_SUMMARY.read_text(encoding="utf-8-sig")),
    }


def arm_table(summary: dict[str, Any], arm_order: list[str]) -> str:
    rows: list[str] = []
    for arm in arm_order:
        if arm not in summary["arms"]:
            continue
        metrics = summary["arms"][arm]
        rows.append(
            "| `{}` | {}/{} | {:.4f} | {}/{} | {:.4f} | {} |".format(
                arm,
                metrics["exact_success"],
                metrics["rows"],
                metrics["exact_rate"],
                metrics["contract_valid"],
                metrics["rows"],
                metrics["avg_cell_accuracy"],
                ", ".join(f"{key}:{value}" for key, value in sorted(metrics["proposal_tier_counts"].items())),
            )
        )
    return "\n".join(rows)


def write_docs(rows: list[dict[str, Any]]) -> None:
    generated_at = utc_now()
    counts = family_counts(rows)
    counts_table = "\n".join(f"| `{shape}` | {count} |" for shape, count in sorted(counts.items()))
    local = local_summary_context()

    if local:
        result = local["result"]
        jobcap = local["jobcap"]
        local_section = f"""## Local 3B Result

The local Qwen2.5-3B Q4 run completed under the Windows job-cap wrapper with a {jobcap['caps']['ram_mb']:,} MB RAM cap, {jobcap['caps']['cpu_pct']}% CPU cap, {jobcap['caps']['io_mb_s']} MB/s IO cap, and {jobcap['caps']['timeout_sec']:,} second timeout. Runner-level child RSS peaked at `{result['summary'].get('peak_child_ram_mb', 0.0):.2f} MB`; the wrapper reported `{jobcap['status']}`.

| Arm | Exact | Exact Rate | Contract Valid | Avg Cell Acc | Tier Counts |
| --- | ---: | ---: | ---: | ---: | --- |
{arm_table(result['summary'], ['baseline', 'pure_trm', 'metta_runtime', 'metta_signature_projection'])}

Interpretation: the projection column is the key hard-env measurement. It tests whether local 3B emits enough verifier-visible grid state for prompt-derived signature projection to close the solution. It is not a trained TRM lift claim.
"""
        evidence = "`no_model_proposal_tier_smoke`, `live_model_local_3b`"
        allowed_live = "- Live local 3B rows can be reported because row IDs, validators, and a job-cap receipt are present."
        if "metta_signature_projection" in result["summary"]["arms"]:
            proj = result["summary"]["arms"]["metta_signature_projection"]
            metta = result["summary"]["arms"].get("metta_runtime", {})
            allowed_live += (
                f"\n- Prompt-derived MeTTa projection scored {proj['exact_success']}/{proj['rows']} exact "
                f"versus raw MeTTa runtime {metta.get('exact_success', 0)}/{metta.get('rows', 0)}."
            )
    else:
        local_section = """## Next Step

Run `research/scripts/run_logic_signature_camp_gate_local_3b.py` under the Windows job-cap wrapper. Preserve these rows and validators for 9B/27B scale comparisons.
"""
        evidence = "`no_model_proposal_tier_smoke`, pending `live_model_local_3b`"
        allowed_live = "- Live local 3B claims require result JSON plus a job-cap receipt."

    readme = f"""# Logic Signature Camp-Gate Leakage-Safe Micro-Suite

Generated: `{generated_at}`

- Route: `hard_env_boundary`
- Project: `logic_signature_camp_gate`
- Evidence classes: {evidence}
- Source menu: `research/generated/metta_project_menu.md`
- Circuit: `intellect3_logic_signature_circuit`

## Purpose

This study turns the prior Intellect-3 camp-gate replay into a leakage-safe micro-suite. The old replay projected against answer-derived signatures from existing receipts; this suite exposes only prompt-derived constraints and audits solver uniqueness before any score table.

## Public Constraint Surface

- Fixed `T` cells are listed in each prompt.
- Row and column `C` counts are listed in each prompt.
- Local adjacency rules define valid campsite grids.
- Target grids are absent from prompts and marked by SHA-256 for audit only.

## Shape Counts

| Grid Shape | Rows |
| --- | ---: |
{counts_table}

## Artifacts

- Rows: `rows/logic_signature_camp_gate_rows.jsonl`
- Validator: `validators/validate_logic_signature_camp_gate.py`
- Suite config: `configs/logic_signature_camp_gate_suite.json`
- Proposal-tier smoke: `results/proposal_tier_smoke/proposal_tier_smoke.results.md`
- Local 3B run: `results/local_qwen25_3b_logic_signature_camp_gate/local_qwen25_3b_logic_signature_camp_gate.results.md`
- Job-cap receipt: `results/local_qwen25_3b_logic_signature_camp_gate/jobcap.summary.json`

{local_section}
"""
    plan = f"""# Study Plan

## Hypothesis

MeTTa/TRM signature projection can amplify hard logic only when a small model emits enough verifier-visible grid state. The gain should appear in `metta_signature_projection`, not necessarily in raw `metta_runtime`.

## Arms

- `baseline`: direct grid answer.
- `pure_trm`: TRM-style contract parsing prompt.
- `metta_runtime`: MeTTa/TRM gate prompt without deterministic projection.
- `metta_signature_projection`: deterministic min-edit projection from the `metta_runtime` candidate to public prompt constraints.

## Metrics

- `exact_success`: grid matches the unique solver-derived target.
- `contract_valid`: grid satisfies public constraints.
- `avg_cell_accuracy`: cell-level agreement with the held-out target.
- `proposal_tier`: `none`, `weak_surface`, `partial_semantic`, or `full_candidate`.

## Promotion Rule

Promote as hard-env evidence only if projection improves exactness/cell accuracy and the audit shows `target_grid_in_prompt=false`, `projection_uses_target_grid=false`, and `unique_solution_from_prompt_constraints=true`.

## Stop Rule

If raw 3B outputs are mostly `none`, this lane needs a stronger model or a public-trace scaffold before projection can be meaningfully tested.
"""
    audit = f"""# Claim Audit

## Evidence Class

- `no_model_proposal_tier_smoke` verifies the validator and projection threshold behavior.
- `live_model_local_3b` applies the same frozen rows and validator to local 3B completions when result receipts exist.

## Allowed Claims

- The suite is leakage-safe with respect to target grids: prompts contain constraints but not answers.
- Prompt-derived signatures and adjacency rules are sufficient to solve each frozen micro-row uniquely.
- Projection may be described as symbolic closure over public constraints.
{allowed_live}

## Disallowed Claims

- Do not call projection success a latent-reasoning improvement.
- Do not compare this directly to the old 27B receipt replay without noting the old replay used answer-derived signatures.
- Do not claim trained TRM lift; this study tests runtime framing and deterministic MeTTa projection.
"""

    config = {
        "generated_at_utc": generated_at,
        "route_id": "hard_env_boundary",
        "project_id": "logic_signature_camp_gate",
        "row_count": len(rows),
        "shape_counts": counts,
        "validator": str(VALIDATOR_PATH.relative_to(ROOT)),
        "projection_inputs": ["candidate_grid", "fixed_t_cells", "row_c_counts", "col_c_counts", "adjacency_rules"],
        "projection_forbidden_inputs": ["canonical_output", "canonical_sha256", "expected_grid"],
        "recommended_caps": {
            "job_memory_limit_mb": 3000,
            "cpu_rate_percent": 50,
            "io_cap_mb_s": 50,
            "runner_child_rss_mb": 2600,
            "timeout_sec": 7200,
        },
    }

    STUDY.mkdir(parents=True, exist_ok=True)
    (STUDY / "README.md").write_text(readme.rstrip() + "\n", encoding="utf-8")
    (STUDY / "study_plan.md").write_text(plan.rstrip() + "\n", encoding="utf-8")
    (STUDY / "claim_audit.md").write_text(audit.rstrip() + "\n", encoding="utf-8")
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    rows = core.generate_rows(target_rows=12)
    for directory in (ROWS_DIR, VALIDATORS_DIR, CONFIGS_DIR, TIER_RESULTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    core.write_jsonl(ROWS_PATH, rows)
    shutil.copyfile(SCRIPT_DIR / "logic_signature_camp_gate_core.py", VALIDATOR_PATH)
    core.write_jsonl(TIER_CANDIDATES_PATH, core.canonical_tier_candidates(rows))
    write_docs(rows)
    subprocess.run(
        [
            sys.executable,
            str(VALIDATOR_PATH),
            "--rows",
            str(ROWS_PATH),
            "--candidates",
            str(TIER_CANDIDATES_PATH),
            "--out-json",
            str(TIER_RESULTS_JSON),
            "--out-md",
            str(TIER_RESULTS_MD),
            "--title",
            "Logic Signature Camp-Gate Proposal-Tier Smoke",
            "--evidence-class",
            "no_model_proposal_tier_smoke",
        ],
        check=True,
    )
    print(STUDY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
