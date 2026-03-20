from __future__ import annotations

from typing import Any

from transformers import AutoConfig, AutoTokenizer


def normalize_rope_scaling(cfg: Any) -> dict[str, Any] | None:
    rope = getattr(cfg, "rope_scaling", None)
    if rope is None:
        return None
    if not isinstance(rope, dict):
        return {"raw": rope}

    normalized = dict(rope)
    rope_type = normalized.get("rope_type") or normalized.get("type")
    if rope_type is not None:
        normalized["rope_type"] = rope_type
        normalized["type"] = rope_type

    factor = normalized.get("factor")
    if factor is not None:
        try:
            normalized["factor"] = float(factor)
        except (TypeError, ValueError):
            pass

    cfg.rope_scaling = normalized
    return normalized


def load_patched_config(model_name: str) -> tuple[Any, Any, dict[str, Any]]:
    cfg = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    pad_id = getattr(cfg, "pad_token_id", None)
    if pad_id is None:
        pad_id = getattr(tok, "pad_token_id", None)
    if pad_id is None:
        pad_id = getattr(tok, "eos_token_id", None)
    if pad_id is None:
        pad_id = 0
    cfg.pad_token_id = int(pad_id)

    rope_scaling = normalize_rope_scaling(cfg)
    patch_meta: dict[str, Any] = {
        "pad_token_id": int(cfg.pad_token_id),
        "tokenizer_pad_token_id": getattr(tok, "pad_token_id", None),
        "tokenizer_eos_token_id": getattr(tok, "eos_token_id", None),
        "rope_scaling": rope_scaling,
        "max_position_embeddings": getattr(cfg, "max_position_embeddings", None),
        "rope_theta": getattr(cfg, "rope_theta", None),
        "config_class": type(cfg).__name__,
    }
    return cfg, tok, patch_meta
