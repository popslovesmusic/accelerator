@echo off
setlocal

set SRC_DIR=%~dp0src
set OUT_EXE=%~dp0triadic_sim.exe

echo Compiling Triadic Closure Substrate Engine (AVX2 mode)...

:: Try to use Intel DPCPP if available (for SYCL/AVX2), otherwise fallback to MSVC
where dpcpp >nul 2>nul
if %errorlevel% equ 0 (
    echo Found Intel DPC++. Compiling with SYCL and AVX2 optimizations...
    dpcpp /O3 /QxAVX2 /fp:fast /openmp -o "%OUT_EXE%" "%SRC_DIR%\main.cpp"
    if %errorlevel% neq 0 exit /b %errorlevel%
) else (
    echo Intel DPC++ not found. Falling back to MSVC with AVX2 and OpenMP...
    cl /EHsc /O2 /arch:AVX2 /openmp /Fe"%OUT_EXE%" "%SRC_DIR%\main.cpp"
    if %errorlevel% neq 0 (
        echo Compilation failed. Ensure you are running in a Developer Command Prompt.
        exit /b %errorlevel%
    )
    :: Cleanup MSVC obj files
    del "%~dp0*.obj" >nul 2>nul
)

echo Compilation successful: %OUT_EXE%
exit /b 0
