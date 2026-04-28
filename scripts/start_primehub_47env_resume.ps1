param(
    [string]$RunId = "primehub-47env-9b27b-resume",
    [int]$MemoryLimitMb = 2048,
    [int]$CpuPercent = 50,
    [string]$WorkDir = "C:\projects\Hermes-Skills\Hermes Skills",
    [string]$RunRoot = "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v2_47env",
    [string]$AuditSummary = "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_bridge_audit_full_v4\audit_prime_env_bridge.summary.json",
    [int]$MaxNewTokens = 256,
    [int]$RequestTimeout = 900,
    [int]$TaskTimeoutSeconds = 2400,
    [double]$MaxRuntimeMinutes = 1440,
    [string[]]$Exclude = @(),
    [switch]$ForceRerun
)

$ErrorActionPreference = "Stop"

$summary = Get-Content $AuditSummary -Raw | ConvertFrom-Json
$include = @($summary.eligible_env_ids | ForEach-Object { [string]$_ } | Where-Object { $_ })
if ($include.Count -eq 0) {
    throw "No eligible_env_ids found in $AuditSummary"
}

$normalizedExclude = @()
foreach ($item in $Exclude) {
    if (-not $item) {
        continue
    }
    $normalizedExclude += @($item -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

$benchArgs = @(
    "scripts/overnight_primehub_benchmark.py",
    "--env-mode",
    "primehub",
    "--model",
    "9b",
    "27b",
    "--include"
) + $include + @(
    "--max-new-tokens",
    "$MaxNewTokens",
    "--request-timeout",
    "$RequestTimeout",
    "--task-timeout-seconds",
    "$TaskTimeoutSeconds",
    "--max-runtime-minutes",
    "$MaxRuntimeMinutes",
    "--run-root",
    $RunRoot
)

if ($normalizedExclude.Count -gt 0) {
    $benchArgs += "--exclude"
    $benchArgs += $normalizedExclude
}

if ($ForceRerun) {
    $benchArgs += "--force-rerun"
}

$wrapperPath = Join-Path $WorkDir "scripts/run_with_job_limits.ps1"
$logDir = Join-Path $WorkDir "data/job_limited_runs"

& $wrapperPath `
    -RunId $RunId `
    -MemoryLimitMb $MemoryLimitMb `
    -CpuPercent $CpuPercent `
    -WorkDir $WorkDir `
    -ExePath "C:/Python311/python.exe" `
    -LogDir $logDir `
    -CommandArgs $benchArgs
