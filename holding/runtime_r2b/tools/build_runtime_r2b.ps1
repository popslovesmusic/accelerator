$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$buildDir = Join-Path $rootDir "build\cmake"
$smokeOutputDir = Join-Path $rootDir "build\smoke_output"
$reportPath = Join-Path $rootDir "build\last_build_report.json"

New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

cmake -S $rootDir -B $buildDir
if ($LASTEXITCODE -ne 0) {
    throw "CMake configure failed."
}

cmake --build $buildDir --config Release
if ($LASTEXITCODE -ne 0) {
    throw "CMake build failed."
}

$exePath = Join-Path $buildDir "Release\analog_runtime_r2b_probe.exe"
if (-not (Test-Path $exePath)) {
    $exePath = Join-Path $buildDir "analog_runtime_r2b_probe.exe"
}
if (-not (Test-Path $exePath)) {
    throw "Probe executable not found."
}

if (Test-Path $smokeOutputDir) {
    Remove-Item -Recurse -Force $smokeOutputDir
}

& $exePath `
    --output-dir $smokeOutputDir `
    --case-label runtime_r2b_smoke `
    --seed 30101 `
    --steps 1024 `
    --snapshot-interval 128 `
    --nodes 128 `
    --drive 0.20

if ($LASTEXITCODE -ne 0) {
    throw "Smoke run failed."
}

$report = @{
    generated_at = (Get-Date).ToString("o")
    status = "ok"
    configuration = "Release"
    build_dir = $buildDir
    executable = $exePath
    smoke_output_dir = $smokeOutputDir
    run_metrics_csv = (Join-Path $smokeOutputDir "run_metrics.csv")
    run_timeseries_csv = (Join-Path $smokeOutputDir "run_timeseries.csv")
    metadata_json = (Join-Path $smokeOutputDir "run_metadata.json")
}

$report | ConvertTo-Json -Depth 4 | Set-Content -Path $reportPath -Encoding ascii
