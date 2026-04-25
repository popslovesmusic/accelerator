param(
    [string]$Source = (Join-Path $PSScriptRoot "level2_results_analyzer.cpp"),
    [string]$Output = (Join-Path $PSScriptRoot "level2_results_analyzer.exe")
)

$ErrorActionPreference = "Stop"

function Get-AvailableCompiler {
    foreach ($name in @("cl", "clang++", "g++")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            return $cmd
        }
    }
    return $null
}

if (-not (Test-Path $Source)) {
    throw "Source file not found: $Source"
}

$compiler = Get-AvailableCompiler
if (-not $compiler) {
    Write-Host "No C++ compiler found on PATH."
    Write-Host "Run this script from a Visual Studio Developer PowerShell, or add clang++/g++ to PATH."
    exit 1
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Output) | Out-Null

switch ($compiler.Name.ToLowerInvariant()) {
    "cl" {
        & $compiler.Source /std:c++17 /O2 /EHsc /nologo /Fe:$Output $Source
        break
    }
    "clang++" {
        & $compiler.Source -std=c++17 -O3 -o $Output $Source
        break
    }
    "g++" {
        & $compiler.Source -std=c++17 -O3 -o $Output $Source
        break
    }
    default {
        throw "Unsupported compiler: $($compiler.Name)"
    }
}

if (-not (Test-Path $Output)) {
    throw "Build completed without producing $Output"
}

Write-Host "Built native analyzer:"
Write-Host "  $Output"
Write-Host ""
Write-Host "Example use:"
Write-Host "  python -m src.analyze_results --input-root C:\Users\j\Documents\MPF\orientation\level2\outputs_batches --output-prefix C:\Users\j\Documents\MPF\orientation\level2\outputs_consolidated\level2_analysis"
