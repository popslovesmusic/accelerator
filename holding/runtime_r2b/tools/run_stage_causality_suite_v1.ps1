$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir
$buildScript = Join-Path $scriptDir "build_runtime_r2b.ps1"
$buildDir = Join-Path $rootDir "build\cmake"
$outputRoot = Join-Path $rootDir "outputs\runtime_r2b_stage_causality_suite_v1"
$caseSummaryPath = Join-Path $outputRoot "case_summary.csv"
$anchorSummaryPath = Join-Path $outputRoot "anchor_summary.csv"
$assessmentPath = Join-Path $outputRoot "assessment_summary.csv"
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

$variants = @(
    @{
        variant = "full"
        args = @(
            "--enable-split-eligibility", "true",
            "--enable-barrier-scaffold", "true",
            "--enable-residue", "true"
        )
    },
    @{
        variant = "eligibility_off"
        args = @(
            "--enable-split-eligibility", "false",
            "--enable-barrier-scaffold", "true",
            "--enable-residue", "true"
        )
    },
    @{
        variant = "scaffold_off"
        args = @(
            "--enable-split-eligibility", "true",
            "--enable-barrier-scaffold", "false",
            "--enable-residue", "true"
        )
    }
)

$anchors = @(
    @{ label = "corridor_interior"; drive = 0.200; steps = 32768; seeds = @(20401, 20402, 20403, 20404, 20405, 20406, 20407, 20408) },
    @{ label = "split_onset"; drive = 0.230; steps = 32768; seeds = @(20401, 20402, 20403, 20404, 20405, 20406, 20407, 20408) },
    @{ label = "split_center"; drive = 0.240; steps = 32768; seeds = @(20401, 20402, 20403, 20404, 20405, 20406, 20407, 20408) },
    @{ label = "barrier_lock"; drive = 0.250; steps = 32768; seeds = @(20401, 20402, 20403, 20404, 20405, 20406, 20407, 20408) }
)

