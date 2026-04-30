@echo off
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
python scripts/multi_sim_runner.py --config configs/multi_runs/cpp_ecosystem_verification.json
