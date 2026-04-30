@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building MC Ensemble C++...
icpx -fsycl -O3 -std=c++17 -o mc_ensemble_sim_v1_cpp/mc_ensemble_runner.exe mc_ensemble_sim_v1_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful.
    .\mc_ensemble_sim_v1_cpp\mc_ensemble_runner.exe --out outputs/mc_ensemble_sim_v1_cpp/smoke
) else (
    echo Build Failed.
)

endlocal
