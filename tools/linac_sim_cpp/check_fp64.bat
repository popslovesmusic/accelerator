@echo off
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
icpx -fsycl -o linac_sim_cpp/check_fp64.exe linac_sim_cpp/check_fp64.cpp
if %ERRORLEVEL% EQU 0 (
    .\linac_sim_cpp\check_fp64.exe
)
