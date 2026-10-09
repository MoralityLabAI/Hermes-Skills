"""Bonsai 1-bit models on the PrismML llama-server, CPU only (-ngl 0), loopback port, reasoning off."""

from __future__ import annotations

import hashlib
import json
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

LLAMA_DIR = Path(r"C:\Users\patri\Documents\Codex\BitAgent-gym\llama-prism\bin")
MODELS = {
    "Bonsai-8B": Path(r"C:\Users\patri\Documents\Codex\BitAgent-gym\prime-artifacts\Bonsai-8B-Q1_0.gguf"),
    "Bonsai-27B": Path(r"C:\Users\patri\Documents\Codex\BitAgent-LatentBench\models\Bonsai-27B-Q1_0.gguf"),
    "Qwen2.5-3B": Path(r"C:\Users\patri\Documents\Codex\models\Qwen2.5-3B-Instruct-GGUF\qwen2.5-3b-instruct-q4_k_m.gguf"),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class Server:
    def __init__(self, model: str, threads: int = 8, slots: int = 1, ctx_per_slot: int = 4096):
        exe = LLAMA_DIR / "llama-server.exe"
        if not exe.exists():
            raise FileNotFoundError(f"{exe} missing (if Norton quarantined it, the user must restore it)")
        self.model = model
        self.path = MODELS[model]
        self.sha256 = sha256(self.path)
        self.port = _free_port()
        self.url = f"http://127.0.0.1:{self.port}"
        self.process = subprocess.Popen(
            [str(exe), "-m", str(self.path), "-ngl", "0", "-t", str(threads), "-c", str(ctx_per_slot * slots),
             "-np", str(slots), "--no-webui", "--alias", model, "--reasoning", "off", "--host", "127.0.0.1",
             "--port", str(self.port)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=str(LLAMA_DIR))
        deadline = time.monotonic() + 600
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(self.url + "/v1/models", timeout=10) as r:
                    names = [m.get("id") for m in json.loads(r.read()).get("data", [])]
                break
            except OSError:
                if self.process.poll() is not None:
                    raise RuntimeError("llama-server exited during startup")
                time.sleep(2)
        else:
            self.stop()
            raise TimeoutError("llama-server did not start")
        if names != [model]:
            self.stop()
            raise RuntimeError(f"server serves {names}, expected [{model}]")

    def _post(self, path: str, body: dict) -> dict:
        req = urllib.request.Request(self.url + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=1800) as r:
            return json.loads(r.read())

    def complete(self, prompt: str, n_predict: int, temperature: float = 0.0, seed: int = 0, stop=None) -> dict:
        body = {"prompt": prompt, "n_predict": n_predict, "temperature": temperature, "seed": seed, "cache_prompt": False}
        if temperature == 0.0:
            body["top_k"] = 1
        else:
            body["top_p"] = 0.95
        if stop:
            body["stop"] = stop
        return self._post("/completion", body)

    def chat(self, messages: list[dict], max_tokens: int = 64) -> dict:
        out = self._post("/v1/chat/completions", {"messages": messages, "max_tokens": max_tokens, "temperature": 0.0,
                                                  "top_k": 1, "seed": 0, "cache_prompt": False})
        return {"content": out["choices"][0]["message"].get("content") or "", "usage": out.get("usage", {})}

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.stop()
