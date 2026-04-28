param(
    [Parameter(Mandatory = $true)]
    [string]$ScriptPath,

    [Parameter()]
    [string]$PythonExe = "python",

    [Parameter()]
    [string]$WorkingDirectory = (Get-Location).Path,

    [Parameter()]
    [string]$RunId = ("jobcap-" + [guid]::NewGuid().ToString("N")),

    [Parameter()]
    [int]$MemoryLimitMB = 2048,

    [Parameter()]
    [int]$CpuRatePercent = 50,

    [Parameter()]
    [int]$IOCapMBps = 50,

    [Parameter()]
    [int]$TimeoutSec = 1800,

    [Parameter(Mandatory = $true)]
    [string]$SummaryPath,

    [Parameter(Mandatory = $true)]
    [string]$EventLogPath,

    [Parameter()]
    [string[]]$ScriptArgs = @()
)

$ErrorActionPreference = "Stop"

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public static class JobCapNative {
  [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
  public static extern IntPtr CreateJobObject(IntPtr lpJobAttributes, string lpName);

  [DllImport("kernel32.dll")]
  public static extern bool AssignProcessToJobObject(IntPtr hJob, IntPtr hProcess);

  [DllImport("kernel32.dll")]
  public static extern bool SetInformationJobObject(IntPtr hJob, int infoType, IntPtr lpJobObjectInfo, uint cbJobObjectInfoLength);

  [DllImport("kernel32.dll", SetLastError = true)]
  public static extern bool CloseHandle(IntPtr hObject);

  public const int JobObjectExtendedLimitInformation = 9;
  public const int JobObjectCpuRateControlInformation = 15;

  public const uint JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100;
  public const uint JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000;
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
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [hashtable]$Payload
    )
    $Payload["ts"] = [DateTime]::UtcNow.ToString("o")
    $json = $Payload | ConvertTo-Json -Compress -Depth 8
    Add-Content -LiteralPath $Path -Value $json -Encoding UTF8
}

function Resolve-ProcessInstanceName {
    param(
        [Parameter(Mandatory = $true)]
        [int]$ProcessId
    )
    try {
        $counter = Get-Counter '\Process(*)\ID Process' -ErrorAction Stop
        foreach ($sample in $counter.CounterSamples) {
            if ([int]$sample.CookedValue -eq $ProcessId) {
                return $sample.InstanceName
            }
        }
    } catch {
        return $null
    }
    return $null
}

function Get-ProcessIoMbps {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstanceName
    )
    try {
        $counter = Get-Counter "\Process($InstanceName)\IO Data Bytes/sec" -ErrorAction Stop
        if ($counter.CounterSamples.Count -gt 0) {
            return [double]$counter.CounterSamples[0].CookedValue / 1MB
        }
    } catch {
        return $null
    }
    return $null
}

function Quote-ProcessArgument {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Value
    )
    if ($Value -match '[\s"]') {
        return '"' + ($Value -replace '"', '\"') + '"'
    }
    return $Value
}

$summaryFile = [System.IO.Path]::GetFullPath($SummaryPath)
$eventFile = [System.IO.Path]::GetFullPath($EventLogPath)
$workdir = [System.IO.Path]::GetFullPath($WorkingDirectory)
$scriptFullPath = [System.IO.Path]::GetFullPath($ScriptPath)
$stdoutFile = [System.IO.Path]::Combine([System.IO.Path]::GetDirectoryName($summaryFile), "child.stdout.log")
$stderrFile = [System.IO.Path]::Combine([System.IO.Path]::GetDirectoryName($summaryFile), "child.stderr.log")

New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($summaryFile)) | Out-Null
New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($eventFile)) | Out-Null
if (Test-Path -LiteralPath $eventFile) {
    Remove-Item -LiteralPath $eventFile -Force
}
if (Test-Path -LiteralPath $stdoutFile) {
    Remove-Item -LiteralPath $stdoutFile -Force
}
if (Test-Path -LiteralPath $stderrFile) {
    Remove-Item -LiteralPath $stderrFile -Force
}

