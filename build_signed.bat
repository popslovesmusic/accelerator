@echo off
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
icpx -fsycl -O3 -o tools/structural_box_signed_v1_cpp/box_sim.exe tools/structural_box_signed_v1_cpp/main.cpp
