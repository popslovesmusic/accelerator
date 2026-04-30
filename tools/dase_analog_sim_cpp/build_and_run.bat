@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building D-ASE Analog SIM SYCL...
icpx -fsycl -O3 -o dase_analog_benchmark.exe main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running benchmark...
    .\dase_analog_benchmark.exe
) else (
    echo Build Failed.
)

endlocal
