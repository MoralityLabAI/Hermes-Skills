param(
    [string]$RunId = "primehub-skill-reasoning-batch",
    [int]$MemoryLimitMb = 3072,
    [int]$CpuPercent = 50,
    [string]$WorkDir = "C:\projects\Hermes-Skills\Hermes Skills",
    [string]$RunRoot = "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_skill_reasoning_batch",
    [string]$AuditSummary = "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_bridge_audit_full_v4\audit_prime_env_bridge.summary.json",
    [string]$SkillBatchManifest = "C:\projects\Hermes-Skills\Hermes Skills\data\primehub_skill_batch_evolution\latest.manifest.json",
    [int]$MaxNewTokens = 256,
    [int]$RequestTimeout = 900,
    [int]$TaskTimeoutSeconds = 2400,
    [double]$MaxRuntimeMinutes = 600,
    [string]$ReasoningMode = "on",
    [string[]]$Variant = @(
        "single-model-baseline",
        "two-model-hard-reasoning-v1",
        "two-model-contract-repair-v1",
        "two-model-abstain-guard-v1",
        "three-model-basket-v3-reasoning-heavy"
    ),
    [string[]]$Exclude = @("passthrough", "verbatim_copy"),
    [switch]$ForceRerun
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

$audit = Get-Content $AuditSummary -Raw | ConvertFrom-Json
$skillManifest = Get-Content $SkillBatchManifest -Raw | ConvertFrom-Json

$eligible = @($audit.eligible_env_ids | ForEach-Object { [string]$_ } | Where-Object { $_ })
if ($eligible.Count -eq 0) {
    throw "No eligible_env_ids found in $AuditSummary"
}

$targetSet = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)
foreach ($clusterEntry in $skillManifest.env_clusters.PSObject.Properties) {
    foreach ($envId in @($clusterEntry.Value)) {
        if ($envId) {
            [void]$targetSet.Add([string]$envId)
        }
    }
}

$include = @()
foreach ($envId in $eligible) {
    if ($targetSet.Contains($envId)) {
        $include += $envId
    }
}
if ($include.Count -eq 0) {
    throw "No overlap between eligible envs and skill batch clusters."
}

$normalizedVariant = Normalize-List -Items $Variant
$normalizedExclude = Normalize-List -Items $Exclude

$benchArgs = @(
    "scripts/overnight_primehub_benchmark.py",
    "--env-mode",
    "primehub",
    "--model",
    "9b",
    "27b",
    "--reasoning-mode",
    $ReasoningMode,
    "--skill-batch-manifest",
    $SkillBatchManifest,
    "--include"
) + $include + @(
    "--variant"
) + $normalizedVariant + @(
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

$wrapperPath = Join-Path $WorkDir "scripts\run_with_job_limits.ps1"
$logDir = Join-Path $WorkDir "data\job_limited_runs"

& $wrapperPath `
    -RunId $RunId `
    -MemoryLimitMb $MemoryLimitMb `
    -CpuPercent $CpuPercent `
    -WorkDir $WorkDir `
    -ExePath "C:/Python311/python.exe" `
    -LogDir $logDir `
    -CommandArgs $benchArgs
