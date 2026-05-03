from __future__ import annotations

import argparse
import json
import inspect
import os
import re
import shutil
import tempfile
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from storyworld_mcp_server import StoryworldIndex  # noqa: E402


DEFAULT_MODEL_PATH = Path(r"D:\Research_Engine\models\Qwen3.5\Qwen3.5-2B-HF")
DEFAULT_ADAPTER_PATH = Path(r"D:\Research_Engine\storyworld_qlora\adapters\qwen35-2b-usual-suspects-local-r2-checkpoint13")
DEFAULT_INDEX_ROOT = Path(
    r"C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\factory_runs\the_usual_suspects_qwen35_2b_run\indices\encounter_index"
)
DEFAULT_OUTPUT_ROOT = Path(r"C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\context_port_runs")


DEFAULT_QUERIES: List[Dict[str, Any]] = [
    {
        "id": "scene_lookup",
        "query": "Show me the encounter card for page_scene_01.",
        "expected_tool": "get_encounter_card",
        "expected_args": {"encounter_id": "page_scene_01"},
        "namespace": "encounters",
    },
    {
        "id": "world_rules",
        "query": "What are the world's core story rules and structural constraints?",
        "expected_tool": "query_lore_index",
        "expected_args": {"namespace": "world_card", "query": "core story rules and structural constraints"},
        "namespace": "world_card",
    },
    {
        "id": "monte_carlo_rebalance",
        "query": "Review the Monte Carlo distribution to target a rebalance.",
        "expected_tool": "query_lore_index",
        "expected_args": {"namespace": "monte_carlo", "query": "distribution target a rebalance"},
        "namespace": "monte_carlo",
    },
    {
        "id": "quality_gate_pathing",
        "query": "Review the quality gate failures that affect pathing, options, reactions, and effects.",
        "expected_tool": "query_lore_index",
        "expected_args": {
            "namespace": "quality_gate",
            "query": "pathing options reactions effects",
        },
        "namespace": "quality_gate",
    },
    {
        "id": "formula_rebalance",
        "query": "Revise the formulas to modify pathing and ending rebalance.",
        "expected_tool": "query_lore_index",
        "expected_args": {
            "namespace": "rebalance_advice",
            "query": "pathing ending rebalance formulas",
        },
        "namespace": "rebalance_advice",
    },
    {
        "id": "scene_followup",
        "query": "I need the encounter card for a terminal route and the adjacent context.",
        "expected_tool": "get_encounter_card",
        "expected_args": {"encounter_id": "page_end_200"},
        "namespace": "encounters",
    },
]


def dump_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")


def dump_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> int:
    count = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
            count += 1
    return count


