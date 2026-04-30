param(
    [Parameter(Mandatory=$true)]
    [string]$EngineDir
)

$ErrorActionPreference = "Stop"
$repo = Resolve-Path (Join-Path $PSScriptRoot "..")
$enginePath = Join-Path $repo $EngineDir
$script = Join-Path $enginePath "build_and_run.bat"

if (!(Test-Path $script)) {
    throw "No build_and_run.bat found for $EngineDir"
}

Push-Location $repo
try {
    & cmd /c $script
} finally {
    Pop-Location
}
