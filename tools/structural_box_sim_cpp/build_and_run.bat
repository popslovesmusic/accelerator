@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building Structural Box SIM SYCL...
icpx -fsycl -O3 -o structural_box_sim_cpp/box_sim_benchmark.exe structural_box_sim_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running benchmark...
    .\structural_box_sim_cpp\box_sim_benchmark.exe
) else (
    echo Build Failed.
)

endlocal
