import argparse
import json
from pathlib import Path

from datasets import load_dataset


def _as_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(f"{k}: {v}" for k, v in value.items())
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value)


def _reasoning_text(row) -> str:
    for key in ("think_block", "reasoning", "reasoning_block", "rationale", "chain_of_thought", "cot"):
        value = row.get(key)
        if value not in (None, "", []):
            return _as_text(value).strip()
    return ""


def _with_think_block(reasoning: str, answer: str, fallback: str) -> str:
    body = reasoning.strip() if reasoning.strip() else fallback.strip()
    if not body:
        return answer.strip()
    if "<think>" in body.lower():
        return body if answer.strip() in body else f"{body}\n\n{answer.strip()}".strip()
    return f"<think>\n{body}\n</think>\n\n{answer.strip()}".strip()


def _mcqa_choices(row) -> str:
    choices = row.get("choices", [])
    rendered = []
    labels = "ABCD"
    if isinstance(choices, dict):
        texts = choices.get("text", [])
        labels_list = choices.get("label", [])
        for idx, text in enumerate(texts):
            label = labels_list[idx] if idx < len(labels_list) else labels[min(idx, len(labels) - 1)]
            rendered.append(f"{label}. {text}")
    elif isinstance(choices, list):
        for idx, choice in enumerate(choices):
            label = labels[min(idx, len(labels) - 1)]
            text = choice.get("text", "") if isinstance(choice, dict) else choice
            rendered.append(f"{label}. {text}")
    return "\n".join(rendered)


def _mcqa_answer(row) -> str:
    raw = row.get("answerKey", row.get("answer", ""))
    if isinstance(raw, int):
        return "ABCD"[raw] if 0 <= raw < 4 else str(raw)
    text = str(raw).strip()
    if text in {"0", "1", "2", "3"}:
        return "ABCD"[int(text)]
    return text


def _row_to_messages(spec, row):
    kind = spec["kind"]
    prefix = spec.get("prompt_prefix", "").strip()

    if kind == "chat":
        prompt = row.get("prompt", [])
        completion = row.get("completion", [])
        if not isinstance(prompt, list) or not isinstance(completion, list):
            raise ValueError(f"{spec['name']}: expected prompt/completion lists")
        return list(prompt) + list(completion)

    if kind == "qa":
        parts = []
        if prefix:
            parts.append(prefix)
        info = row.get("info")
        if info not in (None, "", []):
            parts.append(f"Context:\n{_as_text(info)}")
        parts.append(f"Question:\n{_as_text(row.get('question', ''))}")
        answer = _as_text(row.get("answer", "")).strip()
        assistant = _with_think_block(
            _reasoning_text(row),
            answer,
            "Read the question carefully, use the provided context, and give the final answer directly.",
        )
        return [
            {"role": "system", "content": "You are a careful assistant. Answer the user directly."},
            {"role": "user", "content": "\n\n".join(parts).strip()},
            {"role": "assistant", "content": assistant},
        ]

    if kind == "mcqa":
        parts = []
        if prefix:
            parts.append(prefix)
        subject = _as_text(row.get("subject", "")).strip()
        if subject:
            parts.append(f"Subject: {subject}")
        parts.append(f"Question:\n{_as_text(row.get('question', ''))}")
        parts.append(f"Choices:\n{_mcqa_choices(row)}")
        parts.append("Return only the answer letter.")
        assistant = _with_think_block(
            _reasoning_text(row),
            _mcqa_answer(row),
            "Eliminate the incorrect choices and return the best remaining answer letter.",
        )
        return [
            {"role": "system", "content": "You are a careful assistant. Answer with one choice letter only."},
            {"role": "user", "content": "\n\n".join(parts).strip()},
            {"role": "assistant", "content": assistant},
        ]

    if kind == "code":
        prompt = _as_text(row.get("prompt", row.get("text", ""))).strip()
        if prefix:
            prompt = f"{prefix}\n\n{prompt}"
        assistant = _with_think_block(
            _reasoning_text(row),
            _as_text(row.get("code", "")).strip(),
            "Write the requested code and return code only.",
        )
        return [
            {"role": "system", "content": "You are a careful coding assistant. Return code only."},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": assistant},
        ]

    raise ValueError(f"Unknown kind: {kind}")


def build_dataset(spec, out_dir: Path) -> dict:
    source_root = Path(spec["source_root"])
    config_name = spec.get("config_name")
    split = spec.get("split", "train")
    limit = spec.get("limit")
    data_glob = spec.get("data_glob")

    if data_glob:
        files = sorted(source_root.glob(data_glob))
        if not files:
            raise SystemExit(f"No files matched {source_root / data_glob}")
        ds = load_dataset("parquet", data_files=[str(p) for p in files], split="train")
    else:
        if not config_name:
            raise SystemExit(f"{spec['name']}: config_name is required when data_glob is absent")
        ds = load_dataset(str(source_root), name=config_name, split=split)

    if limit:
        ds = ds.select(range(min(limit, len(ds))))

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "train.jsonl"
    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for row in ds:
            f.write(json.dumps({"messages": _row_to_messages(spec, row)}, ensure_ascii=True) + "\n")
            count += 1

    return {
        "name": spec["name"],
        "source_root": str(source_root),
        "config_name": config_name,
        "split": split,
        "kind": spec["kind"],
        "limit": limit,
        "records": count,
        "out_path": str(out_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build QLoRA-ready JSONL datasets from environment exports.")
    ap.add_argument("--spec-json", required=True)
    ap.add_argument("--out-root", required=True)
    args = ap.parse_args()

    spec = json.loads(Path(args.spec_json).read_text(encoding="utf-8"))
    envs = spec.get("envs", [])
    if not envs:
        raise SystemExit(f"No envs found in {args.spec_json}")

    out_root = Path(args.out_root)
    built = []
    for env in envs:
        built.append(build_dataset(env, out_root / env["name"]))

    (out_root / "manifest.json").write_text(json.dumps({"envs": built}, indent=2), encoding="utf-8")
    print(out_root / "manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
