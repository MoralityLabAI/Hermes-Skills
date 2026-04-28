# llama-cli 3B Probe Postmortem

Date: 2026-04-24

## What Happened

Two Qwen2.5-3B Q4_K_M `llama-cli` probes were interrupted before a clean benchmark receipt was written.

The GPU was clear after interruption (`0 MB / 4096 MB` used) and no `llama-cli` process remained.

## Root Cause

The unsafe part was the wrapper integration, not the GGUF model file itself.

First wrapper issue:

- The Python wrapper spawned `nvidia-smi` repeatedly inside the generation loop.
- The wrapper captured `llama-cli` stdout/stderr through pipes but did not drain them while the child process was running.
- `llama-cli` writes verbose model-load logs to stderr, so the pipe can fill and stall the child process.
- The observed traceback ended inside the wrapper's `nvidia-smi` polling subprocess after a `KeyboardInterrupt`.

Second wrapper issue:

- The safety probe used `--ctx 256`, but the first benchmark prompt was `576 tokens`.
- `llama-cli` rejected the prompt, entered interactive conversation mode, and waited for input.
- The session interrupt then appeared as another `KeyboardInterrupt`.
- The model memory itself looked acceptable in the captured llama.cpp breakdown: `CUDA0 self 1914 MiB`, `model 1834 MiB`, `context 4 MiB`, `Host 169 MiB`.

## Fix Applied

- Removed in-loop `nvidia-smi` polling from the `llama_cli` backend.
- Redirected `llama-cli` stdout/stderr to temp files instead of pipes, preventing pipe backpressure deadlock.
- Kept a hard per-generation timeout.
- Kept child RSS monitoring through `psutil` only.
- Added `--no-conversation` and `--single-turn` so context/prompt errors exit instead of opening an interactive REPL.

## Safety Gate

The corrected safety probe should use:

- `--max-tokens 1`
- `--ctx 1024`
- `--llama-cli-timeout-sec 60`
- capped wrapper with `2048 MB RAM`, `50% CPU`, `50 MB/s IO`

Outcome:

- `ctx 1024` succeeded for the no-MeTTa arm but failed cleanly for the MeTTa arm because the MeTTa prompt was `1342 tokens`, exceeding the `1020` usable token budget.
- `ctx 2048` with `--llama-cli-max-prompt-chars 7000` completed for seed `7` with `max_tokens 1`.
- The completed run used `Qwen2.5-3B-Instruct-Q4_K_M` through llama.cpp CUDA and produced `0.0000 / 0.0000 / 1.0000` for no-MeTTa / runtime / runtime+repair.
- The outer job monitor reported `2488.418 MB` peak working set, but llama.cpp's own memory breakdown from the probe showed the intended VRAM-first placement: approximately `1834 MiB` model on CUDA and `166-169 MiB` host mapped model memory.

Do not scale beyond `max_tokens 1` without accepting that the Windows job-object working-set receipt may exceed the nominal `2048 MB` cap even though llama.cpp reports low host model memory.
