@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building Structural Box SIM SYCL...
icpx -fsycl -O3 -o box_sim.exe main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful.
) else (
    echo Build Failed.
)

endlocal
