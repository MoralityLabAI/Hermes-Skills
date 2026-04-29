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
ABLATION_RESULTS_DIR = RESULTS_DIR / "projection_ablation"
ABLATION_RESULTS_JSON = ABLATION_RESULTS_DIR / "projection_ablation.results.json"
EXTRACT_RESULTS_DIR = RESULTS_DIR / "local_qwen25_3b_constraint_extract"
EXTRACT_RESULTS_JSON = EXTRACT_RESULTS_DIR / "local_qwen25_3b_constraint_extract.results.json"
EXTRACT_JOBCAP_SUMMARY = EXTRACT_RESULTS_DIR / "jobcap.summary.json"
EXTRACT_REPAIR_RESULTS_DIR = RESULTS_DIR / "constraint_extract_schema_repair"
EXTRACT_REPAIR_RESULTS_JSON = EXTRACT_REPAIR_RESULTS_DIR / "constraint_extract_schema_repair.results.json"
NOISY_ROWS_PATH = ROWS_DIR / "logic_signature_camp_gate_noisy_extract_rows.jsonl"
NOISY_CONFIG_PATH = CONFIGS_DIR / "logic_signature_noisy_extract_suite.json"
NOISY_EXTRACT_RESULTS_DIR = RESULTS_DIR / "local_qwen25_3b_noisy_graph_constraint_extract"
NOISY_EXTRACT_RESULTS_JSON = NOISY_EXTRACT_RESULTS_DIR / "local_qwen25_3b_constraint_extract.results.json"
NOISY_EXTRACT_JOBCAP_SUMMARY = NOISY_EXTRACT_RESULTS_DIR / "jobcap.summary.json"
GRAPH_ROUTER_RESULTS_DIR = RESULTS_DIR / "noisy_graph_router_script"
GRAPH_ROUTER_RESULTS_JSON = GRAPH_ROUTER_RESULTS_DIR / "noisy_graph_router.results.json"
GRAPH_ROUTER_CONTRACT = GRAPH_ROUTER_RESULTS_DIR / "camp_gate_graph_router_contract.metta"


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


def ablation_summary_context() -> dict[str, Any] | None:
    if not ABLATION_RESULTS_JSON.exists():
        return None
    return json.loads(ABLATION_RESULTS_JSON.read_text(encoding="utf-8-sig"))


def extract_summary_context() -> dict[str, Any] | None:
    if not EXTRACT_RESULTS_JSON.exists() or not EXTRACT_JOBCAP_SUMMARY.exists():
        return None
    return {
        "result": json.loads(EXTRACT_RESULTS_JSON.read_text(encoding="utf-8-sig")),
        "jobcap": json.loads(EXTRACT_JOBCAP_SUMMARY.read_text(encoding="utf-8-sig")),
    }


def extract_repair_summary_context() -> dict[str, Any] | None:
    if not EXTRACT_REPAIR_RESULTS_JSON.exists():
        return None
    return json.loads(EXTRACT_REPAIR_RESULTS_JSON.read_text(encoding="utf-8-sig"))


def noisy_extract_summary_context() -> dict[str, Any] | None:
    if not NOISY_EXTRACT_RESULTS_JSON.exists() or not NOISY_EXTRACT_JOBCAP_SUMMARY.exists():
        return None
    return {
        "result": json.loads(NOISY_EXTRACT_RESULTS_JSON.read_text(encoding="utf-8-sig")),
        "jobcap": json.loads(NOISY_EXTRACT_JOBCAP_SUMMARY.read_text(encoding="utf-8-sig")),
    }


