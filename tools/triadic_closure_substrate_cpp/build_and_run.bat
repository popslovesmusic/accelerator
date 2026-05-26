@echo off
setlocal enabledelayedexpansion

set SRC_DIR=%~dp0src
set OUT_EXE=%~dp0triadic_sim.exe

echo Compiling Triadic Closure Substrate Engine (AVX2 mode)...

:: Proactively search for oneAPI
where dpcpp >nul 2>nul
if %errorlevel% neq 0 (
    if exist "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" (
        echo Found oneAPI setvars.bat. Initializing environment...
        call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat" --force
    )
)

:: Try to use Intel DPCPP if available
where dpcpp >nul 2>nul
if %errorlevel% equ 0 (
    echo Found Intel DPC++. Compiling with SYCL and AVX2 optimizations...
    dpcpp /O3 /QxAVX2 /fp:fast /openmp -DUSE_SYCL -o "%OUT_EXE%" "%SRC_DIR%\main.cpp"
    if !errorlevel! neq 0 exit /b !errorlevel!
    goto :success
)

:: Check for MSVC
where cl >nul 2>nul
if %errorlevel% equ 0 goto :compile

echo MSVC (cl) not found in path. Searching for vcvarsall.bat using vswhere...
set "VSWHERE_PATH=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "!VSWHERE_PATH!" (
    echo vswhere not found at standard location. Falling back to manual search...
    for /d %%i in ("C:\Program Files\Microsoft Visual Studio\*") do (
        if exist "%%i\Community\VC\Auxiliary\Build\vcvarsall.bat" (
            set "VCVARS_PATH=%%i\Community\VC\Auxiliary\Build\vcvarsall.bat"
            goto :found_vcvars
        )
    )
) else (
    for /f "usebackq tokens=*" %%i in (`"!VSWHERE_PATH!" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do (
        set "VS_INSTALL_PATH=%%i"
    )
    if exist "!VS_INSTALL_PATH!\VC\Auxiliary\Build\vcvarsall.bat" (
        set "VCVARS_PATH=!VS_INSTALL_PATH!\VC\Auxiliary\Build\vcvarsall.bat"
        goto :found_vcvars
    )
)

echo Could not find vcvarsall.bat. Please run in a Developer Command Prompt.
exit /b 1

:found_vcvars
echo Found: !VCVARS_PATH!
call "!VCVARS_PATH!" x64
goto :compile

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
