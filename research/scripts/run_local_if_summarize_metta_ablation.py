"""Run a local MeTTa ablation for if_summarize_judge.

This is a local survivability benchmark for the paper addendum when the
Snacksack 9B endpoint is unavailable.  It uses direct llama.cpp inference
against a local GGUF model and scores with the env's deterministic fast-path
checks, avoiding remote judge/model calls.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import types
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(r"C:\projects\Hermes-Skills\Hermes Skills")
ENV_ROOT = Path(r"C:\projects\prime_intellect_research_environments\environments\if_summarize_judge")
PIPELINE_ROOT = ROOT / "metta-trm-hermes-pipeline"
REPAIR_SCRIPT_ROOT = PIPELINE_ROOT / "scripts"
DEFAULT_MODEL = Path(r"D:\research_engine\models\Qwen3.5\Qwen3.5-2B\Qwen3.5-2B-Q4_K_M.gguf")
DEFAULT_HF_MODEL = Path(r"D:\research_engine\models\Qwen3.5\Qwen3.5-0.8B-Instruct")
DEFAULT_OUT = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "local_eval_qwen35_2b_if_summarize_metta"
)
IF_BUNDLE_DIR = (
    ROOT
    / "research"
    / "studies"
    / "2026-04-22-metta-trm-hermes-pipeline"
    / "artifacts"
    / "if_summarize_judge_bundle"
)


def install_windows_fcntl_stub() -> None:
    if os.name != "nt" or "fcntl" in sys.modules:
        return
    fcntl = types.ModuleType("fcntl")
    fcntl.LOCK_EX = 1
    fcntl.LOCK_UN = 8
    fcntl.LOCK_NB = 4
    fcntl.flock = lambda *args, **kwargs: None
    sys.modules["fcntl"] = fcntl


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local if_summarize_judge MeTTa ablation.")
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL))
    parser.add_argument("--hf-model-path", default=str(DEFAULT_HF_MODEL))
    parser.add_argument("--backend", choices=["auto", "llama_cpp", "llama_cli", "transformers"], default="auto")
    parser.add_argument("--model-id", default="qwen35_local")
    parser.add_argument("--model-name", default="local-qwen")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--llama-cli-path", default=r"D:\research_engine\tools\llama.cpp-b8922-cuda12.4\llama-cli.exe")
    parser.add_argument("--llama-cli-gpu-layers", default="all")
    parser.add_argument("--llama-cli-timeout-sec", type=int, default=240)
    parser.add_argument("--llama-cli-max-prompt-chars", type=int, default=3500)
    parser.add_argument("--seed", type=int, action="append", default=None)
    parser.add_argument("--max-tokens", type=int, default=192)
    parser.add_argument("--ctx", type=int, default=4096)
    parser.add_argument("--threads", type=int, default=max(1, min(8, (os.cpu_count() or 4) // 2)))
    parser.add_argument("--gpu-layers", type=int, default=-1, help="llama.cpp GPU layers; -1 attempts full offload.")
    parser.add_argument("--transformers-device", choices=["auto", "cuda", "cpu"], default="auto")
    parser.add_argument("--transformers-quantization", choices=["auto", "none", "4bit", "8bit"], default="auto")
    parser.add_argument(
        "--allow-cpu-fallback",
        action="store_true",
        help="Permit auto mode to fall back to CPU/DRAM. Disabled by default to avoid accidental PC-wide memory pressure.",
    )
    parser.add_argument(
        "--allow-large-hf-load",
        action="store_true",
        help="Permit loading large HF safetensor checkpoints. Disabled by default because 4-bit HF loading can still spike DRAM.",
    )
    parser.add_argument("--large-hf-threshold-mb", type=int, default=2048)
    parser.add_argument("--torch-dtype", choices=["auto", "float32", "float16", "bfloat16"], default="auto")
    parser.add_argument("--dataset-name", default="kalomaze/glm-wikisummary-if-it4-think")
    parser.add_argument("--dataset-split", default="train")
    return parser.parse_args()


def write_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def load_if_env_module(dataset_name: str, dataset_split: str):
    install_windows_fcntl_stub()
    if str(ENV_ROOT) not in sys.path:
        sys.path.insert(0, str(ENV_ROOT))
    import if_summarize_judge  # type: ignore

    return if_summarize_judge


def load_repair_module():
    if str(REPAIR_SCRIPT_ROOT) not in sys.path:
        sys.path.insert(0, str(REPAIR_SCRIPT_ROOT))
    import metta_repair_pass  # type: ignore

    return metta_repair_pass


def load_runtime_env_payload() -> dict[str, Any]:
    packet = json.loads((IF_BUNDLE_DIR / "runtime_packet.json").read_text(encoding="utf-8"))
    env_payload = packet.get("envs", {}).get("if_summarize_judge")
    if not isinstance(env_payload, dict):
        raise RuntimeError("if_summarize_judge runtime packet missing env payload")
    return env_payload


def build_metta_skill_prompt(env_payload: dict[str, Any]) -> str:
    lines = [
        "You are operating as Hermes skill Primehub-Constraint-Summarize-v1.",
        "Classify the requested structural family before writing any summary text.",
        "Emit only the final constrained summary text with no explanations or wrapper prose.",
        "Treat structural compliance as the primary objective.",
        "",
        "Retrieved MeTTa contract memory for the current env:",
        f"- answer_shape: {env_payload.get('answer_shape', '')}",
        f"- summary: {env_payload.get('summary', '')}",
        f"- query_cues: {'; '.join(env_payload.get('query_cues') or [])}",
        f"- must_do: {'; '.join(env_payload.get('must_do') or [])}",
        f"- avoid: {'; '.join(env_payload.get('avoid') or [])}",
        f"- validation_path: {env_payload.get('validation_path', '')}",
        f"- repair_focus: {'; '.join(env_payload.get('repair_focus') or [])}",
        "",
        "Profile lookup table:",
    ]
    profiles = env_payload.get("profiles") or {}
    for profile_id in sorted(profiles):
        profile = profiles[profile_id]
        if not isinstance(profile, dict):
            continue
        cues = "; ".join(profile.get("query_cues") or [])
        lines.append(f"- {profile_id}: {profile.get('summary', '')} | cues: {cues}")
    lines.extend(
        [
            "",
            "Use this contract memory privately to classify the active structural family.",
            "Then satisfy that family exactly and emit only the final constrained summary text.",
        ]
    )
    return "\n".join(lines).strip()


def get_seed_example(if_env: Any, seed: int, dataset_name: str, dataset_split: str) -> dict[str, Any]:
    builder = if_env.get_dataset_builder(dataset_name=dataset_name, dataset_split=dataset_split, seed=seed)
    dataset = builder()
    if len(dataset) < 1:
        raise RuntimeError(f"dataset builder returned no rows for seed {seed}")
    row = dict(dataset[0])
    info = dict(row.get("info") or {})
    prompt = row.get("prompt") or []
    user_text = ""
    if prompt and isinstance(prompt[0], dict):
        user_text = str(prompt[0].get("content") or "")
    row["info"] = info
    row["user_text"] = user_text
    return row


def flatten_response(raw: Any) -> str:
    try:
        content = raw["choices"][0]["message"]["content"]
    except Exception:
        try:
            content = raw["choices"][0]["text"]
        except Exception:
            content = str(raw)
    return str(content or "").strip()


class LocalGenerator:
    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> tuple[str, dict[str, Any], float]:
        raise NotImplementedError


class LlamaCppGenerator(LocalGenerator):
    def __init__(self, model_path: Path, ctx: int, threads: int, gpu_layers: int):
        if os.name == "nt":
            try:
                import torch

                torch_lib = Path(torch.__file__).resolve().parent / "lib"
                if torch_lib.exists():
                    os.add_dll_directory(str(torch_lib))
                    os.environ["PATH"] = str(torch_lib) + os.pathsep + os.environ.get("PATH", "")
            except Exception:
                pass
        from llama_cpp import Llama

        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=ctx,
            n_threads=threads,
            n_gpu_layers=gpu_layers,
            verbose=False,
        )

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> tuple[str, dict[str, Any], float]:
        start = time.time()
        raw = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.0,
            top_p=1.0,
        )
        elapsed = round(time.time() - start, 4)
        return flatten_response(raw), raw, elapsed


class LlamaCliGenerator(LocalGenerator):
    def __init__(
        self,
        llama_cli_path: Path,
        model_path: Path,
        ctx: int,
        threads: int,
        gpu_layers: str,
        timeout_sec: int,
        max_prompt_chars: int,
    ):
        self.llama_cli_path = llama_cli_path
        self.model_path = model_path
        self.ctx = ctx
        self.threads = threads
        self.gpu_layers = gpu_layers
        self.timeout_sec = timeout_sec
        self.max_prompt_chars = max_prompt_chars

    @staticmethod
    def render_prompt(messages: list[dict[str, str]]) -> str:
        system_parts = [item["content"] for item in messages if item.get("role") == "system"]
        user_parts = [item["content"] for item in messages if item.get("role") == "user"]
        system_text = "\n\n".join(system_parts).strip() or "You are a helpful assistant."
        user_text = "\n\n".join(user_parts).strip()
        return (
            "<|im_start|>system\n"
            f"{system_text}<|im_end|>\n"
            "<|im_start|>user\n"
            f"{user_text}<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> tuple[str, dict[str, Any], float]:
        import tempfile
        import subprocess
        import psutil

        prompt = self.render_prompt(messages)
        if len(prompt) > self.max_prompt_chars:
            raise RuntimeError(
                f"llama-cli prompt too long for safety budget: {len(prompt)} chars > {self.max_prompt_chars}"
            )
        tool_path = self.llama_cli_path
        if tool_path.name.lower() == "llama-cli.exe":
            completion_path = tool_path.with_name("llama-completion.exe")
            if completion_path.exists():
                tool_path = completion_path
        cmd = [
            str(tool_path),
            "-m",
            str(self.model_path),
            "-ngl",
            str(self.gpu_layers),
            "-c",
            str(self.ctx),
            "-t",
            str(self.threads),
            "-b",
            "512",
            "-ub",
            "128",
            "-n",
            str(max_tokens),
            "--no-warmup",
            "-ctk",
            "q8_0",
            "-ctv",
            "q8_0",
            "--temp",
            "0",
            "--top-p",
            "1",
            "--no-display-prompt",
            "--no-conversation",
            "--single-turn",
            "-p",
            prompt,
        ]
        start = time.time()
        stdout_fd, stdout_name = tempfile.mkstemp(prefix="llama_cli_stdout_", suffix=".log")
        stderr_fd, stderr_name = tempfile.mkstemp(prefix="llama_cli_stderr_", suffix=".log")
        os.close(stdout_fd)
        os.close(stderr_fd)
        stdout_path = Path(stdout_name)
        stderr_path = Path(stderr_name)
        peak_child_ram_mb = 0.0
        with stdout_path.open("w", encoding="utf-8", errors="replace") as stdout_handle, stderr_path.open(
            "w", encoding="utf-8", errors="replace"
        ) as stderr_handle:
            proc = subprocess.Popen(cmd, stdout=stdout_handle, stderr=stderr_handle, text=True)
            ps_proc = psutil.Process(proc.pid)
            while proc.poll() is None:
                if time.time() - start > self.timeout_sec:
                    proc.kill()
                    proc.wait(timeout=10)
                    stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
                    stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
                    raise TimeoutError(
                        f"llama-cli exceeded {self.timeout_sec}s; stdout_tail={stdout[-1000:]}; stderr_tail={stderr[-2000:]}"
                    )
                try:
                    peak_child_ram_mb = max(peak_child_ram_mb, ps_proc.memory_info().rss / (1024 * 1024))
                except Exception:
                    pass
                time.sleep(1.0)
        stdout = stdout_path.read_text(encoding="utf-8", errors="replace")
        stderr = stderr_path.read_text(encoding="utf-8", errors="replace")
        elapsed = round(time.time() - start, 4)
        if proc.returncode != 0:
            raise RuntimeError(f"llama-cli exited {proc.returncode}: {stderr[-2000:]}")
        raw = {
            "cli": str(tool_path),
            "returncode": proc.returncode,
            "peak_child_ram_mb": round(peak_child_ram_mb, 4),
            "stderr_tail": stderr[-4000:],
        }
        return stdout.strip(), raw, elapsed


class TransformersGenerator(LocalGenerator):
    def __init__(self, model_path: Path, device: str, dtype: str, quantization: str, allow_cpu_fallback: bool):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        cuda_available = torch.cuda.is_available()
        if device == "cuda" and not cuda_available:
            raise RuntimeError("CUDA requested but torch.cuda.is_available() is false")
        if device == "cpu":
            selected_device = "cpu"
        elif cuda_available:
            selected_device = "cuda"
        elif allow_cpu_fallback:
            selected_device = "cpu"
        else:
            raise RuntimeError("CUDA unavailable and --allow-cpu-fallback was not set")

        if dtype == "auto" and selected_device == "cuda":
            torch_dtype: str | Any = torch.float16
        elif dtype == "auto":
            torch_dtype = "auto"
        elif dtype == "float16":
            torch_dtype = torch.float16
        elif dtype == "bfloat16":
            torch_dtype = torch.bfloat16
        else:
            torch_dtype = torch.float32

        quantization_config = None
        selected_quantization = "none"
        requested_quantization = "4bit" if quantization == "auto" and selected_device == "cuda" else quantization
        if requested_quantization in {"4bit", "8bit"}:
            if selected_device != "cuda":
                raise RuntimeError(f"{requested_quantization} quantization requires CUDA; refusing CPU/DRAM fallback")
            from transformers import BitsAndBytesConfig

            if requested_quantization == "4bit":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )
            else:
                quantization_config = BitsAndBytesConfig(load_in_8bit=True)
            selected_quantization = requested_quantization

        if selected_device == "cuda":
            device_map = "cuda:0"
        else:
            device_map = "cpu"
        self.selected_device = selected_device
        self.selected_quantization = selected_quantization
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path), local_files_only=True)
        load_kwargs: dict[str, Any] = {
            "local_files_only": True,
            "torch_dtype": torch_dtype,
            "device_map": device_map,
            "low_cpu_mem_usage": True,
        }
        if quantization_config is not None:
            load_kwargs["quantization_config"] = quantization_config
        self.model = AutoModelForCausalLM.from_pretrained(str(model_path), **load_kwargs)
        self.model.eval()

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> tuple[str, dict[str, Any], float]:
        start = time.time()
        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            prompt = "\n\n".join(f"{item['role'].upper()}: {item['content']}" for item in messages) + "\n\nASSISTANT:"
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {key: value.to(self.model.device) for key, value in inputs.items()}
        input_tokens = int(inputs["input_ids"].shape[-1])
        with self.torch.inference_mode():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated = output[0][input_tokens:]
        text = self.tokenizer.decode(generated, skip_special_tokens=True).strip()
        elapsed = round(time.time() - start, 4)
        raw = {
            "usage": {
                "prompt_tokens": input_tokens,
                "completion_tokens": int(generated.shape[-1]),
                "total_tokens": int(output.shape[-1]),
            }
        }
        return text, raw, elapsed


def build_generator(args: argparse.Namespace) -> tuple[LocalGenerator, str, Path]:
    model_path = Path(args.model_path).resolve()
    hf_model_path = Path(args.hf_model_path).resolve()
    backend = str(args.backend)
    if backend == "llama_cli":
        llama_cli_path = Path(args.llama_cli_path).resolve()
        if not llama_cli_path.exists():
            raise SystemExit(f"llama-cli not found: {llama_cli_path}")
        if not model_path.exists():
            raise SystemExit(f"GGUF model not found: {model_path}")
        return (
            LlamaCliGenerator(
                llama_cli_path,
                model_path,
                args.ctx,
                args.threads,
                args.llama_cli_gpu_layers,
                args.llama_cli_timeout_sec,
                args.llama_cli_max_prompt_chars,
            ),
            "llama_cli_external_cuda_gguf",
            model_path,
        )
    if backend in {"auto", "llama_cpp"} and model_path.exists() and model_path.suffix.lower() == ".gguf":
        try:
            return LlamaCppGenerator(model_path, args.ctx, args.threads, args.gpu_layers), "llama_cpp_direct_local", model_path
        except Exception as exc:
            if backend == "llama_cpp":
                raise
            print(f"llama_cpp unavailable, falling back to transformers: {exc}", file=sys.stderr)
    if not hf_model_path.exists():
        raise SystemExit(f"HF fallback model not found: {hf_model_path}")
    safetensor_bytes = sum(path.stat().st_size for path in hf_model_path.glob("*.safetensors"))
    safetensor_mb = safetensor_bytes / (1024 * 1024)
    if safetensor_mb > args.large_hf_threshold_mb and not args.allow_large_hf_load:
        raise SystemExit(
            "Refusing large HF safetensor load "
            f"({safetensor_mb:.1f} MB > {args.large_hf_threshold_mb} MB). "
            "Use a quantized GGUF for low-DRAM runs, or pass --allow-large-hf-load for an explicit DRAM-heavy fallback."
        )
    generator = TransformersGenerator(
        hf_model_path,
        args.transformers_device,
        args.torch_dtype,
        args.transformers_quantization,
        args.allow_cpu_fallback,
    )
    backend_name = f"transformers_direct_local_{generator.selected_device}_{generator.selected_quantization}"
    return generator, backend_name, hf_model_path


def generate(llm: LocalGenerator, messages: list[dict[str, str]], max_tokens: int) -> tuple[str, dict[str, Any], float]:
    start = time.time()
    text, raw, elapsed = llm.generate(messages, max_tokens)
    return text, raw, round(time.time() - start, 4) if elapsed is None else elapsed


def score(if_env: Any, constraint_type: str, text: str) -> tuple[float, str]:
    score_value, note = if_env._deterministic_constraint_check(constraint_type, text)
    if score_value < 0.0:
        return 0.0, "NO_FASTPATH_LOCAL_JUDGE_DISABLED"
    return float(score_value), str(note)


def summarize_raw(raw: Any) -> Any:
    if not isinstance(raw, dict):
        return None
    usage = raw.get("usage")
    if usage is not None:
        return usage
    return {
        key: raw.get(key)
        for key in ["cli", "returncode", "peak_child_ram_mb", "stderr_tail"]
        if key in raw
    }


def render_md(results: list[dict[str, Any]], blockers: list[dict[str, Any]], backend_name: str) -> str:
    lines = [
        "# Local if_summarize_judge MeTTa Ablation",
        "",
        f"This run is local-only and uses `{backend_name}` inference, not the lost Snacksack endpoint.",
        "",
        "| Arm | Episodes | Reward Total | Avg Reward | Mean Seconds |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    by_arm: dict[str, list[dict[str, Any]]] = {}
    for row in results:
        by_arm.setdefault(row["arm_id"], []).append(row)
    for arm_id in sorted(by_arm):
        rows = by_arm[arm_id]
        total = sum(float(row["reward"]) for row in rows)
        mean_sec = sum(float(row["generation_sec"]) for row in rows if row.get("generation_sec") is not None) / max(1, len(rows))
        lines.append(f"| `{arm_id}` | {len(rows)} | {total:.4f} | {total / max(1, len(rows)):.4f} | {mean_sec:.4f} |")
    lines.extend(
        [
            "",
            "## Per-Seed Rows",
            "",
            "| Seed | Constraint | Arm | Reward | Judge Note | Action Excerpt |",
            "| ---: | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in results:
        action = " ".join(str(row.get("action") or "").split())
        if len(action) > 120:
            action = action[:117] + "..."
        action = action.replace("|", "\\|")
        lines.append(
            f"| {row['seed']} | `{row['constraint_type']}` | `{row['arm_id']}` | {float(row['reward']):.4f} | {row['judge_note']} | {action} |"
        )
    if blockers:
        lines.extend(["", "## Local Blockers", "", "| Env | Reason |", "| --- | --- |"])
        for blocker in blockers:
            lines.append(f"| `{blocker['env_id']}` | {blocker['reason']} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    seeds = args.seed or [7, 11, 19]
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    events_path = out_dir / "local_if_summarize_metta.events.jsonl"
    if events_path.exists():
        events_path.unlink()

    requested_model_path = Path(args.model_path).resolve()
    if not requested_model_path.exists() and args.backend == "llama_cpp":
        raise SystemExit(f"model not found: {requested_model_path}")

    plan = {
        "training_task_id": "local-if-summarize-metta-controlled-slice",
        "checkpoint_interval": "per_seed_arm",
        "chunk_strategy": "single local model load; one deterministic episode per seed per arm",
        "caps_expected": {"ram_mb": 2048, "cpu_pct": 50, "io_mb_s": 50},
        "model_path": str(requested_model_path),
        "hf_model_path": str(Path(args.hf_model_path).resolve()),
        "seeds": seeds,
        "created_at_utc": utc_now(),
    }
    (out_dir / "local_if_summarize_metta.plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    write_jsonl(events_path, {"event": "start", **plan})

    if_env = load_if_env_module(args.dataset_name, args.dataset_split)
    repair = load_repair_module()
    env_payload = load_runtime_env_payload()
    metta_prompt = build_metta_skill_prompt(env_payload)

    blockers = [
        {
            "env_id": "psycho_bench",
            "reason": "not present in local Prime env checkout; previous runner depended on Snacksack community env bridge",
        },
        {
            "env_id": "ascii_tree",
            "reason": "not present in local Prime env checkout; previous runner depended on Snacksack community env bridge",
        },
        {
            "env_id": "pydantic_adherence",
            "reason": "not present in local Prime env checkout; previous runner depended on Snacksack community env bridge",
        },
    ]

    llm, backend_name, actual_model_path = build_generator(args)

    results: list[dict[str, Any]] = []
    examples = [
        get_seed_example(if_env, seed, args.dataset_name, args.dataset_split)
        for seed in seeds
    ]
    for seed, example in zip(seeds, examples):
        seed = int(seed)
        user_text = str(example["user_text"])
        info = dict(example.get("info") or {})
        constraint_type = str(info.get("constraint_type") or "")

        arms = [
            ("without_metta", [{"role": "user", "content": user_text}]),
            (
                "with_metta_runtime",
                [
                    {"role": "system", "content": metta_prompt},
                    {"role": "user", "content": user_text},
                ],
            ),
        ]
        runtime_candidate = ""
        runtime_raw: dict[str, Any] | None = None
        runtime_elapsed = 0.0
        for arm_id, messages in arms:
            action, raw, elapsed = generate(llm, messages, args.max_tokens)
            reward, judge_note = score(if_env, constraint_type, action)
            if arm_id == "with_metta_runtime":
                runtime_candidate = action
                runtime_raw = raw
                runtime_elapsed = elapsed
            row = {
                "seed": seed,
                "arm_id": arm_id,
                "env_id": "if_summarize_judge",
                "constraint_type": constraint_type,
                "constraint": info.get("constraint", ""),
                "reward": reward,
                "judge_note": judge_note,
                "action": action,
                "generation_sec": elapsed,
                "raw_usage": summarize_raw(raw),
                "success": True,
            }
            results.append(row)
            write_jsonl(events_path, {"event": "episode", "ts": utc_now(), **row})

        repair_report = repair.repair_candidate(
            "if_summarize_judge",
            runtime_candidate,
            env_payload,
            observation_text=user_text,
        )
        repaired_action = str(repair_report.get("repaired_text") or "")
        repaired_reward, repaired_note = score(if_env, constraint_type, repaired_action)
        repaired_row = {
            "seed": seed,
            "arm_id": "with_metta_runtime_repair",
            "env_id": "if_summarize_judge",
            "constraint_type": constraint_type,
            "constraint": info.get("constraint", ""),
            "reward": repaired_reward,
            "judge_note": repaired_note,
            "action": repaired_action,
            "generation_sec": runtime_elapsed,
            "raw_usage": summarize_raw(runtime_raw),
            "repair_report": repair_report,
            "success": True,
        }
        results.append(repaired_row)
        write_jsonl(events_path, {"event": "episode", "ts": utc_now(), **repaired_row})

    payload = {
        "generated_at_utc": utc_now(),
        "model": {
            "model_id": args.model_id,
            "model_name": args.model_name,
            "model_path": str(actual_model_path),
            "backend": backend_name,
        },
        "envs": ["if_summarize_judge"],
        "blocked_envs": blockers,
        "results": results,
    }
    results_json = out_dir / "local_if_summarize_metta.results.json"
    results_md = out_dir / "local_if_summarize_metta.results.md"
    results_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    results_md.write_text(render_md(results, blockers, backend_name), encoding="utf-8")
    write_jsonl(events_path, {"event": "finish", "ts": utc_now(), "results_json": str(results_json)})
    print(results_json)
    print(results_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
