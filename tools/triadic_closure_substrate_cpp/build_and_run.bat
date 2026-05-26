@echo off
setlocal enabledelayedexpansion

set SRC_DIR=%~dp0src
set OUT_EXE=%~dp0triadic_sim.exe

echo Compiling Triadic Closure Substrate Engine (AVX2 mode)...

:: Try to use Intel DPCPP if available
where dpcpp >nul 2>nul
if %errorlevel% equ 0 (
    echo Found Intel DPC++. Compiling with SYCL and AVX2 optimizations...
    dpcpp /O3 /QxAVX2 /fp:fast /openmp -o "%OUT_EXE%" "%SRC_DIR%\main.cpp"
    if !errorlevel! neq 0 exit /b !errorlevel!
    goto :success
)

:: Check for MSVC
where cl >nul 2>nul
if %errorlevel% equ 0 goto :compile

echo MSVC (cl) not found in path. Searching for vcvarsall.bat...
for /d %%i in ("C:\Program Files\Microsoft Visual Studio\*") do (
    if exist "%%i\Community\VC\Auxiliary\Build\vcvarsall.bat" (
        echo Found: %%i\Community\VC\Auxiliary\Build\vcvarsall.bat
        call "%%i\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
        goto :compile
    )
)
echo Could not find vcvarsall.bat. Please run in a Developer Command Prompt.
exit /b 1

:compile
echo Compiling with MSVC (AVX2 and OpenMP)...
cl /EHsc /O2 /arch:AVX2 /openmp:experimental /Fe"%OUT_EXE%" "%SRC_DIR%\main.cpp"
if %errorlevel% neq 0 (
    echo Compilation failed.
    exit /b %errorlevel%
)
:: Cleanup MSVC obj files
del "%~dp0*.obj" >nul 2>nul

:success
echo Compilation successful: %OUT_EXE%
exit /b 0
