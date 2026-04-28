param(
    [string]$RunId = "job-limited-run",
    [int]$MemoryLimitMb = 2048,
    [int]$CpuPercent = 50,
    [string]$WorkDir = "C:\projects\Hermes-Skills\Hermes Skills",
    [string]$ExePath = "C:\Python311\python.exe",
    [string[]]$CommandArgs = @(),
    [string]$LogDir = "C:\projects\Hermes-Skills\Hermes Skills\data\job_limited_runs"
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

function Write-JsonLine([string]$Path, [hashtable]$Payload) {
    ($Payload | ConvertTo-Json -Compress -Depth 8) | Add-Content -Path $Path -Encoding UTF8
}

function Join-Args([string[]]$Items) {
    $parts = foreach ($arg in $Items) {
        if ($null -eq $arg) {
            '""'
        } elseif ($arg -match '[\s"]') {
            '"' + ($arg -replace '"', '\"') + '"'
        } else {
            $arg
        }
    }
    return ($parts -join ' ')
}

$logRoot = [System.IO.Path]::GetFullPath($LogDir)
New-Item -ItemType Directory -Force -Path $logRoot | Out-Null
$eventLog = Join-Path $logRoot "$RunId.events.jsonl"
$summaryPath = Join-Path $logRoot "$RunId.summary.json"
$stdoutPath = Join-Path $logRoot "$RunId.stdout.log"
$stderrPath = Join-Path $logRoot "$RunId.stderr.log"

if (Test-Path $eventLog) { Remove-Item $eventLog -Force }
if (Test-Path $summaryPath) { Remove-Item $summaryPath -Force }
if (Test-Path $stdoutPath) { Remove-Item $stdoutPath -Force }
if (Test-Path $stderrPath) { Remove-Item $stderrPath -Force }

$memoryBytes = $MemoryLimitMb * 1MB
$cpuPermille = [Math]::Max(1, [Math]::Min(10000, $CpuPercent * 100))
$job = [JobObject]::CreateJobObject([IntPtr]::Zero, "codex-$RunId")
if ($job -eq [IntPtr]::Zero) {
    throw "CreateJobObject failed"
}

$limit = New-Object JobObject+JOBOBJECT_EXTENDED_LIMIT_INFORMATION
$limit.BasicLimitInformation.LimitFlags = [JobObject]::JOB_OBJECT_LIMIT_PROCESS_MEMORY
$limit.ProcessMemoryLimit = [System.UIntPtr]::new([uint64]$memoryBytes)
$limitSize = [System.Runtime.InteropServices.Marshal]::SizeOf($limit)
$limitPtr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($limitSize)
[System.Runtime.InteropServices.Marshal]::StructureToPtr($limit, $limitPtr, $false)
if (-not [JobObject]::SetInformationJobObject($job, [JobObject]::JobObjectExtendedLimitInformation, $limitPtr, $limitSize)) {
    [System.Runtime.InteropServices.Marshal]::FreeHGlobal($limitPtr)
    throw "SetInformationJobObject failed for memory limit"
}
[System.Runtime.InteropServices.Marshal]::FreeHGlobal($limitPtr)

$cpu = New-Object JobObject+JOBOBJECT_CPU_RATE_CONTROL_INFORMATION
$cpu.ControlFlags = [JobObject]::JOB_OBJECT_CPU_RATE_CONTROL_ENABLE -bor [JobObject]::JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP
$cpu.CpuRate = $cpuPermille
$cpuSize = [System.Runtime.InteropServices.Marshal]::SizeOf($cpu)
$cpuPtr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($cpuSize)
[System.Runtime.InteropServices.Marshal]::StructureToPtr($cpu, $cpuPtr, $false)
if (-not [JobObject]::SetInformationJobObject($job, [JobObject]::JobObjectCpuRateControlInformation, $cpuPtr, $cpuSize)) {
    [System.Runtime.InteropServices.Marshal]::FreeHGlobal($cpuPtr)
    throw "SetInformationJobObject failed for CPU limit"
}
[System.Runtime.InteropServices.Marshal]::FreeHGlobal($cpuPtr)

Write-JsonLine $eventLog @{
    ts = [DateTime]::UtcNow.ToString("o")
    event = "start"
    run_id = $RunId
    exe = $ExePath
    args = $CommandArgs
    workdir = $WorkDir
    caps = @{
        ram_mb = $MemoryLimitMb
        cpu_pct = $CpuPercent
    }
}

$joinedArgs = Join-Args $CommandArgs
$proc = Start-Process -FilePath $ExePath -ArgumentList $joinedArgs -WorkingDirectory $WorkDir -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
if (-not [JobObject]::AssignProcessToJobObject($job, $proc.Handle)) {
    throw "AssignProcessToJobObject failed"
}

$samples = New-Object System.Collections.Generic.List[double]
while (-not $proc.HasExited) {
    Start-Sleep -Seconds 5
    $live = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    if ($live) {
        $privateMb = [math]::Round($live.PrivateMemorySize64 / 1MB, 1)
        $samples.Add($privateMb)
        Write-JsonLine $eventLog @{
            ts = [DateTime]::UtcNow.ToString("o")
            event = "heartbeat"
            run_id = $RunId
            pid = $proc.Id
            private_ram_mb = $privateMb
        }
    }
}

$peakRamMb = 0.0
$avgRamMb = 0.0
if ($samples.Count -gt 0) {
    $peakRamMb = [math]::Round(($samples | Measure-Object -Maximum).Maximum, 1)
    $avgRamMb = [math]::Round(($samples | Measure-Object -Average).Average, 1)
}

$status = if ($proc.ExitCode -eq 0) { "completed" } else { "aborted" }
Write-JsonLine $eventLog @{
    ts = [DateTime]::UtcNow.ToString("o")
    event = "finish"
    run_id = $RunId
    pid = $proc.Id
    exit_code = $proc.ExitCode
    status = $status
    peak_ram_mb = $peakRamMb
    avg_ram_mb = $avgRamMb
}

$summary = @{
    run_id = $RunId
    status = $status
    exit_code = $proc.ExitCode
    caps = @{
        ram_mb = $MemoryLimitMb
        cpu_pct = $CpuPercent
    }
    peak_ram_mb = $peakRamMb
    avg_ram_mb = $avgRamMb
    peak_io_mb_s = $null
    cpu_pct = $CpuPercent
    steps_completed = $samples.Count
    checkpoints = @()
    stdout_log = $stdoutPath
    stderr_log = $stderrPath
    event_log = $eventLog
}
$summary | ConvertTo-Json -Depth 8 | Set-Content -Path $summaryPath -Encoding UTF8
$summary | ConvertTo-Json -Depth 8
exit $proc.ExitCode
