$ErrorActionPreference = "Stop"

Set-Location (Split-Path $PSScriptRoot -Parent)

New-Item -ItemType Directory -Force .tmp_venv | Out-Null
$env:TEMP = (Resolve-Path .tmp_venv).Path
$env:TMP = $env:TEMP

if (-not (Test-Path .venv\Scripts\Activate.ps1)) {
  Write-Error "Missing .venv. Create it with: python -m venv .venv"
}

. .\.venv\Scripts\Activate.ps1
python -V
