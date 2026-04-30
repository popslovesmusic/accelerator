@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"

echo Compiling CircularEngineAVX2...
cl /O2 /arch:AVX2 /openmp /EHsc /I. ^
    main.cpp CircularEngineAVX2.cpp ^
    /Fe:circular_sim_benchmark.exe

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful. Running benchmark...
    circular_sim_benchmark.exe
) else (
    echo Compilation failed.
)