def graph_router_summary_context() -> dict[str, Any] | None:
    if not GRAPH_ROUTER_RESULTS_JSON.exists():
        return None
    return json.loads(GRAPH_ROUTER_RESULTS_JSON.read_text(encoding="utf-8-sig"))


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
    ablation = ablation_summary_context()
    extract = extract_summary_context()
    extract_repair = extract_repair_summary_context()
    noisy_extract = noisy_extract_summary_context()
    graph_router = graph_router_summary_context()

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

    if ablation:
        ablation_section = f"""## Projection Ablation

The projection replay separates candidate-conditioned closure from pure public-constraint solving.

| Arm | Exact | Exact Rate | Contract Valid | Avg Cell Acc | Tier Counts |
| --- | ---: | ---: | ---: | ---: | --- |
{arm_table(ablation['summary'], ['metta_runtime', 'candidate_conditioned_projection', 'public_constraint_solver'])}

The `candidate_conditioned_projection` arm preserves the earlier 9/12 result. The `public_constraint_solver` arm reaches 12/12 because every frozen row has a unique solution from prompt-visible constraints. This is a stronger but narrower claim: once constraints are machine-visible, the LLM is not needed for grid execution.
"""
        allowed_live += "\n- Public-constraint solver replay scored 12/12 exact; report it as symbolic solver closure, not model lift."
    else:
        ablation_section = """## Projection Ablation

Pending: run `research/scripts/replay_logic_signature_camp_gate_public_solver.py` to separate candidate-conditioned projection from public-constraint solving.
"""

    if extract and extract_repair:
        extract_jobcap = extract["jobcap"]
        extract_result = extract["result"]
        repair_result = extract_repair
        extract_section = f"""## Constraint Extraction Follow-Up

The extraction run completed under the Windows job-cap wrapper with a {extract_jobcap['caps']['ram_mb']:,} MB RAM cap, {extract_jobcap['caps']['cpu_pct']}% CPU cap, {extract_jobcap['caps']['io_mb_s']} MB/s IO cap, and {extract_jobcap['caps']['timeout_sec']:,} second timeout. Runner-level child RSS peaked at `{extract_result['summary'].get('peak_child_ram_mb', 0.0):.2f} MB`; the wrapper reported `{extract_jobcap['status']}`.

| Arm | JSON Parse | Strict Packet Exact | Strict Solve Exact | Repair Packet Exact | Repair Solve Exact |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline_extract` | {repair_result['summary']['arms']['baseline_extract']['json_parse']}/12 | {repair_result['summary']['arms']['baseline_extract']['packet_exact']}/12 | {repair_result['summary']['arms']['baseline_extract']['solve_exact']}/12 | {repair_result['summary']['arms']['baseline_extract']['repair_packet_exact']}/12 | {repair_result['summary']['arms']['baseline_extract']['repair_solve_exact']}/12 |
| `metta_schema_extract` | {repair_result['summary']['arms']['metta_schema_extract']['json_parse']}/12 | {repair_result['summary']['arms']['metta_schema_extract']['packet_exact']}/12 | {repair_result['summary']['arms']['metta_schema_extract']['solve_exact']}/12 | {repair_result['summary']['arms']['metta_schema_extract']['repair_packet_exact']}/12 | {repair_result['summary']['arms']['metta_schema_extract']['repair_solve_exact']}/12 |

The strict `metta_schema_extract` packets failed because the model omitted `width` in all rows and had one row-count mass-balance error. Deterministic MeTTa-style schema repair inferred missing dimensions from count-vector lengths and accepted the unique row/column-balanced packet only when the public solver closed. This produced 12/12 repaired solve exact.
"""
        allowed_live += "\n- Constraint extraction plus deterministic schema repair scored 12/12 repaired solve exact for `metta_schema_extract`."
    else:
        extract_section = """## Constraint Extraction Follow-Up

Pending: run `research/scripts/run_logic_signature_constraint_extract_local_3b.py` and `research/scripts/replay_logic_signature_constraint_extract_repair.py`.
"""

    if noisy_extract:
        noisy_jobcap = noisy_extract["jobcap"]
        noisy_result = noisy_extract["result"]
        noisy_arms = noisy_result["summary"]["arms"]
        noisy_lines = []
        for arm in ("baseline_extract", "metta_schema_extract", "metta_graph_extract", "canonical_packet_solver"):
            if arm not in noisy_arms:
                continue
            metrics = noisy_arms[arm]
            noisy_lines.append(
                f"| `{arm}` | {metrics['json_parse']}/{metrics['rows']} | "
                f"{metrics['packet_exact']}/{metrics['rows']} | {metrics['solve_exact']}/{metrics['rows']} | "
                f"{metrics['repair_solve_exact']}/{metrics['rows']} | {metrics['repair_solve_exact_rate']:.4f} |"
            )
        noisy_section = f"""## Noisy Constraint Extraction

The noisy/paraphrased extraction run completed under the Windows job-cap wrapper with a {noisy_jobcap['caps']['ram_mb']:,} MB RAM cap, {noisy_jobcap['caps']['cpu_pct']}% CPU cap, {noisy_jobcap['caps']['io_mb_s']} MB/s IO cap, and {noisy_jobcap['caps']['timeout_sec']:,} second timeout. Runner-level child RSS peaked at `{noisy_result['summary'].get('peak_child_ram_mb', 0.0):.2f} MB`; the wrapper reported `{noisy_jobcap['status']}`.

| Arm | JSON Parse | Strict Packet Exact | Strict Solve Exact | Repair Solve Exact | Repair Solve Rate |
| --- | ---: | ---: | ---: | ---: | ---: |
{chr(10).join(noisy_lines)}

The graph-gated prompt improves the noisy repaired solve score from `metta_schema_extract` {noisy_arms['metta_schema_extract']['repair_solve_exact']}/{noisy_arms['metta_schema_extract']['rows']} to `metta_graph_extract` {noisy_arms['metta_graph_extract']['repair_solve_exact']}/{noisy_arms['metta_graph_extract']['rows']}. The remaining failures are field-transcription mistakes, not grid-execution failures.
"""
        allowed_live += (
            f"\n- On noisy/paraphrased prompts, `metta_graph_extract` scored "
            f"{noisy_arms['metta_graph_extract']['repair_solve_exact']}/{noisy_arms['metta_graph_extract']['rows']} "
            f"repaired solve exact versus baseline "
            f"{noisy_arms['baseline_extract']['repair_solve_exact']}/{noisy_arms['baseline_extract']['rows']}."
        )
        evidence += ", `live_model_local_3b_constraint_extract`"
    else:
        noisy_section = """## Noisy Constraint Extraction

Pending: run `research/scripts/build_logic_signature_noisy_extract_rows.py` and the noisy local 3B extraction suite.
"""

    if graph_router:
        router_arms = graph_router["summary"]["arms"]
        router_lines = []
        for arm in ("metta_graph_router_script", "canonical_packet_solver"):
            if arm not in router_arms:
                continue
            metrics = router_arms[arm]
            router_lines.append(
                f"| `{arm}` | {metrics['packet_valid']}/{metrics['rows']} | "
                f"{metrics['packet_exact']}/{metrics['rows']} | {metrics['solve_exact']}/{metrics['rows']} | "
                f"{metrics['solve_exact_rate']:.4f} |"
            )
        graph_router_section = f"""## Graph Router Control

The script-owned graph router parses only prompt-visible dimensions, anchor coordinates, row quotas, and column quotas before handing the packet to the public solver. It is the cleanest expression of the current methodology: scripts own stable extraction gates, TRM candidates should target uncertain gates, and the LLM should remain a proposal source rather than the executor.

| Arm | Packet Valid | Packet Exact | Solve Exact | Solve Rate |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(router_lines)}

This control reaches closure because the noisy prompts are still structured enough for typed script gates. It should be reported as a control-plane threshold, not as language understanding or trained TRM lift.
"""
        allowed_live += (
            f"\n- Script-owned graph routing solved "
            f"{router_arms['metta_graph_router_script']['solve_exact']}/{router_arms['metta_graph_router_script']['rows']} "
            "noisy rows using prompt-visible constraints only."
        )
        evidence += ", `no_model_prompt_constraint_graph_router`"
    else:
        graph_router_section = """## Graph Router Control

Pending: run `research/scripts/run_logic_signature_noisy_graph_router.py`.
"""

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
- Projection ablation: `results/projection_ablation/projection_ablation.results.md`
- Constraint extraction: `results/local_qwen25_3b_constraint_extract/local_qwen25_3b_constraint_extract.results.md`
- Constraint extraction repair: `results/constraint_extract_schema_repair/constraint_extract_schema_repair.results.md`
- Noisy extraction rows: `rows/logic_signature_camp_gate_noisy_extract_rows.jsonl`
- Noisy extraction config: `configs/logic_signature_noisy_extract_suite.json`
- Noisy local 3B graph extraction: `results/local_qwen25_3b_noisy_graph_constraint_extract/local_qwen25_3b_constraint_extract.results.md`
- Noisy graph router control: `results/noisy_graph_router_script/noisy_graph_router.results.md`
- Graph router MeTTa contract: `results/noisy_graph_router_script/camp_gate_graph_router_contract.metta`

