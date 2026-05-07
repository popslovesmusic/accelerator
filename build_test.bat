@echo off
call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
icpx -fsycl -DDASE_ENABLE_UHD770_SYCL -DDASE_UHD770_FP32_DEFAULT -DUSE_FFTW3 -O2 -std=c++17 ^
  -I tools/Simulation_engines_extracted_2026-04-25/dase_cli/src ^
  -I tools/Simulation_engines_extracted_2026-04-25/src/cpp ^
  -I tools/Simulation_engines_extracted_2026-04-25 ^
  tools/Simulation_engines_extracted_2026-04-25/dase_cli/src/main.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/dase_cli/src/command_router.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/dase_cli/src/engine_manager.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/dase_cli/src/analysis_router.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/dase_cli/src/engine_fft_analysis.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/dase_cli/src/python_bridge.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/src/cpp/igsoa_gw_engine/core/symmetry_field.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/src/cpp/igsoa_gw_engine/core/fractional_solver.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/src/cpp/igsoa_gw_engine/core/source_manager.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/src/cpp/igsoa_gw_engine/core/projection_operators.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/src/cpp/igsoa_gw_engine/core/echo_generator.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/src/cpp/utils/logger.cpp ^
  tools/Simulation_engines_extracted_2026-04-25/libfftw3-3.lib ^
  -o dase_cli_test.exe
