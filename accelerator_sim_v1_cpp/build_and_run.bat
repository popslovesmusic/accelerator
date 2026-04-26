@echo off
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

echo Compiling AcceleratorEngineAVX2...
cl /O2 /arch:AVX2 /openmp /EHsc /I. /I"D:\acellorator\Simulation_engines_extracted_2026-04-25" ^
    main.cpp AcceleratorEngineAVX2.cpp PoissonSolver.cpp ^
    /Fe:acc_sim_benchmark.exe ^
    /link /LIBPATH:"D:\acellorator\Simulation_engines_extracted_2026-04-25" libfftw3-3.lib

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful. Running benchmark...
    acc_sim_benchmark.exe
) else (
    echo Compilation failed.
)
