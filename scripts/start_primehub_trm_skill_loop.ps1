param(
    [string]$RunId = "primehub-trm-skill-loop",
    [int]$Cycles = 6,
    [int]$SleepSeconds = 300,
    [int]$MemoryLimitMb = 1024,
    [int]$CpuPercent = 25,
    [string]$BenchmarkRunRoot = "",
    [string]$WatchEventLog = "",
    [string[]]$RunRoots = @()
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$python = "C:\Python311\python.exe"
$logDir = Join-Path $root "data\job_limited_runs"
$summary = Join-Path $root "data\primehub_trm_autoresearch\latest.summary.json"
$ledger = Join-Path $root "data\primehub_trm_autoresearch\ledger.jsonl"
$latestImprintJson = Join-Path $root "data\primehub_trm_autoresearch\latest.skill_imprint.json"
$latestImprintMd = Join-Path $root "data\primehub_trm_autoresearch\latest.skill_imprint.md"

$commandArgs = @(
    "scripts/primehub_trm_autoresearch_loop.py",
    "--cycles", $Cycles.ToString(),
    "--sleep-seconds", $SleepSeconds.ToString(),
    "--work-base", "data/primehub_trm_autoresearch",
    "--summary", $summary,
    "--ledger", $ledger,
    "--latest-skill-imprint-json", $latestImprintJson,
    "--latest-skill-imprint-md", $latestImprintMd,
    "--publish-skill-sidecars"
)

if ($BenchmarkRunRoot) {
    $commandArgs += @("--benchmark-run-root", $BenchmarkRunRoot)
}

if ($WatchEventLog) {
    $commandArgs += @("--watch-event-log", $WatchEventLog)
}

$normalizedRunRoots = @()
foreach ($item in $RunRoots) {
    if (-not $item) {
        continue
    }
    $normalizedRunRoots += @($item -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

if ($normalizedRunRoots.Count -gt 0) {
    foreach ($runRoot in $normalizedRunRoots) {
        $commandArgs += @("--run-root", $runRoot)
    }
}

& (Join-Path $PSScriptRoot "run_with_job_limits.ps1") `
    -RunId $RunId `
    -MemoryLimitMb $MemoryLimitMb `
    -CpuPercent $CpuPercent `
    -WorkDir $root `
    -ExePath $python `
    -LogDir $logDir `
    -CommandArgs $commandArgs
