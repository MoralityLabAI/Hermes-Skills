param(
  [string]$RunId = "c_signature_commit_trm_v1",
  [string]$PythonExe = "python",
  [Parameter(Mandatory=$true)][string]$TrainerScript,
  [string]$TrainerArgs = "",
  [string]$OutDir = "research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\c_signature_commit_trm_jobcap",
  [int]$RamMb = 2048,
  [int]$CpuPct = 50,
  [int]$IoMbS = 50,
  [int]$CheckpointIntervalSec = 60
)

$ErrorActionPreference = "Stop"

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class HrmJobObject {
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
  public struct IO_COUNTERS {
    public ulong ReadOperationCount;
    public ulong WriteOperationCount;
    public ulong OtherOperationCount;
    public ulong ReadTransferCount;
    public ulong WriteTransferCount;
    public ulong OtherTransferCount;
  }

  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_BASIC_LIMIT_INFORMATION {
    public long PerProcessUserTimeLimit;
    public long PerJobUserTimeLimit;
    public uint LimitFlags;
    public UIntPtr MinimumWorkingSetSize;
    public UIntPtr MaximumWorkingSetSize;
    public uint ActiveProcessLimit;
    public long Affinity;
    public uint PriorityClass;
    public uint SchedulingClass;
  }

  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_EXTENDED_LIMIT_INFORMATION {
    public JOBOBJECT_BASIC_LIMIT_INFORMATION BasicLimitInformation;
    public IO_COUNTERS IoInfo;
    public UIntPtr ProcessMemoryLimit;
    public UIntPtr JobMemoryLimit;
    public UIntPtr PeakProcessMemoryUsed;
    public UIntPtr PeakJobMemoryUsed;
  }

  [StructLayout(LayoutKind.Sequential)]
  public struct JOBOBJECT_CPU_RATE_CONTROL_INFORMATION {
    public uint ControlFlags;
    public uint CpuRate;
  }
}
'@

function Write-JsonLine {
  param([string]$Path, [hashtable]$Payload)
  $Payload["ts"] = (Get-Date).ToUniversalTime().ToString("o")
  ($Payload | ConvertTo-Json -Compress -Depth 10) | Add-Content -LiteralPath $Path -Encoding UTF8
}

function Set-JobObjectMemoryLimit {
  param([IntPtr]$Job, [UInt64]$MemoryLimitBytes)
  $limit = New-Object HrmJobObject+JOBOBJECT_EXTENDED_LIMIT_INFORMATION
  $limit.BasicLimitInformation.LimitFlags = [HrmJobObject]::JOB_OBJECT_LIMIT_PROCESS_MEMORY
  $limit.ProcessMemoryLimit = [UIntPtr]$MemoryLimitBytes
  $size = [System.Runtime.InteropServices.Marshal]::SizeOf($limit)
  $ptr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($size)
  try {
    [System.Runtime.InteropServices.Marshal]::StructureToPtr($limit, $ptr, $false)
    [HrmJobObject]::SetInformationJobObject($Job, [HrmJobObject]::JobObjectExtendedLimitInformation, $ptr, [uint32]$size) | Out-Null
  } finally {
    [System.Runtime.InteropServices.Marshal]::FreeHGlobal($ptr)
  }
}

function Set-JobObjectCpuLimit {
  param([IntPtr]$Job, [int]$CpuPercent)
  $cpu = New-Object HrmJobObject+JOBOBJECT_CPU_RATE_CONTROL_INFORMATION
  $cpu.ControlFlags = [HrmJobObject]::JOB_OBJECT_CPU_RATE_CONTROL_ENABLE -bor [HrmJobObject]::JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP
  $cpu.CpuRate = [uint32]($CpuPercent * 100)
  $size = [System.Runtime.InteropServices.Marshal]::SizeOf($cpu)
  $ptr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($size)
  try {
    [System.Runtime.InteropServices.Marshal]::StructureToPtr($cpu, $ptr, $false)
    [HrmJobObject]::SetInformationJobObject($Job, [HrmJobObject]::JobObjectCpuRateControlInformation, $ptr, [uint32]$size) | Out-Null
  } finally {
    [System.Runtime.InteropServices.Marshal]::FreeHGlobal($ptr)
  }
}

function Get-ProcessIoBytes {
  param([System.Diagnostics.Process]$Process)
  foreach ($readName in @("IOReadBytes", "IoReadBytes")) {
    foreach ($writeName in @("IOWriteBytes", "IoWriteBytes")) {
      if ($Process.PSObject.Properties.Name -contains $readName -and $Process.PSObject.Properties.Name -contains $writeName) {
        return [UInt64]$Process.$readName + [UInt64]$Process.$writeName
      }
    }
  }
  return 0
}

