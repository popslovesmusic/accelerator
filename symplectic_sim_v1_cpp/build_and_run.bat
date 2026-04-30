@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building Symplectic SIM C++...
icpx -fsycl -O3 -std=c++17 -o symplectic_sim_v1_cpp/symplectic_sim_benchmark.exe symplectic_sim_v1_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running benchmark...
    .\symplectic_sim_v1_cpp\symplectic_sim_benchmark.exe
) else (
    echo Build Failed.
)

endlocal
