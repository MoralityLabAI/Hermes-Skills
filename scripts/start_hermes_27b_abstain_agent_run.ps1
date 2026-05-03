param(
    [string]$RunId = "hermes-27b-abstain-agent-run-20260503",
    [string]$WorkDir = "C:\projects\Hermes-Skills\Hermes Skills",
    [string]$RunRoot = "C:\projects\Hermes-Skills\Hermes Skills\data\hermes_27b_abstain_agent_run_20260503_live",
    [int]$MemoryLimitMb = 3072,
    [int]$CpuPercent = 50,
    [int]$MaxRuntimeMinutes = 480
)

$ErrorActionPreference = "Stop"

$benchArgs = @(
    "scripts\overnight_primehub_benchmark.py",
    "--env-mode", "primehub",
    "--model", "27b",
    "--reasoning-mode", "on",
    "--include", "agency_bench", "jailbreak_bench", "medsafetybench", "wmdp", "truthfulqa",
    "--variant", "single-model-baseline", "two-model-abstain-guard-v1", "two-model-contract-repair-v1",
    "--max-new-tokens", "256",
    "--request-timeout", "900",
    "--task-timeout-seconds", "2400",
    "--max-runtime-minutes", "$MaxRuntimeMinutes",
    "--run-root", $RunRoot,
    "--force-rerun"
)

$wrapperPath = Join-Path $WorkDir "scripts\run_with_job_limits.ps1"
$logDir = Join-Path $WorkDir "data\job_limited_runs"

& $wrapperPath `
    -RunId $RunId `
    -MemoryLimitMb $MemoryLimitMb `
    -CpuPercent $CpuPercent `
    -WorkDir $WorkDir `
    -ExePath "C:\Python311\python.exe" `
    -LogDir $logDir `
    -CommandArgs $benchArgs
