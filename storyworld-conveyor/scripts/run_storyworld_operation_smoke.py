#!/usr/bin/env python3
from __future__ import annotations

import argparse
import inspect
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


SKILL_ROOT = Path(__file__).resolve().parents[1]
HERMES_REPO_ROOT = Path(__file__).resolve().parents[2]


def find_storyworld_repo_root() -> Path:
    candidates = []
    env_root = str(os.environ.get("GPTSTORYWORLD_ROOT", "") or "").strip()
    if env_root:
        candidates.append(Path(env_root))
    candidates.extend([HERMES_REPO_ROOT, Path(r"C:\projects\GPTStoryworld")])
    for root in candidates:
        if (root / "storyworlds").exists() or (root / "storyworld").exists():
            return root.resolve()
    return HERMES_REPO_ROOT.resolve()


STORYWORLD_REPO_ROOT = find_storyworld_repo_root()
CONVEYOR_SCRIPTS = SKILL_ROOT / "scripts"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            count += 1
    return count


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line:
            continue
        row = json.loads(line)
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _load_runtime() -> Dict[str, Any]:
    try:
        import torch
        from peft import LoraConfig, PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    except Exception as exc:  # pragma: no cover - preflight
        raise SystemExit(
            "Missing runtime dependencies for the operation smoke test. "
            "Use the local training python with torch, transformers, and peft installed. "
            f"Original error: {type(exc).__name__}: {exc}"
        )
    return {
        "torch": torch,
        "LoraConfig": LoraConfig,
        "PeftModel": PeftModel,
        "AutoModelForCausalLM": AutoModelForCausalLM,
        "AutoTokenizer": AutoTokenizer,
        "BitsAndBytesConfig": BitsAndBytesConfig,
    }


def _sanitize_adapter_copy(adapter_path: Path, allowed_keys: Iterable[str]) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="storyworld_operation_adapter_"))
    shutil.copytree(adapter_path, temp_dir, dirs_exist_ok=True)
    config_path = temp_dir / "adapter_config.json"
    if config_path.exists():
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except Exception:
            payload = None
        if isinstance(payload, dict):
            allowed = set(allowed_keys)
            filtered = {key: value for key, value in payload.items() if key in allowed}
            if filtered != payload:
                config_path.write_text(json.dumps(filtered, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    return temp_dir


def _load_adapter_model(model: Any, adapter_path: Path, PeftModel: Any) -> Any:
    attempted: set[str] = set()
    candidate_path = adapter_path
    for _ in range(3):
        try:
            return PeftModel.from_pretrained(model, str(candidate_path))
        except TypeError as exc:
            match = re.search(r"unexpected keyword argument '([^']+)'", str(exc))
            if not match:
                raise
            bad_key = match.group(1)
            if bad_key in attempted:
                raise
            attempted.add(bad_key)
            candidate_path = _sanitize_adapter_copy(adapter_path, [])
    return PeftModel.from_pretrained(model, str(candidate_path))


def load_model(model_path: Path, adapter_path: Path | None) -> Tuple[Any, Any]:
    libs = _load_runtime()
    torch = libs["torch"]
    LoraConfig = libs["LoraConfig"]
    PeftModel = libs["PeftModel"]
    AutoModelForCausalLM = libs["AutoModelForCausalLM"]
    AutoTokenizer = libs["AutoTokenizer"]
    BitsAndBytesConfig = libs["BitsAndBytesConfig"]

    dtype = torch.float16
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True, local_files_only=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token or tokenizer.unk_token
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=dtype,
        bnb_4bit_use_double_quant=True,
    )
    base = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        trust_remote_code=True,
        local_files_only=True,
        low_cpu_mem_usage=True,
        quantization_config=bnb,
        torch_dtype=dtype,
        device_map="auto",
    )
    model = base
    if adapter_path and adapter_path.exists():
        config_path = adapter_path / "adapter_config.json"
        if config_path.exists():
            try:
                adapter_config = json.loads(config_path.read_text(encoding="utf-8"))
            except Exception:
                adapter_config = {}
            if isinstance(adapter_config, dict):
                allowed = [name for name in inspect.signature(LoraConfig.__init__).parameters if name != "self"]
                adapter_path = _sanitize_adapter_copy(adapter_path, allowed)
        model = _load_adapter_model(base, adapter_path, PeftModel)
    model.eval()
    return tokenizer, model


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _extract_json_object(text: str) -> str:
    start = text.find("{")
    if start < 0:
        return ""
    depth = 0
    in_string = False
    escape = False
    for idx in range(start, len(text)):
        ch = text[idx]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]
    return ""