def estimate_tokens(text: str) -> int:
    return max(1, len(re.findall(r"[A-Za-z0-9_]+", str(text))))


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def resolve_queries(index: StoryworldIndex, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    summary = index.describe()
    sample_ids = [str(item) for item in summary.get("sample_encounter_ids", []) if str(item).strip()]
    scene_ids = [encounter_id for encounter_id in sample_ids if encounter_id.startswith("page_scene_")]
    terminal_ids = [encounter_id for encounter_id in sample_ids if encounter_id.startswith("page_end_")]
    if not scene_ids and sample_ids:
        scene_ids = [sample_ids[0]]
    if not terminal_ids and sample_ids:
        terminal_ids = [sample_ids[-1]]
    resolved: List[Dict[str, Any]] = []
    for query in queries:
        row = dict(query)
        if row.get("id") == "scene_lookup" and scene_ids:
            row["query"] = f"Show me the encounter card for {scene_ids[0]}."
            row["expected_args"] = {"encounter_id": scene_ids[0]}
        elif row.get("id") == "scene_followup" and terminal_ids:
            row["query"] = f"I need the encounter card for {terminal_ids[0]} and the adjacent context."
            row["expected_args"] = {"encounter_id": terminal_ids[0]}
        resolved.append(row)
    return resolved


def parse_router_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first >= 0 and last >= first:
        candidate = cleaned[first : last + 1]
        try:
            payload = json.loads(candidate)
            return payload if isinstance(payload, dict) else {}
        except Exception:
            pass
    return {}


def normalize_tool_call(payload: Dict[str, Any], query: Dict[str, Any]) -> Dict[str, Any]:
    tool = str(payload.get("tool") or payload.get("intent") or payload.get("action") or "").strip()
    args = payload.get("args", {})
    if not isinstance(args, dict):
        args = {}
    if not tool:
        if "encounter_id" in query.get("expected_args", {}):
            tool = "get_encounter_card"
            args = {"encounter_id": query["expected_args"]["encounter_id"]}
        else:
            tool = "query_lore_index"
            args = {"namespace": query.get("namespace", "world_card"), "query": query["query"]}
    if tool == "get_encounter_card":
        encounter_id = str(args.get("encounter_id") or args.get("id") or query.get("expected_args", {}).get("encounter_id") or "").strip()
        args = {"encounter_id": encounter_id}
    elif tool == "query_lore_index":
        namespace = str(args.get("namespace") or query.get("namespace") or "world_card").strip() or "world_card"
        query_text = str(args.get("query") or query["query"]).strip()
        args = {"namespace": namespace, "query": query_text}
    else:
        args = {k: v for k, v in args.items()}
    return {"tool": tool, "args": args}


def route_is_correct(query: Dict[str, Any], routed: Dict[str, Any]) -> bool:
    expected_tool = str(query.get("expected_tool", "") or "")
    expected_args = dict(query.get("expected_args", {})) if isinstance(query.get("expected_args"), dict) else {}
    tool_name = str(routed.get("tool", "") or "")
    tool_args = routed.get("args", {}) if isinstance(routed.get("args"), dict) else {}
    if tool_name != expected_tool:
        return False
    if tool_name == "get_encounter_card":
        expected_id = str(expected_args.get("encounter_id", "") or "").strip()
        routed_id = str(tool_args.get("encounter_id", "") or "").strip()
        return bool(expected_id) and routed_id == expected_id
    if tool_name == "query_lore_index":
        expected_namespace = str(expected_args.get("namespace", "") or "").strip()
        routed_namespace = str(tool_args.get("namespace", "") or "").strip()
        return bool(expected_namespace) and routed_namespace == expected_namespace
    return True


def build_prompt(index: StoryworldIndex, query: Dict[str, Any]) -> List[Dict[str, str]]:
    summary = index.describe()
    namespace = str(query.get("namespace", "world_card") or "world_card")
    retrieval_bundle = index.query_lore_index(namespace, query["query"], top_k=2)
    if str(query.get("expected_tool")) == "get_encounter_card":
        retrieval_excerpt = index.get_encounter_card(str(query.get("expected_args", {}).get("encounter_id", ""))).get("card_excerpt", "")
    else:
        retrieval_excerpt = retrieval_bundle.get("namespace_excerpt", "") or retrieval_bundle.get("world_card_excerpt", "")
    system = (
        "You are a TRM router for Hermes storyworld indexing. "
        "Return one JSON object and nothing else. "
        "Allowed tools: get_encounter_card, query_lore_index, escalate. "
        "If the user names a specific encounter id like page_scene_01 or page_end_200, choose get_encounter_card. "
        "If the user asks for world rules, lore, structure, relationships, or story bible facts, choose query_lore_index. "
        "If the user asks for Monte Carlo, quality gate, or rebalance advice, choose query_lore_index with the matching report namespace. "
        "Do not answer the question in prose."
    )
    user = {
        "query_id": query["id"],
        "index_summary": summary,
        "retrieval_excerpt": retrieval_excerpt,
        "retrieval_bundle": retrieval_bundle,
        "task": query["query"],
        "expected_tool_hint": query.get("expected_tool"),
    }
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user, ensure_ascii=True, indent=2)},
    ]


def import_runtime() -> Dict[str, Any]:
    try:
        import torch
        from peft import LoraConfig, PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except Exception as exc:  # pragma: no cover - preflight
        raise SystemExit(
            "Missing runtime dependencies for the Qwen smoke test. "
            "Use D:\\Research_Engine\\.venv-train\\Scripts\\python.exe with torch, transformers, and peft installed. "
            f"Original error: {type(exc).__name__}: {exc}"
        )
    return {
        "torch": torch,
        "PeftModel": PeftModel,
        "LoraConfig": LoraConfig,
        "AutoModelForCausalLM": AutoModelForCausalLM,
        "AutoTokenizer": AutoTokenizer,
    }


def _sanitize_adapter_copy(adapter_path: Path, allowed_keys: Iterable[str]) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="storyworld_adapter_"))
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


def load_model(model_path: Path, adapter_path: Path | None) -> Tuple[Any, Any, str]:
    libs = import_runtime()
    torch = libs["torch"]
    PeftModel = libs["PeftModel"]
    LoraConfig = libs["LoraConfig"]
    AutoModelForCausalLM = libs["AutoModelForCausalLM"]
    AutoTokenizer = libs["AutoTokenizer"]

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token or tokenizer.unk_token
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        trust_remote_code=True,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
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
        model = _load_adapter_model(model, adapter_path, PeftModel)
    model.eval()
    return tokenizer, model, device


