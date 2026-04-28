param(
    [string]$RunId = "qwen35-4b-skill-smoke",
    [int]$MemoryLimitMb = 2048,
    [int]$CpuPercent = 50,
    [int]$Port = 18083,
    [int]$CtxSize = 512,
    [string]$ModelPath = "D:\Research_Engine\models\Qwen3.5\Qwen3.5-4B\Qwen3.5-4B-Q4_K_M.gguf",
    [string]$ExePath = "D:\Research_Engine\runtime\llama-b8665-win-cuda-12.4-x64\llama-server.exe",
    [string]$LogDir = "C:\projects\Hermes-Skills\Hermes Skills\data\qwen35_4b_skill_smoke"
)

$ErrorActionPreference = "Stop"

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class JobObject {
  [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
  public static extern IntPtr CreateJobObject(IntPtr lpJobAttributes, string lpName);

  [DllImport("kernel32.dll")]
  public static extern bool AssignProcessToJobObject(IntPtr hJob, IntPtr hProcess);

  [DllImport("kernel32.dll")]
  public static extern bool SetInformationJobObject(IntPtr hJob, int infoType, IntPtr lpJobObjectInfo, uint cbJobObjectInfoLength);

  public const int JobObjectExtendedLimitInformation = 9;
  public const int JobObjectCpuRateControlInformation = 15;
  public const uint JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100;
  public const uint JOB_OBJECT_CPU_RATE_CONTROL_ENABLE = 0x1;
  public const uint JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP = 0x4;

  [StructLayout(LayoutKind.Sequential)]
  public struct IO_COUNTERS { public ulong ReadOperationCount; public ulong WriteOperationCount; public ulong OtherOperationCount; public ulong ReadTransferCount; public ulong WriteTransferCount; public ulong OtherTransferCount; }

  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_BASIC_LIMIT_INFORMATION { public long PerProcessUserTimeLimit; public long PerJobUserTimeLimit; public uint LimitFlags; public UIntPtr MinimumWorkingSetSize; public UIntPtr MaximumWorkingSetSize; public uint ActiveProcessLimit; public long Affinity; public uint PriorityClass; public uint SchedulingClass; }

  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION { public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation; public IO_COUNTERS IoInfo; public UIntPtr ProcessMemoryLimit; public UIntPtr JobMemoryLimit; public UIntPtr PeakProcessMemoryUsed; public UIntPtr PeakJobMemoryUsed; }

  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_CPU_RATE_CONTROL_INFORMATION { public uint ControlFlags; public uint CpuRate; }
}
'@

$logRoot = [System.IO.Path]::GetFullPath($LogDir)
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
$eventLog = Join-Path $logRoot "$RunId.server.events.jsonl"
$summaryPath = Join-Path $logRoot "$RunId.server.summary.json"
$stdoutPath = Join-Path $logRoot "$RunId.server.out.log"
$stderrPath = Join-Path $logRoot "$RunId.server.err.log"

function Write-Event([string]$Event, [hashtable]$Extra) {
    $payload = @{
        ts = [DateTime]::UtcNow.ToString("o")
        event = $Event
        run_id = $RunId
    }
    foreach ($key in $Extra.Keys) {
        $payload[$key] = $Extra[$key]
    }
    ($payload | ConvertTo-Json -Compress) | Add-Content -Path $eventLog -Encoding UTF8
}

$memoryBytes = $MemoryLimitMb * 1MB
$cpuPermille = [Math]::Max(1, [Math]::Min(10000, $CpuPercent * 100))

if (Test-Path $stdoutPath) { Remove-Item $stdoutPath -Force }
if (Test-Path $stderrPath) { Remove-Item $stderrPath -Force }

$listenConn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($listenConn) {
    $stale = Get-Process -Id $listenConn.OwningProcess -ErrorAction SilentlyContinue
    if ($stale) {
        Stop-Process -Id $stale.Id -Force
        Write-Event "cleanup_existing_listener" @{ pid = $stale.Id; port = $Port }
        Start-Sleep -Seconds 1
    }
}

$job = [JobObject]::CreateJobObject([IntPtr]::Zero, "codex-$RunId")

$limit = New-Object JobObject+JOBOBJECT_EXTENDED_LIMIT_INFORMATION
$limit.BasicLimitInformation.LimitFlags = [JobObject]::JOB_OBJECT_LIMIT_PROCESS_MEMORY
$limit.ProcessMemoryLimit = [UIntPtr]$memoryBytes
$limitSize = [System.Runtime.InteropServices.Marshal]::SizeOf($limit)
$limitPtr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($limitSize)
[System.Runtime.InteropServices.Marshal]::StructureToPtr($limit, $limitPtr, $false)
[JobObject]::SetInformationJobObject($job, [JobObject]::JobObjectExtendedLimitInformation, $limitPtr, $limitSize) | Out-Null
[System.Runtime.InteropServices.Marshal]::FreeHGlobal($limitPtr)

$cpu = New-Object JobObject+JOBOBJECT_CPU_RATE_CONTROL_INFORMATION
$cpu.ControlFlags = [JobObject]::JOB_OBJECT_CPU_RATE_CONTROL_ENABLE -bor [JobObject]::JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP
$cpu.CpuRate = $cpuPermille
$cpuSize = [System.Runtime.InteropServices.Marshal]::SizeOf($cpu)
$cpuPtr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($cpuSize)
[System.Runtime.InteropServices.Marshal]::StructureToPtr($cpu, $cpuPtr, $false)
[JobObject]::SetInformationJobObject($job, [JobObject]::JobObjectCpuRateControlInformation, $cpuPtr, $cpuSize) | Out-Null
[System.Runtime.InteropServices.Marshal]::FreeHGlobal($cpuPtr)

$args = @(
    "--model", $ModelPath,
    "--host", "127.0.0.1",
    "--port", "$Port",
    "--ctx-size", "$CtxSize",
    "--n-gpu-layers", "99",
    "--threads", "4",
    "--threads-batch", "2",
    "--batch-size", "64",
    "--ubatch-size", "32",
    "--parallel", "1",
    "--flash-attn", "on",
    "--cache-type-k", "q4_0",
    "--cache-type-v", "q4_0",
    "--no-webui"
)

Write-Event "start" @{
    caps = @{
        ram_mb = $MemoryLimitMb
        cpu_pct = $CpuPercent
    }
    model_path = $ModelPath
    port = $Port
    ctx_size = $CtxSize
}

$proc = Start-Process -FilePath $ExePath -ArgumentList $args -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
[JobObject]::AssignProcessToJobObject($job, $proc.Handle) | Out-Null

$ready = $false
for ($i = 0; $i -lt 25; $i++) {
    Start-Sleep -Seconds 2
    if ($proc.HasExited) {
        break
    }
    try {
        $resp = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 4
        if ($resp.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
    }
}

$status = if ($ready) { "ready" } elseif ($proc.HasExited) { "aborted" } else { "not_ready" }
$peakRamMb = $null
$privateMb = $null
if (-not $proc.HasExited) {
    $live = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    if ($live) {
        $peakRamMb = [math]::Round($live.WorkingSet64 / 1MB, 1)
        $privateMb = [math]::Round($live.PrivateMemorySize64 / 1MB, 1)
    }
}

Write-Event $status @{
    pid = $proc.Id
    ready = $ready
    peak_ram_mb = $peakRamMb
    private_ram_mb = $privateMb
}

$summary = @{
    run_id = $RunId
    status = $status
    port = $Port
    pid = $proc.Id
    caps = @{
        ram_mb = $MemoryLimitMb
        cpu_pct = $CpuPercent
    }
    peak_ram_mb = $peakRamMb
    private_ram_mb = $privateMb
    stdout_log = $stdoutPath
    stderr_log = $stderrPath
    event_log = $eventLog
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -Path $summaryPath -Encoding UTF8
$summary | ConvertTo-Json -Depth 5
