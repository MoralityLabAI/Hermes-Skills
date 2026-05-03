# Windows wrapper for the Hermes storyworld MCP + TRM smoke test.

param(
    [string]$ModelPath = "D:\Research_Engine\models\Qwen3.5\Qwen3.5-2B-HF",
    [string]$AdapterPath = "D:\Research_Engine\storyworld_qlora\adapters\qwen35-2b-usual-suspects-local-r2-checkpoint13",
    [string]$IndexRoot = "C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\factory_runs\the_usual_suspects_qwen35_2b_run\indices\encounter_index",
    [string]$OutputRoot = "C:\projects\GPTStoryworld\hermes-skills\storyworld-conveyor\context_port_runs",
    [string]$RunId = "",
    [string]$QueriesJson = "",
    [int]$MaxNewTokens = 96,
    [int]$TopK = 3,
    [switch]$NoAdapter,
    [switch]$DryRun
)

$PythonExe = "D:\Research_Engine\.venv-train\Scripts\python.exe"
$ScriptPath = Join-Path $PSScriptRoot "run_storyworld_mcp_trm_smoke.py"

$argsList = @(
    "--model-path", $ModelPath,
    "--index-root", $IndexRoot,
    "--output-root", $OutputRoot,
    "--max-new-tokens", $MaxNewTokens,
    "--top-k", $TopK
)

if (-not $NoAdapter) {
    $argsList += @("--adapter-path", $AdapterPath)
}

if ($RunId) {
    $argsList += @("--run-id", $RunId)
}

if ($QueriesJson) {
    $argsList += @("--queries-json", $QueriesJson)
}

if ($DryRun) {
    $argsList += "--dry-run"
}

& $PythonExe $ScriptPath @argsList
exit $LASTEXITCODE