def _load_packets(path: Path) -> List[Dict[str, Any]]:
    return read_jsonl(path)


def _normalize_op(row: Dict[str, Any], allowed_actions: set[str]) -> Dict[str, Any]:
    kind = str(row.get("kind", "") or "").strip()
    action = str(row.get("action", "") or "").strip()
    target = str(row.get("target", "") or "").strip()
    details = str(row.get("details", "") or "").strip()
    if kind not in {"option", "reaction", "effect", "formula"}:
        kind = "formula" if action in {"rewrite_formula", "diversify_operator"} else "effect"
    if action not in allowed_actions:
        if kind == "formula":
            action = "rewrite_formula" if action not in {"rewrite_formula", "diversify_operator"} else action
        elif kind == "option":
            action = "add_option" if action not in {"add_option", "rebalance_visibility"} else action
        elif kind == "reaction":
            action = "add_reaction" if not action.startswith("add_") else action
        elif kind == "effect":
            action = "add_effect" if action not in {"add_effect", "diversify_effect_operator"} else action
    return {"kind": kind, "action": action, "target": target, "details": details}


def _normalize_response(packet: Dict[str, Any], parsed: Dict[str, Any]) -> Dict[str, Any]:
    contract = packet.get("repair_contract", {})
    allowed_actions = set(contract.get("allowed_actions", []) or [])
    selected_op: Dict[str, Any] | None = None
    raw_op = parsed.get("selected_op")
    if isinstance(raw_op, dict):
        selected_op = _normalize_op(raw_op, allowed_actions)
    else:
        raw_ops = parsed.get("selected_ops", [])
        if isinstance(raw_ops, list) and raw_ops:
            first = raw_ops[0]
            if isinstance(first, dict):
                selected_op = _normalize_op(first, allowed_actions)
    if selected_op is None:
        fallback_row = packet.get("suggested_ops", [])[:1]
        if fallback_row and isinstance(fallback_row[0], dict):
            row = fallback_row[0]
            selected_op = {
                "kind": str(row.get("kind", "") or ""),
                "action": str(row.get("action", "") or ""),
                "target": str(row.get("target_count", row.get("operator_diversity_target", row.get("formula_diversity_target", ""))) or ""),
                "details": str(row.get("reason", "") or ""),
            }
    notes = parsed.get("repair_notes", [])
    if not isinstance(notes, list):
        notes = []
    note_text = [str(x) for x in notes if str(x).strip()]
    if not note_text:
        note_text = ["fallback_to_deterministic_suggestions"]
    status = str(parsed.get("status", "") or "").strip() or "needs_repair"
    return {
        "encounter_id": str(packet.get("encounter_id", "") or ""),
        "status": status,
        "selected_op": selected_op,
        "repair_notes": note_text,
    }


def _build_prompt(packet: Dict[str, Any]) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You normalize one storyworld repair packet into strict JSON only. "
                "Do not use markdown fences or prose."
            ),
        },
        {
            "role": "user",
            "content": (
                "Return JSON matching this shape exactly:\n"
                "{"
                "\"encounter_id\":\"string\","
                "\"status\":\"ok|needs_repair\","
                "\"selected_op\":{\"kind\":\"option|reaction|effect|formula\",\"action\":\"string\",\"target\":\"string\",\"details\":\"string\"},"
                "\"repair_notes\":[\"string\"]"
                "}\n\n"
                "Use only the packet data below and prefer local deterministic edits.\n"
                "Choose exactly 1 selected_op.\n"
                f"PACKET\n{json.dumps(packet, ensure_ascii=True, indent=2)}"
            ),
        },
    ]


