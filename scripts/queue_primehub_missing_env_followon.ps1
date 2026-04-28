param(
    [string]$WaitEventLog = "C:\projects\Hermes-Skills\Hermes Skills\data\job_limited_runs\primehub-skill-reasoning-20260416-2100mdt.events.jsonl",
    [string]$RunId = "primehub-missing-envs-followon-20260419",
    [string]$WorkDir = "C:\projects\Hermes-Skills\Hermes Skills",
    [string]$RunRoot = "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_missing_envs_followon_20260419",
    [int]$MemoryLimitMb = 3072,
    [int]$CpuPercent = 50,
    [int]$PollSeconds = 60,
    [double]$MaxRuntimeMinutes = 480
)

$ErrorActionPreference = "Stop"

$missingEnvIds = @(
    "clbench",
    "coconot",
    "colf",
    "deep_consult",
    "if_summarize_judge",
    "llm_writing_detection",
    "longbench_v2",
    "misguided_attn",
    "mmlu",
    "reward_bench",
    "rust_cargo",
    "unscramble",
    "uq",
    "uq_project",
    "vpct_1",
    "writing_bench"
)

function Test-RunFinished {
    param([string]$EventLogPath)
    if (-not (Test-Path -LiteralPath $EventLogPath)) {
        return $false
    }
    $tail = Get-Content -LiteralPath $EventLogPath -Tail 20 -ErrorAction Stop
    foreach ($line in $tail) {
        if (-not $line) {
            continue
        }
        try {
            $obj = $line | ConvertFrom-Json -ErrorAction Stop
        } catch {
            continue
        }
        if ($obj.event -eq "finish") {
            return $true
        }
    }
    return $false
}

while (-not (Test-RunFinished -EventLogPath $WaitEventLog)) {
    Start-Sleep -Seconds $PollSeconds
}

$wrapperPath = Join-Path $WorkDir "scripts\run_with_job_limits.ps1"
$logDir = Join-Path $WorkDir "data\job_limited_runs"

$benchArgs = @(
    "scripts/overnight_primehub_benchmark.py",
    "--env-mode",
    "primehub",
    "--model",
    "9b",
    "27b",
    "--reasoning-mode",
    "on",
    "--variant",
    "single-model-baseline",
    "--include"
) + $missingEnvIds + @(
    "--max-new-tokens",
    "256",
    "--request-timeout",
    "900",
    "--task-timeout-seconds",
    "2400",
    "--max-runtime-minutes",
    "$MaxRuntimeMinutes",
    "--run-root",
    $RunRoot
)

& $wrapperPath `
    -RunId $RunId `
    -MemoryLimitMb $MemoryLimitMb `
    -CpuPercent $CpuPercent `
    -WorkDir $WorkDir `
    -ExePath "C:/Python311/python.exe" `
    -LogDir $logDir `
    -CommandArgs $benchArgs