$rows = @()
foreach ($anchor in $anchors) {
    foreach ($variant in $variants) {
        foreach ($seed in $anchor.seeds) {
            $caseLabel = "{0}_{1}_seed_{2}" -f $variant.variant, $anchor.label, $seed
            $caseDir = Join-Path $outputRoot ($variant.variant + "\" + $anchor.label + "\seed_" + $seed)
            New-Item -ItemType Directory -Force -Path $caseDir | Out-Null

            & $exePath `
                --output-dir $caseDir `
                --case-label $caseLabel `
                --seed $seed `
                --drive $anchor.drive `
                --steps $anchor.steps `
                --snapshot-interval 1024 `
                --nodes 128 `
                @($variant.args)

            if ($LASTEXITCODE -ne 0) {
                throw "Stage causality case failed: $($variant.variant) / $($anchor.label) / $seed"
            }

            $metrics = Import-Csv (Join-Path $caseDir "run_metrics.csv")
            $row = $metrics[0]
            $rows += [pscustomobject]@{
                variant = $variant.variant
                anchor_label = $anchor.label
                seed = [int]$seed
                drive = [double]$anchor.drive
                regime = $row.regime
                mean_directional_dominance = [double]$row.mean_directional_dominance
                mean_channel_coexistence = [double]$row.mean_channel_coexistence
                mean_split_eligibility = [double]$row.mean_split_eligibility
                mean_tension = [double]$row.mean_tension
                mean_barrier_scaffold = [double]$row.mean_barrier_scaffold
                corridor_edge_fraction = [double]$row.corridor_edge_fraction
                coexistence_edge_fraction = [double]$row.coexistence_edge_fraction
                barrier_edge_fraction = [double]$row.barrier_edge_fraction
                dual_active_node_fraction = [double]$row.dual_active_node_fraction
            }
        }
    }
}

$rows | Export-Csv -Path $caseSummaryPath -NoTypeInformation -Encoding ascii

$anchorSummary = @()
foreach ($anchor in $anchors) {
    $baselineRows = @($rows | Where-Object { $_.anchor_label -eq $anchor.label -and $_.variant -eq "full" })
    $baselineCoexistence = [double](($baselineRows | Measure-Object -Property coexistence_edge_fraction -Average).Average)
    $baselineBarrier = [double](($baselineRows | Measure-Object -Property barrier_edge_fraction -Average).Average)
    $baselineCorridor = [double](($baselineRows | Measure-Object -Property corridor_edge_fraction -Average).Average)

    foreach ($variant in $variants) {
        $variantRows = @($rows | Where-Object { $_.anchor_label -eq $anchor.label -and $_.variant -eq $variant.variant })
        $coexistence = [double](($variantRows | Measure-Object -Property coexistence_edge_fraction -Average).Average)
        $barrier = [double](($variantRows | Measure-Object -Property barrier_edge_fraction -Average).Average)
        $corridor = [double](($variantRows | Measure-Object -Property corridor_edge_fraction -Average).Average)

        $anchorSummary += [pscustomobject]@{
            anchor_label = $anchor.label
            variant = $variant.variant
            drive = [double]$anchor.drive
            seeds_tested = $variantRows.Count
            mean_directional_dominance = [double](($variantRows | Measure-Object -Property mean_directional_dominance -Average).Average)
            mean_channel_coexistence = [double](($variantRows | Measure-Object -Property mean_channel_coexistence -Average).Average)
            mean_split_eligibility = [double](($variantRows | Measure-Object -Property mean_split_eligibility -Average).Average)
            mean_tension = [double](($variantRows | Measure-Object -Property mean_tension -Average).Average)
            mean_barrier_scaffold = [double](($variantRows | Measure-Object -Property mean_barrier_scaffold -Average).Average)
            mean_corridor_edge_fraction = $corridor
            mean_coexistence_edge_fraction = $coexistence
            mean_barrier_edge_fraction = $barrier
            delta_corridor_vs_full = ($corridor - $baselineCorridor)
            delta_coexistence_vs_full = ($coexistence - $baselineCoexistence)
            delta_barrier_vs_full = ($barrier - $baselineBarrier)
        }
    }
}

$anchorSummary | Export-Csv -Path $anchorSummaryPath -NoTypeInformation -Encoding ascii

$assessmentRows = foreach ($anchor in $anchors) {
    $full = $anchorSummary | Where-Object { $_.anchor_label -eq $anchor.label -and $_.variant -eq "full" }
    $splitOff = $anchorSummary | Where-Object { $_.anchor_label -eq $anchor.label -and $_.variant -eq "eligibility_off" }
    $scaffoldOff = $anchorSummary | Where-Object { $_.anchor_label -eq $anchor.label -and $_.variant -eq "scaffold_off" }
    [pscustomobject]@{
        anchor_label = $anchor.label
        full_coexistence = [double]$full.mean_coexistence_edge_fraction
        full_barrier = [double]$full.mean_barrier_edge_fraction
        full_split_eligibility = [double]$full.mean_split_eligibility
        eligibility_off_coexistence_delta = [double]$splitOff.delta_coexistence_vs_full
        eligibility_off_barrier_delta = [double]$splitOff.delta_barrier_vs_full
        scaffold_off_coexistence_delta = [double]$scaffoldOff.delta_coexistence_vs_full
        scaffold_off_barrier_delta = [double]$scaffoldOff.delta_barrier_vs_full
    }
}

$assessmentRows | Export-Csv -Path $assessmentPath -NoTypeInformation -Encoding ascii

$manifest = @{
    generated_at = (Get-Date).ToString("o")
    output_root = $outputRoot
    case_summary_csv = $caseSummaryPath
    anchor_summary_csv = $anchorSummaryPath
    assessment_summary_csv = $assessmentPath
    variants = $variants
    anchors = $anchors
}
$manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding ascii
