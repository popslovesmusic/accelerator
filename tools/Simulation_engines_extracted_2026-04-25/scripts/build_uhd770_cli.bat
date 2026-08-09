@echo off
setlocal
pushd "%~dp0.."

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

set BIN_DIR=bin\uhd770
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

echo Building DASE JSON CLI with UHD 770 SYCL diagnostics...
icpx -fsycl -DDASE_ENABLE_UHD770_SYCL -DDASE_UHD770_FP32_DEFAULT -DUSE_FFTW3 -O2 -std=c++17 ^
  -I dase_cli\src -I src\cpp -I . ^
  dase_cli\src\main.cpp ^
  dase_cli\src\command_router.cpp ^
  dase_cli\src\engine_manager.cpp ^
  dase_cli\src\analysis_router.cpp ^
  dase_cli\src\engine_fft_analysis.cpp ^
  dase_cli\src\python_bridge.cpp ^
  src\cpp\igsoa_gw_engine\core\symmetry_field.cpp ^
  src\cpp\igsoa_gw_engine\core\fractional_solver.cpp ^
  src\cpp\igsoa_gw_engine\core\source_manager.cpp ^
  src\cpp\igsoa_gw_engine\core\projection_operators.cpp ^
  src\cpp\igsoa_gw_engine\core\echo_generator.cpp ^
  src\cpp\utils\logger.cpp ^
  libfftw3-3.lib ^
  -o "%BIN_DIR%\dase_cli_json_uhd770.exe"

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Binary: %BIN_DIR%\dase_cli_json_uhd770.exe
) else (
    echo Build Failed.
)

popd
endlocal