$resolvedOut = Resolve-Path -LiteralPath "." | Select-Object -ExpandProperty Path
if (-not [System.IO.Path]::IsPathRooted($OutDir)) {
  $OutDir = Join-Path $resolvedOut $OutDir
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$eventsPath = Join-Path $OutDir "jobcap.events.jsonl"
$summaryPath = Join-Path $OutDir "jobcap.summary.json"
if (Test-Path -LiteralPath $eventsPath) { Remove-Item -LiteralPath $eventsPath }
if (Test-Path -LiteralPath $summaryPath) { Remove-Item -LiteralPath $summaryPath }

$caps = @{ ram_mb = $RamMb; cpu_pct = $CpuPct; io_mb_s = $IoMbS }
Write-JsonLine -Path $eventsPath -Payload @{ event = "start"; run_id = $RunId; caps = $caps; trainer_script = $TrainerScript; trainer_args = $TrainerArgs }

$job = [HrmJobObject]::CreateJobObject([IntPtr]::Zero, "hrm-trainer-$RunId")
Set-JobObjectMemoryLimit -Job $job -MemoryLimitBytes ([UInt64]$RamMb * 1MB)
Set-JobObjectCpuLimit -Job $job -CpuPercent $CpuPct

$argList = @("`"$TrainerScript`"")
if ($TrainerArgs.Trim().Length -gt 0) {
  $argList += $TrainerArgs
}

$proc = Start-Process -FilePath $PythonExe -ArgumentList ($argList -join " ") -PassThru -NoNewWindow
[HrmJobObject]::AssignProcessToJobObject($job, $proc.Handle) | Out-Null

$start = Get-Date
$lastCheckpoint = $start
$lastIoTs = $start
$lastIoBytes = 0
$peakRamMb = 0.0
$ramSamples = New-Object System.Collections.Generic.List[double]
$peakIoMbS = 0.0
$abortReason = $null

while (-not $proc.HasExited) {
  Start-Sleep -Seconds 1
  $sample = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
  if ($null -eq $sample) {
    break
  }

  $ramMbNow = [math]::Round($sample.WorkingSet64 / 1MB, 4)
  $ramSamples.Add($ramMbNow)
  if ($ramMbNow -gt $peakRamMb) {
    $peakRamMb = $ramMbNow
  }

  $now = Get-Date
  $ioBytes = Get-ProcessIoBytes -Process $sample
  $elapsedIo = [math]::Max(0.001, ($now - $lastIoTs).TotalSeconds)
  $ioRateMbS = [math]::Round((($ioBytes - $lastIoBytes) / 1MB) / $elapsedIo, 4)
  if ($ioRateMbS -gt $peakIoMbS) {
    $peakIoMbS = $ioRateMbS
  }
  $lastIoBytes = $ioBytes
  $lastIoTs = $now

  if (($now - $lastCheckpoint).TotalSeconds -ge $CheckpointIntervalSec) {
    Write-JsonLine -Path $eventsPath -Payload @{ event = "checkpoint_due"; run_id = $RunId; elapsed_sec = [math]::Round(($now - $start).TotalSeconds, 3); peak_ram_mb = $peakRamMb; peak_io_mb_s = $peakIoMbS }
    $lastCheckpoint = $now
  }

  if ($ioRateMbS -gt $IoMbS) {
    $abortReason = "io_cap_exceeded"
    Write-JsonLine -Path $eventsPath -Payload @{ event = "abort"; run_id = $RunId; reason = $abortReason; peak_ram_mb = $peakRamMb; peak_io_mb_s = $peakIoMbS; steps_completed = 0 }
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    break
  }
}

$proc.Refresh()
$exitCode = $null
try {
  $exitCode = $proc.ExitCode
} catch {
  $exitCode = $null
}

$status = "completed"
if ($abortReason) {
  $status = "aborted"
} elseif ($exitCode -ne 0) {
  $status = "failed"
}

$avgRam = 0.0
if ($ramSamples.Count -gt 0) {
  $avgRam = [math]::Round(($ramSamples | Measure-Object -Average).Average, 4)
}

$summary = @{
  run_id = $RunId
  status = $status
  exit_code = $exitCode
  abort_reason = $abortReason
  peak_ram_mb = $peakRamMb
  avg_ram_mb = $avgRam
  peak_io_mb_s = $peakIoMbS
  cpu_pct = $CpuPct
  steps_completed = 0
  checkpoints = @()
  caps = $caps
}
($summary | ConvertTo-Json -Depth 10) | Set-Content -LiteralPath $summaryPath -Encoding UTF8
Write-JsonLine -Path $eventsPath -Payload @{ event = "finish"; run_id = $RunId; status = $status; exit_code = $exitCode; abort_reason = $abortReason; peak_ram_mb = $peakRamMb; peak_io_mb_s = $peakIoMbS }

if ($status -eq "completed") {
  exit 0
}
exit 1
