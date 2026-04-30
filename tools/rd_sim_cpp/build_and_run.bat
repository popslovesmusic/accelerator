@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building RD SIM SYCL...
icpx -fsycl -O3 -o rd_sim_cpp/rd_sim_benchmark.exe rd_sim_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running benchmark...
    .\rd_sim_cpp\rd_sim_benchmark.exe
) else (
    echo Build Failed.
)

endlocal
