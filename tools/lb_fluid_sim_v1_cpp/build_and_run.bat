@echo off
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Compiling LB Fluid Engine SYCL...
icpx -fsycl -O3 -I. main.cpp lb_capi.cpp -o lb_benchmark.exe

echo Compiling LB C-API DLL...
icpx -fsycl -O3 -shared lb_capi.cpp -o lb_engine.dll

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful. Running benchmark...
    lb_benchmark.exe
) else (
    echo Compilation failed.
)
