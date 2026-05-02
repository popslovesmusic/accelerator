@echo off
setlocal
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
.\tools\tda_module_v2_cpp\tda_multi_benchmark.exe %*
endlocal
