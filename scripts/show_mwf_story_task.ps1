param([string]$TaskName = "Krishna Story Factory MWF")

# Print MWF scheduler status: TaskName, State, Enabled, next run times, action path.

$ErrorActionPreference = "Stop"

$Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
$Info = Get-ScheduledTaskInfo -TaskName $TaskName -ErrorAction Stop
$Action = @($Task.Actions)[0]
$ActionPath = if ($Action) {
    $exe = [string]$Action.Execute
    $args = [string]$Action.Arguments
    if ($args) { "$exe $args" } else { $exe }
} else {
    "(no action)"
}

$NextRuns = @()
if ($Info.NextRunTime -and $Info.NextRunTime -gt [datetime]::MinValue) {
    $NextRuns += $Info.NextRunTime.ToString("o")
}
foreach ($trigger in @($Task.Triggers)) {
    if ($trigger.StartBoundary) {
        try {
            $NextRuns += ([datetime]::Parse($trigger.StartBoundary)).ToString("o")
        } catch {
            $NextRuns += [string]$trigger.StartBoundary
        }
    }
}
$NextRuns = @($NextRuns | Select-Object -Unique)

[pscustomobject]@{
    TaskName     = $Task.TaskName
    State        = [string]$Task.State
    Enabled      = [bool]$Task.Settings.Enabled
    NextRunTime  = if ($Info.NextRunTime -and $Info.NextRunTime -gt [datetime]::MinValue) {
        $Info.NextRunTime.ToString("o")
    } else {
        "(none — typically when Disabled)"
    }
    TriggerStarts = ($NextRuns -join "; ")
    ActionPath   = $ActionPath
    WorkingDirectory = [string]$Action.WorkingDirectory
} | Format-List
