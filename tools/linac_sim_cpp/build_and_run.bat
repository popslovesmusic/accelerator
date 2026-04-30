@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building Linac SIM SYCL...
icpx -fsycl -O3 -o linac_sim_cpp/linac_sim_benchmark.exe linac_sim_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running benchmark...
    .\linac_sim_cpp\linac_sim_benchmark.exe
) else (
    echo Build Failed.
)

endlocal
