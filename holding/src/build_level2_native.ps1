param(
    [string]$SourceDir = $PSScriptRoot,
    [string]$Output = "",
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"

function Get-PythonBuildConfig {
    $script = @'
import json
import pathlib
import sys
import sysconfig

try:
    import pybind11
except ImportError as exc:
    raise SystemExit(f"pybind11 is required to build _level2_native: {exc}")

base_prefix = pathlib.Path(sys.base_prefix)
version_nodot = sysconfig.get_config_var("py_version_nodot") or f"{sys.version_info.major}{sys.version_info.minor}"
python_lib = base_prefix / "libs" / f"python{version_nodot}.lib"
payload = {
    "python_exe": sys.executable,
    "python_include": sysconfig.get_path("include"),
    "pybind11_include": pybind11.get_include(),
    "ext_suffix": sysconfig.get_config_var("EXT_SUFFIX") or ".pyd",
    "python_lib": str(python_lib),
}
print(json.dumps(payload))
'@
    $json = @"
$script
"@ | python -
    if (-not $json) {
        throw "Failed to query Python build configuration."
    }
    return $json | ConvertFrom-Json
}

function Get-VsWherePath {
    foreach ($candidate in @(
        "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe",
        "C:\Program Files\Microsoft Visual Studio\Installer\vswhere.exe"
    )) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }
    return $null
}

function Get-VcVarsBatch {
    $vswhere = Get-VsWherePath
    if (-not $vswhere) {
        return $null
    }

    $installationPath = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
    if (-not $installationPath) {
        return $null
    }

    $vcvars = Join-Path $installationPath "VC\Auxiliary\Build\vcvars64.bat"
    if (Test-Path $vcvars) {
        return $vcvars
    }
    return $null
}

function Get-ClPath {
    $command = Get-Command cl -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }
    return $null
}

$sourceRoot = (Resolve-Path $SourceDir).Path
$config = Get-PythonBuildConfig
$sourceFiles = @(
    (Join-Path $sourceRoot "level2_pybind_module.cpp"),
    (Join-Path $sourceRoot "level2_pde_engine.cpp")
)

foreach ($file in $sourceFiles) {
    if (-not (Test-Path $file)) {
        throw "Source file not found: $file"
    }
}

if (-not (Test-Path $config.python_include)) {
    throw "Python include directory not found: $($config.python_include)"
}
if (-not (Test-Path $config.pybind11_include)) {
    throw "pybind11 include directory not found: $($config.pybind11_include)"
}
if (-not (Test-Path $config.python_lib)) {
    throw "Python import library not found: $($config.python_lib)"
}

if (-not $Output) {
    $Output = Join-Path $sourceRoot ("_level2_native" + $config.ext_suffix)
}
$outputPath = [System.IO.Path]::GetFullPath($Output)
$outputDir = Split-Path -Parent $outputPath
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

if ($Rebuild -and (Test-Path $outputPath)) {
    Remove-Item -LiteralPath $outputPath -Force
}

$clPath = Get-ClPath
$vcvarsBatch = $null
if (-not $clPath) {
    $vcvarsBatch = Get-VcVarsBatch
    if (-not $vcvarsBatch) {
        throw "Could not find cl.exe on PATH or a Visual Studio vcvars64.bat. Run from a Developer PowerShell or install Visual Studio Build Tools."
    }
}

$quotedSources = $sourceFiles | ForEach-Object { '"' + $_ + '"' }
$compileArgs = @(
    "cl",
    "/nologo",
    "/std:c++17",
    "/O2",
    "/EHsc",
    "/LD",
    "/openmp",
    "/DNOMINMAX",
    "/DWIN32",
    "/D_WINDOWS",
    "/bigobj",
    "/I`"$($config.python_include)`"",
    "/I`"$($config.pybind11_include)`""
) + $quotedSources + @(
    "/link",
    "/OUT:`"$outputPath`"",
    "`"$($config.python_lib)`""
)
$compileCommand = ($compileArgs -join " ")

if ($vcvarsBatch) {
    $tempCmd = Join-Path $env:TEMP ("build_level2_native_" + [System.Guid]::NewGuid().ToString("N") + ".cmd")
    @(
        "@echo off",
        "call `"$vcvarsBatch`"",
        "if errorlevel 1 exit /b %errorlevel%",
        $compileCommand,
        "exit /b %errorlevel%"
    ) | Set-Content -LiteralPath $tempCmd -Encoding ASCII
    try {
        & cmd.exe /c $tempCmd
        if ($LASTEXITCODE -ne 0) {
            throw "Native module build failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Remove-Item -LiteralPath $tempCmd -Force -ErrorAction SilentlyContinue
    }
}
else {
    Invoke-Expression $compileCommand
    if ($LASTEXITCODE -ne 0) {
        throw "Native module build failed with exit code $LASTEXITCODE."
    }
}

if (-not (Test-Path $outputPath)) {
    throw "Build completed without producing $outputPath"
}

Write-Host "Built native module:"
Write-Host "  $outputPath"
Write-Host ""
Write-Host "Example use:"
Write-Host "  python -m rerun_v23.tools.batch_wrapper --config <config.json> --batch-id <batch_id> --backend native"
