param(
  [string]$OutDir = "",
  [string]$ExePath = ""
)

$ErrorActionPreference = "Stop"

$toolDir = Split-Path -Parent $PSCommandPath
$rootDir = Split-Path -Parent $toolDir

if (-not $ExePath) {
  $candidate = Join-Path $rootDir "box_sim.exe"
  if (Test-Path $candidate) {
    $ExePath = $candidate
  } else {
    throw "box_sim.exe not found at $candidate (use -ExePath)."
  }
}

if (-not $OutDir) {
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $rootDir ("outputs\\runs\\smoke_" + $stamp)
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$cmd = @($ExePath, "--out", $OutDir)
$started = (Get-Date).ToString("o")

& $ExePath --out $OutDir
$exit = $LASTEXITCODE

$report = @{
  tool_name = "structural_box_signed_v1_cpp"
  started_at = $started
  finished_at = (Get-Date).ToString("o")
  exe_path = $ExePath
  out_dir = $OutDir
  command = $cmd
  exit_code = $exit
  notes = @(
    "exit_code -1073741515 (0xC0000135) commonly indicates missing runtime DLL dependencies."
  )
}

$reportPath = Join-Path $toolDir "smoke_report.json"
$report | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $reportPath

if (Test-Path (Join-Path $OutDir "summary.json")) {
  Write-Host "Smoke OK. summary.json produced at $OutDir\\summary.json"
} else {
  Write-Host "Smoke did not produce summary.json. See $reportPath"
}

