param(
    [string]$WorkDir = "C:\projects\Hermes-Skills\Hermes Skills",
    [string]$BenchmarkRunId = "primehub-44env-9b27b-tuned-v2",
    [string]$LoopRunId = "primehub-trm-skill-loop-v4",
    [string]$RunRoot = "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v3_tuned_44env_v2",
    [string]$AuditSummary = "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_bridge_audit_full_v4\audit_prime_env_bridge.summary.json",
    [int]$BenchmarkMemoryLimitMb = 2048,
    [int]$BenchmarkCpuPercent = 50,
    [int]$MaxNewTokens = 256,
    [int]$RequestTimeout = 900,
    [int]$TaskTimeoutSeconds = 2400,
    [double]$MaxRuntimeMinutes = 1440,
    [string[]]$Exclude = @("passthrough", "verbatim_copy"),
    [int]$LoopCycles = 48,
    [int]$LoopSleepSeconds = 900,
    [int]$LoopMemoryLimitMb = 1024,
    [int]$LoopCpuPercent = 25,
    [string[]]$RunRoots = @(
        "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v1",
        "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v1_retry_27b_tail",
        "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v2_47env",
        "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_eligible_benchmark_v3_tuned_44env_v2"
    )
)

$ErrorActionPreference = "Stop"

function Normalize-List {
    param([string[]]$Items)
    $normalized = @()
    foreach ($item in $Items) {
        if (-not $item) {
            continue
        }
        $normalized += @($item -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    }
    return $normalized
}

function Start-DetachedPowerShell {
    param(
        [string]$RunId,
        [string]$ScriptPath,
        [string[]]$ScriptArgs
    )

    $logDir = Join-Path $WorkDir "data\job_limited_runs"
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
    $launcherStdout = Join-Path $logDir "$RunId.launcher.stdout.log"
    $launcherStderr = Join-Path $logDir "$RunId.launcher.stderr.log"
    Remove-Item $launcherStdout, $launcherStderr -Force -ErrorAction SilentlyContinue

    $commandParts = @("&", "'" + ($ScriptPath -replace "'", "''") + "'")
    foreach ($item in $ScriptArgs) {
        if ($item -match "^-") {
            $commandParts += $item
        } else {
            $commandParts += "'" + ($item -replace "'", "''") + "'"
        }
    }
    $commandText = $commandParts -join " "

    $proc = Start-Process powershell.exe `
        -WindowStyle Hidden `
        -ArgumentList (@(
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            $commandText
        )) `
        -WorkingDirectory $WorkDir `
        -RedirectStandardOutput $launcherStdout `
        -RedirectStandardError $launcherStderr `
        -PassThru

    return [pscustomobject]@{
        pid = $proc.Id
        launcher_stdout = $launcherStdout
        launcher_stderr = $launcherStderr
    }
}

$normalizedExclude = Normalize-List -Items $Exclude
$normalizedRunRoots = Normalize-List -Items $RunRoots
$benchEventLog = Join-Path $WorkDir "data\job_limited_runs\$BenchmarkRunId.events.jsonl"

$benchArgs = @(
    "-RunId", $BenchmarkRunId,
    "-MemoryLimitMb", $BenchmarkMemoryLimitMb.ToString(),
    "-CpuPercent", $BenchmarkCpuPercent.ToString(),
    "-WorkDir", $WorkDir,
    "-RunRoot", $RunRoot,
    "-AuditSummary", $AuditSummary,
    "-MaxNewTokens", $MaxNewTokens.ToString(),
    "-RequestTimeout", $RequestTimeout.ToString(),
    "-TaskTimeoutSeconds", $TaskTimeoutSeconds.ToString(),
    "-MaxRuntimeMinutes", $MaxRuntimeMinutes.ToString()
)
if ($normalizedExclude.Count -gt 0) {
    $benchArgs += @("-Exclude", ($normalizedExclude -join ","))
}

$benchLaunch = Start-DetachedPowerShell `
    -RunId $BenchmarkRunId `
    -ScriptPath (Join-Path $WorkDir "scripts\start_primehub_47env_resume.ps1") `
    -ScriptArgs $benchArgs

$loopArgs = @(
    "-RunId", $LoopRunId,
    "-Cycles", $LoopCycles.ToString(),
    "-SleepSeconds", $LoopSleepSeconds.ToString(),
    "-MemoryLimitMb", $LoopMemoryLimitMb.ToString(),
    "-CpuPercent", $LoopCpuPercent.ToString(),
    "-BenchmarkRunRoot", $RunRoot,
    "-WatchEventLog", $benchEventLog,
    "-RunRoots", ($normalizedRunRoots -join ",")
)

$loopLaunch = Start-DetachedPowerShell `
    -RunId $LoopRunId `
    -ScriptPath (Join-Path $WorkDir "scripts\start_primehub_trm_skill_loop.ps1") `
    -ScriptArgs $loopArgs

[pscustomobject]@{
    benchmark = $benchLaunch
    loop = $loopLaunch
    run_root = $RunRoot
    benchmark_event_log = $benchEventLog
} | ConvertTo-Json -Depth 6
