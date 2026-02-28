# SpecForge Distill - PowerShell 7 development runner
# Usage: .\distill.ps1 path\to\spec.pdf [args]

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $scriptDir ".venv\Scripts\python.exe"
$pythonExe = $null
$pythonArgs = @()

if (Test-Path $venvPython) {
    $pythonExe = $venvPython
} elseif ($python = Get-Command python -ErrorAction SilentlyContinue) {
    $pythonExe = $python.Source
} elseif ($py = Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = $py.Source
    $pythonArgs = @("-3")
} else {
    [Console]::Error.WriteLine("error: python was not found. Use a release binary from GitHub Releases instead.")
    exit 127
}

if ($pythonArgs.Count -gt 0) {
    $env:DISTILL_SELECTED_PYTHON = "$pythonExe $($pythonArgs -join ' ')"
} else {
    $env:DISTILL_SELECTED_PYTHON = $pythonExe
}

$runnerPath = Join-Path $scriptDir "scripts\run_local_dev.py"
& $pythonExe @pythonArgs $runnerPath @args
exit $LASTEXITCODE