$jobName = "jobcap-" + [guid]::NewGuid().ToString("N")
$job = [JobCapNative]::CreateJobObject([IntPtr]::Zero, $jobName)
if ($job -eq [IntPtr]::Zero) {
    throw "Failed to create Windows Job Object."
}

$limit = New-Object JobCapNative+JOBOBJECT_EXTENDED_LIMIT_INFORMATION
$limit.BasicLimitInformation.LimitFlags = [JobCapNative]::JOB_OBJECT_LIMIT_PROCESS_MEMORY -bor [JobCapNative]::JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
$memoryLimitBytes = [UInt64]$MemoryLimitMB * 1MB
$limit.ProcessMemoryLimit = [System.UIntPtr]::new($memoryLimitBytes)
$limitSize = [System.Runtime.InteropServices.Marshal]::SizeOf($limit)
$limitPtr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($limitSize)
[System.Runtime.InteropServices.Marshal]::StructureToPtr($limit, $limitPtr, $false)
try {
    [void][JobCapNative]::SetInformationJobObject($job, [JobCapNative]::JobObjectExtendedLimitInformation, $limitPtr, [uint32]$limitSize)
} finally {
    [System.Runtime.InteropServices.Marshal]::FreeHGlobal($limitPtr)
}

$cpu = New-Object JobCapNative+JOBOBJECT_CPU_RATE_CONTROL_INFORMATION
$cpu.ControlFlags = [JobCapNative]::JOB_OBJECT_CPU_RATE_CONTROL_ENABLE -bor [JobCapNative]::JOB_OBJECT_CPU_RATE_CONTROL_HARD_CAP
$cpu.CpuRate = [uint32]([Math]::Max(1, [Math]::Min(100, $CpuRatePercent)) * 100)
$cpuSize = [System.Runtime.InteropServices.Marshal]::SizeOf($cpu)
$cpuPtr = [System.Runtime.InteropServices.Marshal]::AllocHGlobal($cpuSize)
[System.Runtime.InteropServices.Marshal]::StructureToPtr($cpu, $cpuPtr, $false)
try {
    [void][JobCapNative]::SetInformationJobObject($job, [JobCapNative]::JobObjectCpuRateControlInformation, $cpuPtr, [uint32]$cpuSize)
} finally {
    [System.Runtime.InteropServices.Marshal]::FreeHGlobal($cpuPtr)
}

$pythonArgs = @($scriptFullPath) + $ScriptArgs
$pythonArgString = (($pythonArgs | ForEach-Object { Quote-ProcessArgument -Value $_ }) -join " ")
$proc = Start-Process -FilePath $PythonExe -ArgumentList $pythonArgString -WorkingDirectory $workdir -PassThru -NoNewWindow -RedirectStandardOutput $stdoutFile -RedirectStandardError $stderrFile
if (-not [JobCapNative]::AssignProcessToJobObject($job, $proc.Handle)) {
    try {
        $proc.Kill()
    } catch {
    }
    [void][JobCapNative]::CloseHandle($job)
    throw "Failed to assign process $($proc.Id) to Windows Job Object."
}

$start = [DateTime]::UtcNow
$sampleCount = 0
$peakRamMB = 0.0
$ramTotal = 0.0
$peakIoMBps = 0.0
$cpuSamples = New-Object System.Collections.Generic.List[double]
$instanceName = $null
$prevSampleAt = $start
$prevCpuSec = 0.0
$timedOut = $false

Write-JsonLine -Path $eventFile -Payload @{
    event = "start"
    run_id = $RunId
    pid = $proc.Id
    script_path = $scriptFullPath
    working_directory = $workdir
    caps = @{
        ram_mb = $MemoryLimitMB
        cpu_pct = $CpuRatePercent
        io_mb_s = $IOCapMBps
    }
    chunk_strategy = "variant_per_run"
    checkpoint_interval = "variant_complete"
}

