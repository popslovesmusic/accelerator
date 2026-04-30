@echo off
setlocal

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Building Spectral Analysis C++...
icpx -fsycl -O3 -std=c++17 -o spectral_analysis_v1_cpp/spectral_analysis_benchmark.exe spectral_analysis_v1_cpp/main.cpp

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running built-in control...
    .\spectral_analysis_v1_cpp\spectral_analysis_benchmark.exe
) else (
    echo Build Failed.
)

endlocal
