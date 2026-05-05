from __future__ import annotations

import argparse
import gc
import threading
import time
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from llama_cpp import Llama


def make_chat_response(raw: dict[str, Any], model_name: str, started: float) -> dict[str, Any]:
    choices = raw.get("choices") or []
    normalized_choices: list[dict[str, Any]] = []
    for index, choice in enumerate(choices):
        message = choice.get("message") or {}
        content = message.get("content")
        if content is None:
            content = choice.get("text") or ""
        normalized_choices.append(
            {
                "index": int(choice.get("index", index)),
                "message": {"role": "assistant", "content": str(content)},
                "finish_reason": choice.get("finish_reason", "stop"),
            }
        )
    if not normalized_choices:
        normalized_choices.append({"index": 0, "message": {"role": "assistant", "content": ""}, "finish_reason": "stop"})
    return {
        "id": raw.get("id") or f"chatcmpl-local-{int(started * 1000)}",
        "object": "chat.completion",
        "created": int(started),
        "model": model_name,
        "choices": normalized_choices,
        "usage": raw.get("usage") or {},
    }


def create_app(llm: Llama, model_name: str) -> FastAPI:
    app = FastAPI(title="local-llama-cpp-openai-shim")
    lock = threading.Lock()

    @app.get("/v1/models")
    def models() -> dict[str, Any]:
        return {"object": "list", "data": [{"id": model_name, "object": "model", "owned_by": "local"}]}

    @app.post("/v1/chat/completions")
    def chat_completions(payload: dict[str, Any]) -> dict[str, Any]:
        messages = payload.get("messages")
        if not isinstance(messages, list):
            raise HTTPException(status_code=400, detail="messages must be a list")
        started = time.time()
        with lock:
            try:
                raw = llm.create_chat_completion(
                    messages=messages,
                    temperature=float(payload.get("temperature", 0.2)),
                    top_p=float(payload.get("top_p", 0.95)),
                    max_tokens=int(payload.get("max_tokens", 256)),
                    stop=payload.get("stop") or [],
                    stream=False,
                    model=str(payload.get("model") or model_name),
                )
            except Exception as exc:  # pragma: no cover - depends on native llama runtime state
                raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}") from exc
        return make_chat_response(dict(raw), model_name, started)

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"status": "ok", "model": model_name}

    return app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve a llama-cpp GGUF through the small OpenAI-compatible subset used by local bootstrap benches.")
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--model-name", default="local-3b-gguf")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8084)
    parser.add_argument("--n-ctx", type=int, default=4096)
    parser.add_argument("--n-threads", type=int, default=6)
    parser.add_argument("--n-batch", type=int, default=128)
    parser.add_argument("--n-gpu-layers", type=int, default=0)
    parser.add_argument("--no-mmap", action="store_true")
    parser.add_argument("--mlock", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    llm: Llama | None = None
    try:
        llm = Llama(
            model_path=args.model_path,
            n_ctx=args.n_ctx,
            n_threads=args.n_threads,
            n_batch=args.n_batch,
            n_gpu_layers=args.n_gpu_layers,
            use_mmap=not args.no_mmap,
            use_mlock=args.mlock,
            verbose=False,
        )
        uvicorn.run(create_app(llm, args.model_name), host=args.host, port=args.port, log_level="info")
    finally:
        del llm
        gc.collect()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
