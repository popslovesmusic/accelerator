@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building Multi-Dimensional TDA Module C++...
icpx -fsycl -O3 -std=c++17 -o tools/tda_module_v2_cpp/tda_multi_benchmark.exe tools/tda_module_v2_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running controls...
    .\tools\tda_module_v2_cpp\tda_multi_benchmark.exe
) else (
    echo Build Failed.
)

endlocal
