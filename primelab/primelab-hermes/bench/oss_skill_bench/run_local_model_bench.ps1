param(
    [Parameter(Mandatory = $true)][string]$Model,
    [string]$RunId,
    [int]$MaxSteps = 2,
    [int]$SeqLen = 256,
    [int]$BatchSize = 1,
    [int]$GradAccum = 1,
    [int]$LoraR = 8,
    [int]$LoraAlpha = 16
)

$ErrorActionPreference = "Stop"

if (-not $RunId) {
    $safe = ($Model -replace '[^A-Za-z0-9._-]', '_')
    $RunId = "bench-$safe"
}

$venvPython = ".\.venv-gpu\Scripts\python.exe"
$outDir = "runs\qlora_conveyor\$RunId"
$logPath = "$outDir.log"

if (-not (Test-Path $venvPython)) {
    throw "Missing GPU bench interpreter at $venvPython"
}

if (-not (Test-Path "data\qlora_conveyor\bench-default\gsm8k_main_sample\train.jsonl")) {
    & $venvPython scripts\build_qlora_dataset.py --spec-json bench\oss_skill_bench\default_qlora_spec.json --out-root data\qlora_conveyor\bench-default
}

if (Test-Path $outDir) {
    Remove-Item -Recurse -Force $outDir
}
if (Test-Path $logPath) {
    Remove-Item -Force $logPath
}

$env:PYTHONPATH = "src"
$cmd = @(
    $venvPython,
    "scripts\train_qlora_sft.py",
    "--model", $Model,
    "--data", "data\qlora_conveyor\bench-default\gsm8k_main_sample\train.jsonl",
    "--out", $outDir,
    "--max-steps", "$MaxSteps",
    "--seq-len", "$SeqLen",
    "--batch-size", "$BatchSize",
    "--grad-accum", "$GradAccum",
    "--lora-r", "$LoraR",
    "--lora-alpha", "$LoraAlpha",
    "--lora-dropout", "0.05",
    "--target-modules", "q_proj,k_proj,v_proj,o_proj"
)

& cmd /c (($cmd -join " ") + " > `"$logPath`" 2>&1")

& $venvPython bench\oss_skill_bench\summarize_bench.py --run-dir $outDir --log $logPath
Get-Content "$outDir\bench_summary.json"
