param(
    [string[]]$Engines = @(
        "symplectic_sim_v1_cpp",
        "spectral_analysis_v1_cpp",
        "tda_module_v1_cpp",
        "mc_ensemble_sim_v1_cpp",
        "parameter_optimizer_v1_cpp"
    )
)

$ErrorActionPreference = "Stop"
$repo = Resolve-Path (Join-Path $PSScriptRoot "..")
$runDir = Join-Path $repo "outputs\cpp_smoke"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$summary = @()
foreach ($engine in $Engines) {
    $log = Join-Path $runDir "$engine.log"
    $started = Get-Date
    Push-Location $repo
    try {
        & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "build_cpp_engine.ps1") -EngineDir $engine *> $log
        $exitCode = $LASTEXITCODE
    } finally {
        Pop-Location
    }
    $summary += [pscustomobject]@{
        engine = $engine
        exit_code = $exitCode
        started_at = $started.ToString("o")
        finished_at = (Get-Date).ToString("o")
        log = "outputs/cpp_smoke/$engine.log"
    }
}

$summary | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $runDir "summary.json")
$summary | Format-Table -AutoSize