{local_section}

{ablation_section}

{extract_section}

{noisy_section}

{graph_router_section}
"""
    plan = f"""# Study Plan

## Hypothesis

MeTTa/TRM signature projection can amplify hard logic only when a small model emits enough verifier-visible grid state. The gain should appear in `metta_signature_projection`, not necessarily in raw `metta_runtime`.

The broader methodology is a task graph: stable symbolic gates should be scripts, uncertain verifier-facing gates become TRM training targets, and the LLM is most useful as a proposal/imagination source rather than as the final executor.

## Arms

- `baseline`: direct grid answer.
- `pure_trm`: TRM-style contract parsing prompt.
- `metta_runtime`: MeTTa/TRM gate prompt without deterministic projection.
- `metta_signature_projection`: deterministic min-edit projection from the `metta_runtime` candidate to public prompt constraints.
- `metta_graph_extract`: noisy natural-language constraint extraction framed as typed gates.
- `metta_graph_router_script`: no-model control where typed script gates own prompt-visible extraction before public solving.

## Metrics

- `exact_success`: grid matches the unique solver-derived target.
- `contract_valid`: grid satisfies public constraints.
- `avg_cell_accuracy`: cell-level agreement with the held-out target.
- `proposal_tier`: `none`, `weak_surface`, `partial_semantic`, or `full_candidate`.
- `repair_solve_exact`: solved grid after deterministic schema repair of extracted constraint packets.