while (-not $proc.HasExited) {
    Start-Sleep -Milliseconds 1000
    try {
        $proc.Refresh()

        if ($proc.HasExited) {
            break
        }

        $now = [DateTime]::UtcNow
        $elapsed = ($now - $start).TotalSeconds
        if ($elapsed -ge $TimeoutSec) {
            $timedOut = $true
            Write-JsonLine -Path $eventFile -Payload @{
                event = "abort"
                run_id = $RunId
                reason = "timeout_sec_exceeded"
                timeout_sec = $TimeoutSec
            }
            try {
                $proc.Kill()
            } catch {
            }
            break
        }

        $ramMB = [math]::Round($proc.WorkingSet64 / 1MB, 4)
        $sampleCount += 1
        $ramTotal += $ramMB
        if ($ramMB -gt $peakRamMB) {
            $peakRamMB = $ramMB
        }

        $cpuNow = $proc.TotalProcessorTime.TotalSeconds
        $deltaWall = ($now - $prevSampleAt).TotalSeconds
        if ($sampleCount -gt 1 -and $deltaWall -gt 0) {
            $cpuPct = [math]::Round((($cpuNow - $prevCpuSec) / $deltaWall / [Environment]::ProcessorCount) * 100.0, 4)
            if ($cpuPct -lt 0) {
                $cpuPct = 0.0
            }
            [void]$cpuSamples.Add($cpuPct)
        }
        $prevSampleAt = $now
        $prevCpuSec = $cpuNow

        if (-not $instanceName) {
            $instanceName = Resolve-ProcessInstanceName -ProcessId $proc.Id
        }
        if ($instanceName) {
            $ioMBps = Get-ProcessIoMbps -InstanceName $instanceName
            if ($null -ne $ioMBps -and $ioMBps -gt $peakIoMBps) {
                $peakIoMBps = [double]$ioMBps
            }
        }
    } catch {
        Write-JsonLine -Path $eventFile -Payload @{
            event = "monitor_warning"
            run_id = $RunId
            message = $_.Exception.Message
        }
    }
}

$proc.WaitForExit()
$end = [DateTime]::UtcNow
$avgRamMB = if ($sampleCount -gt 0) { [math]::Round($ramTotal / $sampleCount, 4) } else { 0.0 }
$avgCpuPct = if ($cpuSamples.Count -gt 0) { [math]::Round((($cpuSamples | Measure-Object -Average).Average), 4) } else { 0.0 }
$peakIoRounded = [math]::Round($peakIoMBps, 4)

$status = if ($timedOut) { "aborted" } elseif ($proc.ExitCode -eq 0) { "success" } else { "failed" }
$abortReason = if ($timedOut) { "timeout_sec_exceeded" } elseif ($proc.ExitCode -ne 0) { "child_exit_$($proc.ExitCode)" } else { $null }

$summary = @{
    run_id = $RunId
    status = $status
    abort_reason = $abortReason
    script_path = $scriptFullPath
    working_directory = $workdir
    exit_code = $proc.ExitCode
    started_at_utc = $start.ToString("o")
    finished_at_utc = $end.ToString("o")
    duration_sec = [math]::Round(($end - $start).TotalSeconds, 4)
    peak_ram_mb = [math]::Round($peakRamMB, 4)
    avg_ram_mb = $avgRamMB
    peak_io_mb_s = $peakIoRounded
    cpu_pct = $avgCpuPct
    steps_completed = $sampleCount
    checkpoint_strategy = "variant_complete"
    caps = @{
        ram_mb = $MemoryLimitMB
        cpu_pct = $CpuRatePercent
        io_mb_s = $IOCapMBps
        timeout_sec = $TimeoutSec
    }
    child_args = $pythonArgs
    child_arg_string = $pythonArgString
    stdout_path = $stdoutFile
    stderr_path = $stderrFile
    event_log_path = $eventFile
}

$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryFile -Encoding UTF8

Write-JsonLine -Path $eventFile -Payload @{
    event = "finish"
    run_id = $RunId
    status = $status
    exit_code = $proc.ExitCode
    peak_ram_mb = $summary.peak_ram_mb
    avg_ram_mb = $summary.avg_ram_mb
    peak_io_mb_s = $summary.peak_io_mb_s
    cpu_pct = $summary.cpu_pct
    steps_completed = $summary.steps_completed
}

[void][JobCapNative]::CloseHandle($job)

if ($proc.ExitCode -ne 0) {
    throw "Child process exited with code $($proc.ExitCode). See $stderrFile"
}
