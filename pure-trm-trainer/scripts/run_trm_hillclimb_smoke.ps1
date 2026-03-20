param(
  [string]$ConfigPath = "C:/projects/GPTStoryworld/hermes-skills/pure-trm-trainer/references/hillclimb-spec.smoke.json",
  [string]$RunId = "",
  [switch]$DryRun,
  [switch]$NoEval
)

$scriptPath = Join-Path $PSScriptRoot "run_trm_generalization_hillclimb.py"
if (-not (Test-Path $scriptPath)) {
  Write-Error "Missing runner: $scriptPath"
  exit 1
}

$effectiveConfigPath = $ConfigPath
if ($NoEval) {
  $tempConfigPath = Join-Path ([System.IO.Path]::GetTempPath()) ("trm_hillclimb_smoke_" + [System.Guid]::NewGuid().ToString("N") + ".json")
  $config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
  $config.PSObject.Properties.Remove("evaluation_command")
  $config.PSObject.Properties.Remove("evaluator_script")
  $config | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 $tempConfigPath
  $effectiveConfigPath = $tempConfigPath
}

$args = @(
  $scriptPath,
  "--config", $ConfigPath
)

if ($RunId -ne "") {
  $args += @("--run-id", $RunId)
}

if ($DryRun) {
  $args += "--dry-run"
}

if ($effectiveConfigPath -ne $ConfigPath) {
  $args[2] = $effectiveConfigPath
}

Write-Host "Launching TRM hill-climb smoke run with config: $effectiveConfigPath"
python @args
$exitCode = $LASTEXITCODE
if ($NoEval -and (Test-Path $effectiveConfigPath) -and $effectiveConfigPath -ne $ConfigPath) {
  Remove-Item $effectiveConfigPath -ErrorAction SilentlyContinue
}
exit $exitCode