## Promotion Rule

Promote as hard-env evidence only if projection improves exactness/cell accuracy and the audit shows `target_grid_in_prompt=false`, `projection_uses_target_grid=false`, and `unique_solution_from_prompt_constraints=true`.

## Stop Rule

If raw 3B outputs are mostly `none`, this lane needs a stronger model or a public-trace scaffold before projection can be meaningfully tested.
"""
    audit = f"""# Claim Audit

## Evidence Class

- `no_model_proposal_tier_smoke` verifies the validator and projection threshold behavior.
- `live_model_local_3b` applies the same frozen rows and validator to local 3B completions when result receipts exist.
- `live_model_local_3b_constraint_extract` measures whether 3B can transcribe prompt-visible constraints into solver packets.
- `no_model_prompt_constraint_graph_router` measures typed script-gate closure without an LLM solve step.

## Allowed Claims

- The suite is leakage-safe with respect to target grids: prompts contain constraints but not answers.
- Prompt-derived signatures and adjacency rules are sufficient to solve each frozen micro-row uniquely.
- Projection may be described as symbolic closure over public constraints.
{allowed_live}

## Disallowed Claims

- Do not call projection success a latent-reasoning improvement.
- Do not compare this directly to the old 27B receipt replay without noting the old replay used answer-derived signatures.
- Do not claim trained TRM lift; this study tests runtime framing and deterministic MeTTa projection.
- Do not claim broad natural-language puzzle extraction yet; the noisy prompts are paraphrased but still generated from known controlled surfaces.
- Do not conflate script-gate closure with model reasoning. It is evidence for control-plane allocation, not language-model capability.
"""

    config = {
        "generated_at_utc": generated_at,
        "route_id": "hard_env_boundary",
        "project_id": "logic_signature_camp_gate",
        "row_count": len(rows),
        "shape_counts": counts,
        "validator": str(VALIDATOR_PATH.relative_to(ROOT)),
        "noisy_rows": str(NOISY_ROWS_PATH.relative_to(ROOT)),
        "noisy_config": str(NOISY_CONFIG_PATH.relative_to(ROOT)),
        "graph_router_contract": str(GRAPH_ROUTER_CONTRACT.relative_to(ROOT)),
        "projection_inputs": ["candidate_grid", "fixed_t_cells", "row_c_counts", "col_c_counts", "adjacency_rules"],
        "projection_forbidden_inputs": ["canonical_output", "canonical_sha256", "expected_grid"],
        "task_graph_allocation": {
            "script_gate": ["dimension_extraction", "anchor_extraction", "row_quota_extraction", "column_quota_extraction", "public_constraint_solver"],
            "trm_training_target": ["field_transcription_under_paraphrase", "schema_repair_accept_reject", "candidate_commit_policy"],
            "llm_role": ["proposal_generation", "ambiguous_surface_interpretation"],
        },
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
