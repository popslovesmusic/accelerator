@echo off
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Compiling Metrics Engine SYCL...
icpx -fsycl -O3 -I. main.cpp metrics_capi.cpp -o metrics_benchmark.exe

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful. Running benchmark...
    metrics_benchmark.exe
) else (
    echo Compilation failed.
)
