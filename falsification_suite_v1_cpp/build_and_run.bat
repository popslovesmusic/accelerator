@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

echo Compiling FalsificationSuiteAVX2...
cl /O2 /arch:AVX2 /openmp /EHsc /I. ^
    main.cpp FalsificationRunner.cpp ^
    /Fe:falsification_benchmark.exe

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful. Running benchmark...
    falsification_benchmark.exe
) else (
    echo Compilation failed.
)
