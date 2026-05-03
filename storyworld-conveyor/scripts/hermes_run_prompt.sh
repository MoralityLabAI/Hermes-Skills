#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <prompt_file_wsl> <loop_dir_wsl>" >&2
  exit 2
fi

PROMPT_FILE="$1"
LOOP_DIR="$2"
REPO_ROOT="/mnt/c/projects/GPTStoryworld"
WORK_DIR="/mnt/c/projects/GPTStoryworld"
SKILL_ROOT="$REPO_ROOT/hermes-skills/storyworld-conveyor/skills"
HERMES_SKILL_ROOT="$HOME/.hermes/skills/mlops/datasets"

mkdir -p "$LOOP_DIR"
mkdir -p "$LOOP_DIR/wsl_sessions"
mkdir -p "$LOOP_DIR/hermes_logs"
mkdir -p "$HERMES_SKILL_ROOT"

for skill_name in comprehensive-storyworld-building moral-quandary-storyworld-building storyworld-conveyor-runner storyworld-batch-auditor; do
  if [[ -d "$SKILL_ROOT/$skill_name" ]]; then
    rm -rf "$HERMES_SKILL_ROOT/$skill_name"
    cp -r "$SKILL_ROOT/$skill_name" "$HERMES_SKILL_ROOT/$skill_name"
  fi
done

cp "$PROMPT_FILE" "$LOOP_DIR/prompt.txt"
cp "$REPO_ROOT/hermes-skills/storyworld-conveyor/AGENTS.md" "$LOOP_DIR/AGENTS.storyworld-conveyor.md"
hermes skills list > "$LOOP_DIR/hermes_skills_list.txt" 2>&1 || true
hermes config show > "$LOOP_DIR/hermes_config.txt" 2>&1 || true

# Disable mid-run cross-model summarization for long conveyor loops.
export CONTEXT_COMPRESSION_ENABLED=false
export CONTEXT_COMPRESSION_THRESHOLD=0.90
unset CONTEXT_COMPRESSION_MODEL
unset CONTEXT_COMPRESSION_PROVIDER

# Keep the run rooted at the repo so edits, reports, and skills share one tree.
export BROWSER_INACTIVITY_TIMEOUT=120

cd "$WORK_DIR"
/mnt/c/projects/GPTStoryworld/tools/hermes_write_guard.sh pre > "$LOOP_DIR/preflight.log" 2>&1 || true

ls -t ~/.hermes/sessions/session_*.json 2>/dev/null | head -n 10 > "$LOOP_DIR/sessions_before.txt" || true

PROMPT="$(cat "$PROMPT_FILE")"
hermes chat -Q --yolo --pass-session-id -q "$PROMPT" > "$LOOP_DIR/hermes_stdout.log" 2> "$LOOP_DIR/hermes_stderr.log"

ls -t ~/.hermes/sessions/session_*.json 2>/dev/null | head -n 10 > "$LOOP_DIR/sessions_after.txt" || true

if [[ -f "$LOOP_DIR/sessions_after.txt" ]]; then
  while IFS= read -r session_path; do
    [[ -n "$session_path" ]] || continue
    cp "$session_path" "$LOOP_DIR/wsl_sessions/" || true
  done < "$LOOP_DIR/sessions_after.txt"
fi

if [[ -d ~/.hermes/logs ]]; then
  cp -r ~/.hermes/logs/. "$LOOP_DIR/hermes_logs/" 2>/dev/null || true
fi

if [[ -d ~/.hermes/cron ]]; then
  mkdir -p "$LOOP_DIR/hermes_cron"
  cp -r ~/.hermes/cron/. "$LOOP_DIR/hermes_cron/" 2>/dev/null || true
fi

if [[ -d "$REPO_ROOT/hermes-skills/storyworld-conveyor/factory_runs" ]]; then
  mkdir -p "$LOOP_DIR/factory_runs_snapshot"
  cp -r "$REPO_ROOT/hermes-skills/storyworld-conveyor/factory_runs/." "$LOOP_DIR/factory_runs_snapshot/" 2>/dev/null || true
fi

if [[ -d ~/.hermes/watchdog-logs ]]; then
  mkdir -p "$LOOP_DIR/watchdog_logs"
  cp -r ~/.hermes/watchdog-logs/. "$LOOP_DIR/watchdog_logs/" 2>/dev/null || true
fi
