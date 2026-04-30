param(
    [string[]]$Engines = @(
        "accelerator_sim_v1_cpp",
        "agent_based_sim_v1_cpp",
        "bifurcation_analyzer_v1_cpp",
        "ca_admissibility_sim_v1_cpp",
        "circular_accelerator_sim_v1_cpp",
        "falsification_suite_v1_cpp",
        "fsa_rule_engine_sim_v1_cpp",
        "graph_dynamics_sim_v1_cpp",
        "info_metrics_module_v1_cpp",
        "kuramoto_sim_v1_cpp",
        "lb_fluid_sim_v1_cpp",
        "linac_sim_cpp",
        "mc_ensemble_sim_v1_cpp",
        "parameter_optimizer_v1_cpp",
        "rd_sim_cpp",
        "spectral_analysis_v1_cpp",
        "stochastic_sim_cpp",
        "structural_box_sim_cpp",
        "symplectic_sim_v1_cpp",
        "tda_module_v1_cpp"
    )
)

$ErrorActionPreference = "Continue"
$repo = Resolve-Path (Join-Path $PSScriptRoot "..")
$runDir = Join-Path $repo "outputs\full_cpp_validation"
New-Item -ItemType Directory -Force -Path $runDir | Out-Null

$summary = @()
foreach ($engine in $Engines) {
    Write-Host "Processing $engine..."
    $log = Join-Path $runDir "$engine.log"
    $started = Get-Date
    Push-Location $repo
    $exitCode = -1
    try {
        if (Test-Path (Join-Path $repo "$engine\build_and_run.bat")) {
            & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "build_cpp_engine.ps1") -EngineDir $engine *> $log
            $exitCode = $LASTEXITCODE
        } else {
            Write-Warning "No build_and_run.bat found for $engine"
            "No build_and_run.bat found" | Set-Content $log
        }
    } catch {
        $_.Exception.Message | Add-Content $log
    } finally {
        Pop-Location
    }
    $summary += [pscustomobject]@{
        engine = $engine
        exit_code = $exitCode
        started_at = $started.ToString("o")
        finished_at = (Get-Date).ToString("o")
        log = "outputs/full_cpp_validation/$engine.log"
    }
}

$summary | ConvertTo-Json -Depth 4 | Set-Content -Path (Join-Path $runDir "summary.json")
$summary | Format-Table -AutoSize
