# train_trm_3090_full.ps1
# Full TRM training pipeline optimized for RTX 3090 (24GB VRAM) and 16k context.

param(
    [string]$WorldJson = "storyworlds/charter_of_ashen_aegis.json",
    [string]$ModelName = "Qwen/Qwen2.5-1.5B-Instruct",
    [string]$OutputDir = "hermes-skills/pure-trm-trainer/runs/index_routing_v1",
    [int]$MaxLength = 16384
)

$RepoRoot = Get-Location
$ScriptsDir = "$RepoRoot/hermes-skills/storyworld-conveyor/scripts"

# 1. Generate Training Corpus
Write-Host "--- Generating retrieval corpus from $WorldJson ---" -ForegroundColor Cyan
python "$ScriptsDir/build_retrieval_corpus.py" `
    --world-json "$WorldJson" `
    --output "$OutputDir/train.jsonl"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Corpus generation failed."
    exit $LASTEXITCODE
}

# 2. Run QLoRA Training
Write-Host "--- Starting 3090-optimized QLoRA training (16k context) ---" -ForegroundColor Cyan
python "$ScriptsDir/train_qlora_3090.py" `
    --model-name "$ModelName" `
    --data-path "$OutputDir/train.jsonl" `
    --output-dir "$OutputDir/adapter" `
    --max-length $MaxLength

if ($LASTEXITCODE -ne 0) {
    Write-Error "Training failed. This might be due to OOM. Check VRAM usage."
    exit $LASTEXITCODE
}

Write-Host "--- Pipeline complete! Adapter saved to $OutputDir/adapter ---" -ForegroundColor Green
