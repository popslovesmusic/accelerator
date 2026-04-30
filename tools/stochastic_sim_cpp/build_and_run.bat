@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building Stochastic SIM SYCL...
icpx -fsycl -O3 -o stochastic_sim_cpp/stochastic_sim_benchmark.exe stochastic_sim_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running benchmark...
    .\stochastic_sim_cpp\stochastic_sim_benchmark.exe
) else (
    echo Build Failed.
)

endlocal
