"""Addendum A3: replicate the April Qwen2.5-3B results with the April runners executed unchanged (from git),
and run the new arms through the same llama-completion path. CPU only.

usage: python qwen_replicate.py rudder-published | rudder-extra | mixed-published | mixed-neutral | campx
"""

from __future__ import annotations

import subprocess
import sys
import time
import types
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import RESULTS, append_jsonl, head_jsonl, lower_priority, read_jsonl, write_json  # noqa: E402

OUT = RESULTS / "qwen3b"
HEAD = OUT / "head" / "research"
SCRIPTS = HEAD / "scripts"
MODEL = Path(r"C:\Users\patri\Documents\Codex\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf")
LLAMA = Path(r"C:\Users\patri\Documents\Codex\BitAgent-gym\llama-prism\bin\llama-completion.exe")
CPU = {"threads": 8, "batch_size": 512, "ubatch_size": 512, "gpu_layers": "0"}
CPU_ARGS = ["--threads", "8", "--batch-size", "512", "--ubatch-size", "512", "--gpu-layers", "0", "--cooldown-sec", "0"]
SUITES = {"heldout50": ("2026-04-28-mixed-contract-compactification-heldout50", "mixed_contract_heldout50_rows.jsonl"),
          "hard30": ("2026-04-28-mixed-contract-hard-ablation30", "mixed_contract_hard_ablation30_rows.jsonl")}


def run(cmd: list[str]) -> None:
    print(" ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=str(SCRIPTS))


@lru_cache(maxsize=None)
def module(path: Path, name: str):
    m = types.ModuleType(name)
    m.__file__ = str(path)
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))
    exec(compile(path.read_text(encoding="utf-8-sig"), str(path), "exec"), m.__dict__)  # noqa: S102
    return m


def rudder_published() -> None:
    arms = ["raw_3b_rudder", "repair_training_rudder", "metta_action_space_rudder", "metta_action_space_training_rudder",
            "metta_static_gate_rudder", "metta_validator_gate"]
    run([sys.executable, "-u", str(SCRIPTS / "run_3b_repair_training_rudder_benchmark_apr28.py"),
         "--model-path", str(MODEL), "--llama-completion-path", str(LLAMA),
         "--split-dir", str(HEAD / "generated" / "near_miss_repair_curriculum" / "splits"),
         "--out-dir", str(OUT / "rudder_published"), "--max-cases", "0", "--shots", "4", "--ctx", "1536",
         "--max-tokens", "64", "--timeout-sec", "300", "--max-child-rss-mb", "3500", *CPU_ARGS,
         *[x for a in arms for x in ("--arm", a)]])


def rudder_extra() -> None:
    import rudder

    m = module(SCRIPTS / "run_3b_repair_training_rudder_benchmark_apr28.py", "rudder_apr28")
    for arm in ("raw-fullvocab", "retrieval-clean"):
        path = OUT / f"rudder_extra.{arm}.jsonl"
        done = {r["key"] for r in read_jsonl(path)}
        for row in rudder.eval_rows():
            if rudder.key(row) in done:
                continue
            if arm == "raw-fullvocab":
                msgs, retrieved = m.make_prompt("raw_3b_rudder", row, [], rudder.all_actions()), []
            else:
                ex = rudder.clean_retrieve(rudder.rows()["train"], row)
                msgs, retrieved = m.make_prompt("repair_training_rudder", row, ex, rudder.train_actions()), [e["state"]["case_id"] for e in ex]
            out, diag, elapsed = m.run_llama_completion(
                llama_completion=LLAMA, model_path=MODEL, messages=msgs, ctx=1536, max_tokens=64, timeout_sec=300,
                max_child_rss_mb=3500.0, cooldown_sec=0.0, max_prompt_chars=7000, **CPU)
            parsed = m.parse_model_json(out)
            append_jsonl(path, rudder.score(row, parsed["repair_action"], parsed["target_action"], arm=arm, raw_output=out,
                                            retrieved=retrieved, latency_s=round(elapsed, 2)))
        print(f"{arm}: done", flush=True)


def mixed_published() -> None:
    for suite, (study, rows) in SUITES.items():
        base = HEAD / "studies" / study
        run([sys.executable, "-u", str(SCRIPTS / "run_mixed_contract_local_3b.py"), "--rows", str(base / "rows" / rows),
             "--validator", str(base / "validators" / "validate_mixed_contracts.py"), "--out-dir", str(OUT / f"mixed_{suite}"),
             "--model-path", str(MODEL), "--llama-completion-path", str(LLAMA), "--max-cases", "0", "--ctx", "1536",
             "--max-tokens", "64", "--timeout-sec", "300", "--max-child-rss-mb", "3500", "--include-blind-repair",
             "--run-title", f"Qwen2.5-3B CPU replication {suite}", *CPU_ARGS])


def mixed_neutral() -> None:
    m = module(SCRIPTS / "run_mixed_contract_local_3b.py", "mixed_head")
    for suite, (study, rows_name) in SUITES.items():
        base = HEAD / "studies" / study
        validator = module(base / "validators" / "validate_mixed_contracts.py", f"validator_{suite}")
        path = OUT / f"mixed_neutral.{suite}.jsonl"
        done = {r["row_id"] for r in read_jsonl(path)}
        for row in read_jsonl(base / "rows" / rows_name):
            if row["row_id"] in done:
                continue
            msgs = [m.arm_prompt(row, "baseline")[0], m.arm_prompt(row, "pure_trm")[1]]
            out, diag = m.run_llama_completion(llama_completion=LLAMA, model_path=MODEL, messages=msgs, ctx=1536, max_tokens=64,
                                               timeout_sec=300, max_prompt_chars=5000, max_child_rss_mb=3500.0, **CPU)
            output = m.clean_model_output(out)
            v = validator.validate(row, output)
            append_jsonl(path, {"suite": suite, "row_id": row["row_id"], "env_family": row["env_family"], "arm": "contract-neutral",
                                "output": output, "contract_valid": bool(v["contract_valid"]),
                                "semantic_valid": bool(v["semantic_valid"]), "exact_success": bool(v["exact_success"])})
        print(f"{suite}: done", flush=True)


def campx() -> None:
    # The rows path inside the extracted tree exceeds Windows' 260-character limit; read it from HEAD
    # into a short path instead (same bytes as the committed file).
    from common import git_show

    rows = OUT / "campx_rows.jsonl"
    rows.write_text(git_show("research/studies/2026-04-29-logic-signature-camp-gate-leakage-safe/rows/"
                             "logic_signature_camp_gate_noisy_extract_rows.jsonl"), encoding="utf-8")
    run([sys.executable, "-u", str(SCRIPTS / "run_logic_signature_constraint_extract_local_3b.py"),
         "--rows", str(rows),
         "--out-dir", str(OUT / "campgate_noisy"), "--model-path", str(MODEL), "--llama-completion-path", str(LLAMA),
         "--max-cases", "0", "--ctx", "1536", "--max-tokens", "180", "--timeout-sec", "300", "--max-child-rss-mb", "3500",
         *CPU_ARGS])


def main() -> int:
    lower_priority()
    write_json(OUT / "model.json", {"path": str(MODEL), "repo": "Qwen/Qwen2.5-3B-Instruct-GGUF", "revision": "7dabda4d13d513e3e842b20f0d435c732f172cbe",
                                    "sha256": "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d",
                                    "llama_completion": str(LLAMA), **CPU})
    {"rudder-published": rudder_published, "rudder-extra": rudder_extra, "mixed-published": mixed_published,
     "mixed-neutral": mixed_neutral, "campx": campx}[sys.argv[1]]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
