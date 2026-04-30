@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building TDA Module C++...
icpx -fsycl -O3 -std=c++17 -o tda_module_v1_cpp/tda_benchmark.exe tda_module_v1_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running controls...
    .\tda_module_v1_cpp\tda_benchmark.exe
) else (
    echo Build Failed.
)

endlocal
