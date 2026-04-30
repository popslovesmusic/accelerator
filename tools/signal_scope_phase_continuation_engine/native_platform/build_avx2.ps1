$ErrorActionPreference = "Stop"

$vcvars = "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
if (!(Test-Path $vcvars)) {
    # Fallback or search for vcvars
    $vcvars = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
}

$compileCmd = "cl /O2 /arch:AVX2 /LD /EHsc phase_core_avx2.cpp /Fe:phase_core_avx2.dll"

Write-Host "🚀 Compiling Phase Core AVX2 Backend..."
& cmd /c "call `"$vcvars`" && $compileCmd"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Compilation successful: phase_core_avx2.dll"
} else {
    Write-Host "❌ Compilation failed."
    exit $LASTEXITCODE
}
