"""Part M: the mixed-contract suites rerun with Bonsai-8B, adding a contract-neutral arm so that showing the
validator contract and the skill wording separate. Prompts, rows and validators come from Hermes-Skills HEAD.

usage: python mixed.py llm | dry
"""

from __future__ import annotations

import argparse
import sys
import time
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS, append_jsonl, head_jsonl, head_module, lower_priority, read_jsonl, write_json  # noqa: E402

RUNNER = "research/scripts/run_mixed_contract_local_3b.py"
SUITES = {
    "heldout50": "research/studies/2026-04-28-mixed-contract-compactification-heldout50",
    "hard30": "research/studies/2026-04-28-mixed-contract-hard-ablation30",
}
ARMS = ("baseline", "contract-neutral", "skill-wording", "gate-wording", "repair-feedback", "repair-blind")
OUT = RESULTS / "mixed"


@lru_cache(maxsize=None)
def pub():
    return head_module(RUNNER, "published_mixed_runner", stubs=("psutil",))


@lru_cache(maxsize=None)
def validator(suite: str):
    return head_module(f"{SUITES[suite]}/validators/validate_mixed_contracts.py", f"validator_{suite}")


@lru_cache(maxsize=None)
def suite_rows(suite: str) -> list[dict]:
    name = "mixed_contract_heldout50_rows.jsonl" if suite == "heldout50" else "mixed_contract_hard_ablation30_rows.jsonl"
    return head_jsonl(f"{SUITES[suite]}/rows/{name}")


def first_messages(row: dict, arm: str) -> list[dict]:
    p = pub()
    if arm == "baseline":
        return p.arm_prompt(row, "baseline")
    if arm == "contract-neutral":
        system = p.arm_prompt(row, "baseline")[0]
        user = p.arm_prompt(row, "pure_trm")[1]  # "Prompt: ...\n\nPublic validator contract: ..."
        return [system, user]
    if arm == "skill-wording":
        return p.arm_prompt(row, "pure_trm")
    if arm == "gate-wording":
        return p.arm_prompt(row, "metta_runtime")
    raise ValueError(arm)


def evaluate(suite: str, row: dict, output: str) -> dict:
    v = validator(suite).validate(row, output)
    return {"contract_valid": bool(v["contract_valid"]), "semantic_valid": bool(v["semantic_valid"]),
            "exact_success": bool(v["exact_success"]), "details": v["details"]}


def run_llm() -> None:
    import bonsai

    lower_priority()
    p = pub()
    with bonsai.Server("Bonsai-8B", threads=8, slots=1, ctx_per_slot=8192) as server:
        write_json(OUT / "server.json", {"model": "Bonsai-8B", "sha256": server.sha256, "gpu_layers": 0, "max_tokens": 64,
                                         "temperature": 0.0})
        for suite in SUITES:
            path = OUT / f"bonsai8b.{suite}.jsonl"
            done = {(r["row_id"], r["arm"]) for r in read_jsonl(path)}
            for row in suite_rows(suite):
                gate_out = None
                for arm in ARMS:
                    if (row["row_id"], arm) in done:
                        if arm == "gate-wording":
                            gate_out = next(r for r in read_jsonl(path) if r["row_id"] == row["row_id"] and r["arm"] == arm)
                        continue
                    t0 = time.time()
                    if arm in ("repair-feedback", "repair-blind"):
                        if gate_out["exact_success"]:  # as in the published runner: an exact output is not repaired
                            output, source = gate_out["output"], "already_exact"
                        else:
                            verdict = evaluate(suite, row, gate_out["output"])
                            msgs = p.repair_prompt(row, gate_out["output"], verdict) if arm == "repair-feedback" \
                                else p.blind_repair_prompt(row, gate_out["output"])
                            output, source = p.clean_model_output(server.chat(msgs, max_tokens=64)["content"]), "model"
                    else:
                        output, source = p.clean_model_output(server.chat(first_messages(row, arm), max_tokens=64)["content"]), "model"
                    rec = {"suite": suite, "row_id": row["row_id"], "env_family": row["env_family"], "arm": arm, "output": output,
                           "source": source, "latency_s": round(time.time() - t0, 2), **evaluate(suite, row, output)}
                    append_jsonl(path, rec)
                    if arm == "gate-wording":
                        gate_out = rec
            print(f"{suite}: done", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("llm", "dry"))
    args = ap.parse_args()
    if args.mode == "llm":
        run_llm()
        return 0
    for suite in SUITES:
        rs = suite_rows(suite)
        print(suite, len(rs), "rows")
        for arm in ARMS[:4]:
            m = first_messages(rs[0], arm)
            print("==", arm, "| system:", m[0]["content"][:120], "| user:", m[1]["content"][:160].replace("\n", " / "))
        print("validator on empty output:", evaluate(suite, rs[0], "")["exact_success"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
