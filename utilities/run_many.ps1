<#
.SYNOPSIS
Run many acellorator simulation configs in a batch and index outputs.

.DESCRIPTION
Expands one or more config globs/paths, optionally overrides seed(s) into a generated
config copy (without touching originals), runs the target sim, and writes an index CSV
with output directories + final metrics extracted from each run's summary.json.

By default it uses tool definitions from tool_manifest.json (by tool name). You can also
run an explicit script path.

.EXAMPLE
pwsh -File utilities/run_many.ps1 -Tool ca_admissibility_sim_v1 -Configs "ca_admissibility_sim_v1/configs/*.json" -OutRoot outputs/batch_ca

.EXAMPLE
pwsh -File utilities/run_many.ps1 -Tool fsa_rule_engine_sim_v1 -Configs "outputs/research_residue_necessity_2026-04-25/configs/fsa_sweep_*.json" -OutRoot outputs/batch_fsa -Seeds 21,22,23

.EXAMPLE
pwsh -File utilities/run_many.ps1 -Script structural_box_sim_v2/sim.py -Configs "structural_box_sim_v2/configs/default.json" -Seeds 1001,1002,1003
#>

[CmdletBinding(DefaultParameterSetName = "Tool")]
param(
  [Parameter(ParameterSetName = "Tool", Mandatory = $true)]
  [string]$Tool,

  [Parameter(ParameterSetName = "Script", Mandatory = $true)]
  [string]$Script,

  [Parameter(Mandatory = $true)]
  [string[]]$Configs,

  [string]$OutRoot,

  [string[]]$Seeds,

  [string]$Python = "python",

  [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoRoot {
  $here = (Get-Location).Path
  $p = Get-Item -LiteralPath $here
  while ($true) {
    $candidate = Join-Path $p.FullName "tool_manifest.json"
    if (Test-Path -LiteralPath $candidate) { return $p.FullName }
    if (-not $p.Parent) { throw "Could not find tool_manifest.json walking up from $here" }
    $p = $p.Parent
  }
}

function Expand-ConfigInputs([string[]]$inputs, [string]$repoRoot) {
  $all = New-Object System.Collections.Generic.List[string]
  foreach ($raw in $inputs) {
    $path = $raw
    if (-not [System.IO.Path]::IsPathRooted($path)) {
      $path = Join-Path $repoRoot $path
    }

    if (Test-Path -LiteralPath $path -PathType Container) {
      Get-ChildItem -LiteralPath $path -File -Filter "*.json" | ForEach-Object { $all.Add($_.FullName) }
      continue
    }

    # glob
    $dir = Split-Path -Parent $path
    $leaf = Split-Path -Leaf $path
    if (Test-Path -LiteralPath $dir -PathType Container -ErrorAction SilentlyContinue) {
      $matches = Get-ChildItem -Path (Join-Path $dir $leaf) -File -ErrorAction SilentlyContinue
      if ($matches) { $matches | ForEach-Object { $all.Add($_.FullName) }; continue }
    }

    if (Test-Path -LiteralPath $path -PathType Leaf) {
      $all.Add((Resolve-Path -LiteralPath $path).Path)
      continue
    }

    throw "Config input not found: $raw (resolved to $path)"
  }

  return @($all | Sort-Object -Unique)
}

function Get-ToolEntry([string]$toolName, [string]$repoRoot) {
  $manifestPath = Join-Path $repoRoot "tool_manifest.json"
  $manifest = Get-Content -Raw -Encoding UTF8 $manifestPath | ConvertFrom-Json
  $entry = $manifest.tools | Where-Object { $_.name -eq $toolName } | Select-Object -First 1
  if (-not $entry) { throw "Tool '$toolName' not found in $manifestPath" }
  return $entry
}

function Ensure-Dir([string]$path) {
  New-Item -ItemType Directory -Force -Path $path | Out-Null
}

function Safe-Name([string]$s) {
  ($s -replace "[^a-zA-Z0-9._-]", "_")
}

function Apply-SeedOverride([object]$configObj, [int]$seed) {
  # Common patterns across this repo:
  # - root-level "seed"
  # - nested "initial_condition.seed"
  if ($null -ne $configObj.PSObject.Properties["seed"]) {
    $configObj.seed = $seed
  }
  if ($null -ne $configObj.PSObject.Properties["initial_condition"]) {
    $ic = $configObj.initial_condition
    if ($null -ne $ic -and $null -ne $ic.PSObject.Properties["seed"]) {
      $ic.seed = $seed
    }
  }
  return $configObj
}

function Extract-FinalMetrics([string]$summaryPath) {
  if (-not (Test-Path -LiteralPath $summaryPath)) { return $null }
  $summary = Get-Content -Raw -Encoding UTF8 $summaryPath | ConvertFrom-Json

  if ($null -ne $summary.PSObject.Properties["final_metrics"]) { return $summary.final_metrics }
  if ($null -ne $summary.PSObject.Properties["final"]) { return $summary.final }
  return $null
}

function Parse-Seeds([string[]]$rawSeeds) {
  if (-not $rawSeeds) { return @() }
  $tokens = New-Object System.Collections.Generic.List[int]
  foreach ($item in $rawSeeds) {
    if ($null -eq $item) { continue }
    foreach ($tok in ($item -split "[,\\s]+")) {
      if ([string]::IsNullOrWhiteSpace($tok)) { continue }
      $tokens.Add([int]$tok)
    }
  }
  return @($tokens | Sort-Object -Unique)
}

$repoRoot = Resolve-RepoRoot
if (-not $OutRoot) {
  $stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
  $OutRoot = Join-Path $repoRoot ("outputs\\batch_" + $stamp)
} elseif (-not [System.IO.Path]::IsPathRooted($OutRoot)) {
  $OutRoot = Join-Path $repoRoot $OutRoot
}
Ensure-Dir $OutRoot
$OutRoot = (Resolve-Path -LiteralPath $OutRoot).Path

$runsRoot = Join-Path $OutRoot "runs"
$genCfgRoot = Join-Path $OutRoot "configs_generated"
$analysisRoot = Join-Path $OutRoot "analysis"
Ensure-Dir $runsRoot
Ensure-Dir $genCfgRoot
Ensure-Dir $analysisRoot

$configPaths = @(Expand-ConfigInputs -inputs $Configs -repoRoot $repoRoot)
if (-not $configPaths -or @($configPaths).Count -eq 0) { throw "No configs matched inputs." }

$Seeds = Parse-Seeds -rawSeeds $Seeds

if ($PSCmdlet.ParameterSetName -eq "Tool") {
  $entry = Get-ToolEntry -toolName $Tool -repoRoot $repoRoot
  $Script = Join-Path $repoRoot $entry.entry_point
}

if (-not [System.IO.Path]::IsPathRooted($Script)) {
  $Script = Join-Path $repoRoot $Script
}

$Script = (Resolve-Path -LiteralPath $Script).Path

Write-Host "RepoRoot:  $repoRoot"
Write-Host "Script:    $Script"
Write-Host "OutRoot:   $OutRoot"
Write-Host "Configs:   $(@($configPaths).Count)"
Write-Host "Seeds:     $([string]::Join(',', @($Seeds | ForEach-Object { $_.ToString() })))"
Write-Host ""

$index = New-Object System.Collections.Generic.List[object]

foreach ($cfg in $configPaths) {
  $cfgBase = [System.IO.Path]::GetFileNameWithoutExtension($cfg)
  $cfgSafe = Safe-Name $cfgBase

  $seedList = @()
  if ($Seeds.Count -gt 0) { $seedList = $Seeds } else { $seedList = @($null) }

  foreach ($seed in $seedList) {
    $runName = $cfgSafe
    $cfgToRun = $cfg
    if ($null -ne $seed) {
      $runName = "${cfgSafe}__seed${seed}"
      $cfgObj = Get-Content -Raw -Encoding UTF8 $cfg | ConvertFrom-Json
      $cfgObj = Apply-SeedOverride -configObj $cfgObj -seed $seed
      $cfgToRun = Join-Path $genCfgRoot ("$runName.json")
      $cfgObj | ConvertTo-Json -Depth 40 | Set-Content -Encoding UTF8 $cfgToRun
    }

    $outDir = Join-Path $runsRoot $runName
    Ensure-Dir $outDir

    $logPath = Join-Path $outDir "run.log"
    $cmdLine = "$Python `"$Script`" --config `"$cfgToRun`" --out `"$outDir`""
    Set-Content -LiteralPath (Join-Path $outDir "cmd.txt") -Encoding UTF8 -Value $cmdLine

    Write-Host "==> $runName"
    Write-Host "    Config: $cfgToRun"
    Write-Host "    Out:    $outDir"

    $status = "DRY_RUN"
    $elapsed = $null
    $summaryPath = Join-Path $outDir "summary.json"

    if (-not $DryRun) {
      $sw = [System.Diagnostics.Stopwatch]::StartNew()
      try {
        & $Python $Script --config $cfgToRun --out $outDir 2>&1 | Tee-Object -FilePath $logPath | Out-Null
        $status = "OK"
      } catch {
        $status = "ERROR"
        $_ | Out-String | Add-Content -Encoding UTF8 $logPath
      } finally {
        $sw.Stop()
        $elapsed = [math]::Round($sw.Elapsed.TotalSeconds, 3)
      }
    }

    $finalMetrics = $null
    if (Test-Path -LiteralPath $summaryPath) {
      $finalMetrics = Extract-FinalMetrics -summaryPath $summaryPath
    }

    $index.Add([pscustomobject]@{
      run_name = $runName
      status = $status
      seed = $seed
      config_path = $cfgToRun
      original_config_path = $cfg
      out_dir = $outDir
      summary_path = (Test-Path -LiteralPath $summaryPath) ? $summaryPath : $null
      elapsed_sec = $elapsed
      final_metrics_json = ($finalMetrics | ConvertTo-Json -Compress -Depth 20)
    })
  }
}

$indexPath = Join-Path $analysisRoot "index.csv"
$index | Export-Csv -NoTypeInformation -Encoding UTF8 -Path $indexPath
Write-Host ""
Write-Host "Wrote index: $indexPath"
