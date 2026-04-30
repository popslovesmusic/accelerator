@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building Parameter Optimizer C++...
icpx -fsycl -O3 -std=c++17 -o parameter_optimizer_v1_cpp/parameter_optimizer.exe parameter_optimizer_v1_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful.
    .\parameter_optimizer_v1_cpp\parameter_optimizer.exe --out outputs/parameter_optimizer_v1_cpp/smoke
) else (
    echo Build Failed.
)

endlocal