def _generate(tokenizer: Any, model: Any, messages: List[Dict[str, str]], max_new_tokens: int, temperature: float) -> str:
    import torch

    if hasattr(tokenizer, "apply_chat_template"):
        try:
            rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        except Exception:
            rendered = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    else:
        rendered = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    inputs = tokenizer(rendered, return_tensors="pt", truncation=True, max_length=4096)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=temperature > 0.0,
            temperature=max(0.01, temperature),
            top_p=0.9,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id,
        )
    new_tokens = out[0][inputs["input_ids"].shape[1] :]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Windows-friendly operation-level smoke test for storyworld repair packets.")
    parser.add_argument("--world-json", required=True)
    parser.add_argument("--quality-report", default="")
    parser.add_argument("--packet-jsonl", default="")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--adapter-path", default="")
    parser.add_argument("--output-root", default=str(SKILL_ROOT / "context_port_runs"))
    parser.add_argument("--run-id", default="")
    parser.add_argument("--max-packets", type=int, default=24)
    parser.add_argument("--max-new-tokens", type=int, default=160)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--no-adapter", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = args.run_id or f"operation_smoke_{int(time.time())}"
    output_root = ensure_dir(Path(args.output_root).resolve())
    run_dir = ensure_dir(output_root / run_id)
    dump_json(
        run_dir / "run_config.snapshot.json",
        {
            "world_json": str(Path(args.world_json).resolve()),
            "quality_report": str(Path(args.quality_report).resolve()) if args.quality_report else "",
            "packet_jsonl": str(Path(args.packet_jsonl).resolve()) if args.packet_jsonl else "",
            "model_path": str(Path(args.model_path).resolve()),
            "adapter_path": str(Path(args.adapter_path).resolve()) if args.adapter_path and not args.no_adapter else "",
            "max_packets": args.max_packets,
            "max_new_tokens": args.max_new_tokens,
            "temperature": args.temperature,
        },
    )

    packet_path = Path(args.packet_jsonl).resolve() if args.packet_jsonl else run_dir / "reports" / "operation_packets.jsonl"
    if not args.packet_jsonl:
        builder_cmd = [
            sys.executable,
            str(CONVEYOR_SCRIPTS / "build_storyworld_operation_packets.py"),
            "--world-json",
            str(Path(args.world_json).resolve()),
            "--out",
            str(packet_path),
        ]
        if args.quality_report:
            builder_cmd.extend(["--quality-report", str(Path(args.quality_report).resolve())])
        rc = subprocess.run(builder_cmd, capture_output=True, text=True, check=False)
        (run_dir / "build_packets.stdout.log").write_text(rc.stdout or "", encoding="utf-8", newline="\n")
        (run_dir / "build_packets.stderr.log").write_text(rc.stderr or "", encoding="utf-8", newline="\n")
        if rc.returncode != 0:
            raise SystemExit((rc.stderr or rc.stdout or "failed to build operation packets").strip())

    packets = _load_packets(packet_path)[: args.max_packets]
    dump_json(run_dir / "packet_manifest.json", {"packet_jsonl": str(packet_path), "packet_count": len(packets)})

    if args.dry_run:
        dump_json(
            run_dir / "summary.json",
            {
                "run_id": run_id,
                "status": "planned",
                "packet_count": len(packets),
                "model_path": str(Path(args.model_path).resolve()),
            },
        )
        print(str(run_dir))
        return 0

    adapter_path = None if args.no_adapter else Path(args.adapter_path).resolve() if args.adapter_path else None
    tokenizer, model = load_model(Path(args.model_path).resolve(), adapter_path)

    generations: List[Dict[str, Any]] = []
    parse_ok_count = 0
    fallback_count = 0
    for packet in packets:
        messages = _build_prompt(packet)
        prompt_text = json.dumps(messages, ensure_ascii=True, indent=2)
        prompt_est = _estimate_tokens(prompt_text)
        t0 = time.time()
        raw = _generate(tokenizer, model, messages, args.max_new_tokens, args.temperature)
        latency_ms = int((time.time() - t0) * 1000)
        parsed_text = _extract_json_object(raw) or raw
        try:
            parsed = json.loads(parsed_text)
            parse_ok = isinstance(parsed, dict)
        except Exception:
            parsed = {}
            parse_ok = False
        if not parse_ok:
            fallback_count += 1
        else:
            parse_ok_count += 1
        normalized = _normalize_response(packet, parsed if isinstance(parsed, dict) else {})
        if not parse_ok:
            normalized["status"] = "needs_repair"
        generations.append(
            {
                "encounter_id": packet.get("encounter_id", ""),
                "title": packet.get("title", ""),
                "turn_span": packet.get("turn_span", ""),
                "prompt_estimated_tokens": prompt_est,
                "latency_ms": latency_ms,
                "parse_ok": parse_ok,
                "raw_output": raw,
                "normalized": normalized,
                "packet": packet,
            }
        )

    gen_path = run_dir / "generations.jsonl"
    dump_jsonl(gen_path, generations)
    summary = {
        "run_id": run_id,
        "status": "completed",
        "world_json": str(Path(args.world_json).resolve()),
        "quality_report": str(Path(args.quality_report).resolve()) if args.quality_report else "",
        "packet_jsonl": str(packet_path),
        "packet_count": len(packets),
        "parse_ok_count": parse_ok_count,
        "fallback_count": fallback_count,
        "parse_accuracy": round(parse_ok_count / max(1, len(packets)), 3),
        "generations_jsonl": str(gen_path),
    }
    dump_json(run_dir / "summary.json", summary)
    print(str(run_dir))
    print(str(run_dir / "summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
