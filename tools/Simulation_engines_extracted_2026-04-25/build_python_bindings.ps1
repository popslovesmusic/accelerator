$ErrorActionPreference = "Stop"

# 1. Detect Paths
$py_include = python -c "import sysconfig; print(sysconfig.get_paths()['include'])"
$py_libdir = python -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR'))"
$pybind_include = python -c "import pybind11; print(pybind11.get_include())"

$engine_root = "D:\projects\acellorator\tools\Simulation_engines_extracted_2026-04-25"
$cpp_dir = "$engine_root\src\cpp"
$fftw_lib = "$engine_root\libfftw3-3.lib"

# 2. Visual Studio Environment
$vcvars = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if (!(Test-Path $vcvars)) {
    $vcvars = "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"
}

# 3. Compilation Command
$src_files = "`"$cpp_dir\python_bindings.cpp`" `"$cpp_dir\analog_universal_node_engine_avx2.cpp`""
$includes = "/I `"$cpp_dir`" /I `"$engine_root`" /I `"$py_include`" /I `"$pybind_include`""
$libs = "/link /LIBPATH:`"$py_libdir`" `"$fftw_lib`" /OUT:dase_engine.pyd"

# Added /std:c++17 for nested namespace support
$compileCmd = "cl /O2 /arch:AVX2 /LD /EHsc /openmp /std:c++17 $includes $src_files $libs"

Write-Host "Compiling DASE Engine..."
& cmd /c "call `"$vcvars`" && $compileCmd"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Compilation successful: dase_engine.pyd"
    $target_dir = "D:\projects\acellorator\tools\signal_scope_phase_continuation_engine\native_platform"
    if (!(Test-Path $target_dir)) {
        New-Item -ItemType Directory -Path $target_dir -Force
    }
    Copy-Item "dase_engine.pyd" "$target_dir\dase_engine.pyd" -Force
    Write-Host "Extension deployed to native_platform."
} else {
    Write-Host "Compilation failed."
    exit $LASTEXITCODE
}