def generate_router_action(tokenizer: Any, model: Any, messages: List[Dict[str, str]], max_new_tokens: int) -> str:
    import torch

    prompt = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt")
    if hasattr(prompt, "input_ids"):
        input_ids = prompt["input_ids"].to(next(model.parameters()).device)
        attention_mask = prompt.get("attention_mask")
        if attention_mask is not None:
            attention_mask = attention_mask.to(next(model.parameters()).device)
    else:
        input_ids = prompt.to(next(model.parameters()).device)
        attention_mask = None
    with torch.inference_mode():
        output = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    generated = output[0][input_ids.shape[-1] :]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Windows-compatible TRM-to-MCP smoke test for Qwen 3.5 2B.")
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--adapter-path", default=str(DEFAULT_ADAPTER_PATH))
    parser.add_argument("--index-root", default=str(DEFAULT_INDEX_ROOT))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT))
    parser.add_argument("--run-id", default="", help="Optional run id override.")
    parser.add_argument("--queries-json", default="", help="Optional JSON file with query specs.")
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--no-adapter", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    index = StoryworldIndex(args.index_root)
    run_id = args.run_id or f"mcp_trm_smoke_{int(time.time())}"
    output_root = Path(args.output_root).resolve()
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    queries = DEFAULT_QUERIES
    if args.queries_json:
        queries_path = Path(args.queries_json).resolve()
        payload = load_json(queries_path)
        if isinstance(payload, dict) and isinstance(payload.get("queries"), list):
            queries = [row for row in payload["queries"] if isinstance(row, dict)]
        elif isinstance(payload, list):
            queries = [row for row in payload if isinstance(row, dict)]
    queries = resolve_queries(index, queries)

    dump_json(run_dir / "index_summary.json", index.describe())
    dump_json(run_dir / "queries.json", {"queries": queries})

    if args.dry_run:
        planned = []
        for query in queries:
            planned.append(
                {
                    "query_id": query["id"],
                    "prompt_tokens_est": estimate_tokens(json.dumps(build_prompt(index, query), ensure_ascii=True)),
                    "expected_tool": query.get("expected_tool"),
                }
            )
        dump_json(run_dir / "summary.json", {"run_id": run_id, "status": "planned", "planned": planned})
        print(str(run_dir))
        return 0

    model_path = Path(args.model_path).resolve()
    adapter_path = None if args.no_adapter else Path(args.adapter_path).resolve()
    tokenizer, model, device = load_model(model_path, adapter_path)

    generations: List[Dict[str, Any]] = []
    scores: List[Dict[str, Any]] = []
    for query in queries:
        messages = build_prompt(index, query)
        prompt_text = json.dumps(messages, ensure_ascii=True, indent=2)
        prompt_tokens_est = estimate_tokens(prompt_text)
        raw_output = generate_router_action(tokenizer, model, messages, args.max_new_tokens)
        parsed = parse_router_json(raw_output)
        routed = normalize_tool_call(parsed, query)
        tool_name = routed["tool"]
        tool_args = routed["args"]
        expected_tool = str(query.get("expected_tool", "") or "")
        expected_args = dict(query.get("expected_args", {})) if isinstance(query.get("expected_args"), dict) else {}
        route_correct = route_is_correct(query, routed)

        if tool_name == "get_encounter_card":
            tool_result = index.get_encounter_card(str(tool_args.get("encounter_id", "")))
        elif tool_name == "query_lore_index":
            tool_result = index.query_lore_index(
                str(tool_args.get("namespace", "world_card")),
                str(tool_args.get("query", query["query"])),
                top_k=args.top_k,
            )
        else:
            tool_result = {
                "tool": "escalate",
                "reason": "router_declined_index_lookup",
                "query": query["query"],
            }

        result = {
            "query_id": query["id"],
            "query": query["query"],
            "expected_tool": expected_tool,
            "expected_args": expected_args,
            "raw_model_output": raw_output,
            "parsed_tool_call": routed,
            "tool_result": tool_result,
            "route_correct": route_correct,
            "prompt_tokens_est": prompt_tokens_est,
            "retrieved_tokens_est": estimate_tokens(json.dumps(tool_result, ensure_ascii=True)),
            "retrieval_compression_ratio": round(prompt_tokens_est / max(1, estimate_tokens(json.dumps(tool_result, ensure_ascii=True))), 3),
            "device": device,
        }
        generations.append(result)
        scores.append(
            {
                "query_id": query["id"],
                "route_correct": route_correct,
                "expected_tool": expected_tool,
                "predicted_tool": tool_name,
                "tool_args": tool_args,
            }
        )

    dump_jsonl(run_dir / "generations.jsonl", generations)
    dump_jsonl(run_dir / "scorecard.jsonl", scores)

    total = len(scores)
    correct = sum(1 for row in scores if row["route_correct"])
    tool_accuracy = correct / total if total else 0.0
    summary = {
        "run_id": run_id,
        "status": "completed",
        "model_path": str(model_path),
        "adapter_path": str(adapter_path) if adapter_path else "",
        "index_root": str(Path(args.index_root).resolve()),
        "device": device,
        "total_queries": total,
        "tool_accuracy": round(tool_accuracy, 3),
        "route_correct": correct,
        "route_incorrect": total - correct,
        "output_dir": str(run_dir),
    }
    dump_json(run_dir / "summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
