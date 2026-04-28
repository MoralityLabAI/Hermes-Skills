param(
    [string]$BundleRoot = "C:\projects\Hermes-Skills\Hermes Skills\data\handoffs\bluebeam_mechinterp_2026-04-16"
)

$ErrorActionPreference = "Stop"

$zipPath = "$BundleRoot.zip"
Remove-Item $BundleRoot -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $zipPath -Force -ErrorAction SilentlyContinue

New-Item -ItemType Directory -Force -Path `
    $BundleRoot, `
    (Join-Path $BundleRoot "benchmark"), `
    (Join-Path $BundleRoot "benchmark\positive_replays"), `
    (Join-Path $BundleRoot "trm"), `
    (Join-Path $BundleRoot "logs") | Out-Null

Copy-Item "data\primehub_eligible_benchmark_v3_tuned_44env_v2\ledger.jsonl" (Join-Path $BundleRoot "benchmark\ledger.jsonl")
Copy-Item "data\primehub_eligible_benchmark_v3_tuned_44env_v2\overnight_primehub_benchmark.stout.jsonl" (Join-Path $BundleRoot "benchmark\overnight_primehub_benchmark.stout.jsonl")
Copy-Item "data\job_limited_runs\primehub-44env-9b27b-tuned-v2.events.jsonl" (Join-Path $BundleRoot "logs\primehub-44env-9b27b-tuned-v2.events.jsonl")
Copy-Item "data\job_limited_runs\primehub-trm-skill-loop-v4.events.jsonl" (Join-Path $BundleRoot "logs\primehub-trm-skill-loop-v4.events.jsonl")

Copy-Item "data\primehub_trm_autoresearch\latest.summary.json" (Join-Path $BundleRoot "trm\latest.summary.json")
Copy-Item "data\primehub_trm_autoresearch\latest.skill_imprint.json" (Join-Path $BundleRoot "trm\latest.skill_imprint.json")
Copy-Item "data\primehub_trm_autoresearch\latest.skill_imprint.md" (Join-Path $BundleRoot "trm\latest.skill_imprint.md")
Copy-Item "data\primehub_trm_autoresearch\cycle_12\primehub_trm_rollup.manifest.json" (Join-Path $BundleRoot "trm\cycle_12.primehub_trm_rollup.manifest.json")
Copy-Item "data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.jsonl" (Join-Path $BundleRoot "trm\cycle_12.primehub_trm_merged.jsonl")
Copy-Item "data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.summary.json" (Join-Path $BundleRoot "trm\cycle_12.primehub_trm_merged.summary.json")
Copy-Item "data\primehub_trm_autoresearch\cycle_12\bench\trm_critic_bench.summary.json" (Join-Path $BundleRoot "trm\cycle_12.trm_critic_bench.summary.json")
Copy-Item "data\primehub_trm_autoresearch\cycle_12\bench\trm_retriever_bench.summary.json" (Join-Path $BundleRoot "trm\cycle_12.trm_retriever_bench.summary.json")
Copy-Item "data\primehub_trm_autoresearch\cycle_12\bench\trm_router_bench.summary.json" (Join-Path $BundleRoot "trm\cycle_12.trm_router_bench.summary.json")

$rows = Get-Content "data\primehub_eligible_benchmark_v3_tuned_44env_v2\ledger.jsonl" | ForEach-Object {
    $_ | ConvertFrom-Json
}

$positiveRows = $rows | Where-Object {
    $_.status -eq "success" -and (($_.reward_totals.PSObject.Properties.Value | Measure-Object -Sum).Sum) -gt 0
}

foreach ($row in $positiveRows) {
    $modelDir = Join-Path (Join-Path $BundleRoot "benchmark\positive_replays") $row.model_id
    New-Item -ItemType Directory -Force -Path $modelDir | Out-Null
    foreach ($path in @($row.export_path, $row.summary_path, $row.config_path)) {
        if ($path -and (Test-Path $path)) {
            Copy-Item $path $modelDir
        }
    }
}

Compress-Archive -Path (Join-Path $BundleRoot "*") -DestinationPath $zipPath -Force

$bundleFiles = Get-ChildItem $BundleRoot -Recurse -File
[pscustomobject]@{
    bundle_root = $BundleRoot
    zip_path = $zipPath
    file_count = $bundleFiles.Count
    bundle_size_bytes = ($bundleFiles | Measure-Object -Property Length -Sum).Sum
    zip_size_bytes = (Get-Item $zipPath).Length
    positive_replay_count = $positiveRows.Count
} | ConvertTo-Json -Depth 4
