@echo off
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
python tools/igsoa_gw_core_cpp/sim_governed.py --config results/test_gw.json --out results/test_gw_out
