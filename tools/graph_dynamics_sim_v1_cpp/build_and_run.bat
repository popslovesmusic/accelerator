@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Community\VC\Auxiliary\Build\vcvars64.bat"

echo Compiling NetworkEngineAVX2...
cl /O2 /arch:AVX2 /openmp /EHsc /I. ^
    main.cpp NetworkEngineAVX2.cpp ^
    /Fe:network_sim_benchmark.exe

echo Compiling network_capi.dll...
cl /O2 /arch:AVX2 /openmp /EHsc /I. /LD ^
    network_capi.cpp NetworkEngineAVX2.cpp ^
    /Fe:network_capi.dll

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful. Running benchmark...
    network_sim_benchmark.exe
) else (
    echo Compilation failed.
)

