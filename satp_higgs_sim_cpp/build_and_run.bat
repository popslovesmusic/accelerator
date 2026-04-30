@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building SATP+Higgs 2D SIM SYCL...
icpx -fsycl -O3 -o satp_higgs_sim_cpp/satp_higgs_benchmark.exe satp_higgs_sim_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running benchmark...
    .\satp_higgs_sim_cpp\satp_higgs_benchmark.exe
) else (
    echo Build Failed.
)

endlocal
