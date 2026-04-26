@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

echo Compiling BifurcationAnalyzerAVX2...
cl /O2 /arch:AVX2 /openmp /EHsc /I. ^
    main.cpp BifurcationEngine.cpp ^
    /Fe:bifurcation_benchmark.exe

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful. Running benchmark...
    bifurcation_benchmark.exe
) else (
    echo Compilation failed.
)
