$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$buildScript = Join-Path $scriptDir "build_runtime_r2b.ps1"
$buildDir = Join-Path $rootDir "build\cmake"
$outputRoot = Join-Path $rootDir "outputs\runtime_r2b_stage_anchor_suite_v1"
$caseSummaryPath = Join-Path $outputRoot "case_summary.csv"
$anchorSummaryPath = Join-Path $outputRoot "anchor_summary.csv"
$manifestPath = Join-Path $outputRoot "suite_manifest.json"

& $buildScript

$exePath = Join-Path $buildDir "Release\analog_runtime_r2b_probe.exe"
if (-not (Test-Path $exePath)) {
    $exePath = Join-Path $buildDir "analog_runtime_r2b_probe.exe"
}
if (-not (Test-Path $exePath)) {
    throw "Probe executable not found."
}

if (Test-Path $outputRoot) {
    Remove-Item -Recurse -Force $outputRoot
}
New-Item -ItemType Directory -Force -Path $outputRoot | Out-Null

$quietSeeds = @(20501, 20502, 20503, 20504, 20505, 20506, 20507, 20508)
$splitSeeds = @(20401, 20402, 20403, 20404, 20405, 20406, 20407, 20408)

$anchors = @(
    @{ label = "quiet_reference"; drive = 0.080; steps = 32768; focus = "quiet_reference"; seeds = $quietSeeds },
    @{ label = "first_precursor"; drive = 0.100; steps = 32768; focus = "first_precursor"; seeds = $quietSeeds },
    @{ label = "middle_precursor"; drive = 0.140; steps = 32768; focus = "middle_precursor"; seeds = $quietSeeds },
    @{ label = "corridor_interior"; drive = 0.200; steps = 32768; focus = "corridor_interior"; seeds = $splitSeeds },
    @{ label = "split_onset"; drive = 0.230; steps = 32768; focus = "split_onset"; seeds = $splitSeeds },
    @{ label = "split_center"; drive = 0.240; steps = 32768; focus = "split_center"; seeds = $splitSeeds },
    @{ label = "barrier_lock"; drive = 0.250; steps = 32768; focus = "barrier_lock"; seeds = $splitSeeds }
)

$rows = @()
foreach ($anchor in $anchors) {
    foreach ($seed in $anchor.seeds) {
        $caseLabel = "{0}_seed_{1}" -f $anchor.label, $seed
        $caseDir = Join-Path $outputRoot ($anchor.label + "\seed_" + $seed)
        New-Item -ItemType Directory -Force -Path $caseDir | Out-Null

        & $exePath `
            --output-dir $caseDir `
            --case-label $caseLabel `
            --seed $seed `
            --drive $anchor.drive `
            --steps $anchor.steps `
            --snapshot-interval 1024 `
            --nodes 128 `
            --enable-split-eligibility true `
            --enable-barrier-scaffold true `
            --enable-residue true

        if ($LASTEXITCODE -ne 0) {
            throw "Stage anchor case failed: $($anchor.label) / $seed"
        }

        $metrics = Import-Csv (Join-Path $caseDir "run_metrics.csv")
        $row = $metrics[0]
        $rows += [pscustomobject]@{
            anchor_label = $anchor.label
            focus = $anchor.focus
            seed = [int]$seed
            drive = [double]$anchor.drive
            steps = [int64]$anchor.steps
            regime = $row.regime
            mean_output = [double]$row.mean_output
            mean_abs_output = [double]$row.mean_abs_output
            mean_total_activation = [double]$row.mean_total_activation
            mean_forward_channel = [double]$row.mean_forward_channel
            mean_reverse_channel = [double]$row.mean_reverse_channel
            mean_directional_dominance = [double]$row.mean_directional_dominance
            mean_channel_coexistence = [double]$row.mean_channel_coexistence
            mean_split_eligibility = [double]$row.mean_split_eligibility
            mean_admissibility = [double]$row.mean_admissibility
            mean_residue = [double]$row.mean_residue
            mean_tension = [double]$row.mean_tension
            mean_barrier_scaffold = [double]$row.mean_barrier_scaffold
            corridor_edge_fraction = [double]$row.corridor_edge_fraction
            coexistence_edge_fraction = [double]$row.coexistence_edge_fraction
            barrier_edge_fraction = [double]$row.barrier_edge_fraction
            dual_active_node_fraction = [double]$row.dual_active_node_fraction
            output_interface_count = [int]$row.output_interface_count
        }
    }
}

$rows | Export-Csv -Path $caseSummaryPath -NoTypeInformation -Encoding ascii

$anchorSummary = foreach ($anchor in $anchors) {
    $anchorRows = @($rows | Where-Object { $_.anchor_label -eq $anchor.label })
    [pscustomobject]@{
        anchor_label = $anchor.label
        focus = $anchor.focus
        drive = [double]$anchor.drive
        seeds_tested = $anchorRows.Count
        quiet_count = ($anchorRows | Where-Object regime -eq "quiet_vector" | Measure-Object).Count
        precursor_count = ($anchorRows | Where-Object regime -eq "directional_precursor_candidate" | Measure-Object).Count
        corridor_count = ($anchorRows | Where-Object regime -eq "directional_corridor_candidate" | Measure-Object).Count
        split_count = ($anchorRows | Where-Object regime -eq "split_coexistence_candidate" | Measure-Object).Count
        lock_count = ($anchorRows | Where-Object regime -eq "scaffold_lock_candidate" | Measure-Object).Count
        mean_abs_output = [double](($anchorRows | Measure-Object -Property mean_abs_output -Average).Average)
        mean_total_activation = [double](($anchorRows | Measure-Object -Property mean_total_activation -Average).Average)
        mean_directional_dominance = [double](($anchorRows | Measure-Object -Property mean_directional_dominance -Average).Average)
        mean_channel_coexistence = [double](($anchorRows | Measure-Object -Property mean_channel_coexistence -Average).Average)
        mean_split_eligibility = [double](($anchorRows | Measure-Object -Property mean_split_eligibility -Average).Average)
        mean_admissibility = [double](($anchorRows | Measure-Object -Property mean_admissibility -Average).Average)
        mean_residue = [double](($anchorRows | Measure-Object -Property mean_residue -Average).Average)
        mean_tension = [double](($anchorRows | Measure-Object -Property mean_tension -Average).Average)
        mean_barrier_scaffold = [double](($anchorRows | Measure-Object -Property mean_barrier_scaffold -Average).Average)
        mean_corridor_edge_fraction = [double](($anchorRows | Measure-Object -Property corridor_edge_fraction -Average).Average)
        mean_coexistence_edge_fraction = [double](($anchorRows | Measure-Object -Property coexistence_edge_fraction -Average).Average)
        mean_barrier_edge_fraction = [double](($anchorRows | Measure-Object -Property barrier_edge_fraction -Average).Average)
        mean_dual_active_node_fraction = [double](($anchorRows | Measure-Object -Property dual_active_node_fraction -Average).Average)
        mean_output_interface_count = [double](($anchorRows | Measure-Object -Property output_interface_count -Average).Average)
    }
}

$anchorSummary | Export-Csv -Path $anchorSummaryPath -NoTypeInformation -Encoding ascii

$manifest = @{
    generated_at = (Get-Date).ToString("o")
    output_root = $outputRoot
    case_summary_csv = $caseSummaryPath
    anchor_summary_csv = $anchorSummaryPath
    anchors = $anchors
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath -Encoding ascii
