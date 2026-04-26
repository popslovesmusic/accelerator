@echo off
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

echo Compiling Kuramoto Engine SYCL...
icpx -fsycl -O3 -I. main.cpp kuramoto_capi.cpp -o kuramoto_benchmark.exe

echo Compiling Kuramoto C-API DLL...
icpx -fsycl -O3 -shared kuramoto_capi.cpp -o kuramoto_engine.dll

if %ERRORLEVEL% EQU 0 (
    echo Compilation successful. Running benchmark...
    kuramoto_benchmark.exe
) else (
    echo Compilation failed.
)
