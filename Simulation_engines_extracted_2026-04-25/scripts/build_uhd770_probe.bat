@echo off
setlocal
pushd "%~dp0.."

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

set BIN_DIR=bin\uhd770
set OUT_DIR=outputs\uhd770\device_probe
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

echo Building UHD 770 device probe...
icpx -fsycl -DDASE_ENABLE_UHD770_SYCL -DDASE_UHD770_FP32_DEFAULT -O3 -std=c++17 ^
  src\cpp\uhd770_device_probe.cpp ^
  -o "%BIN_DIR%\uhd770_device_probe.exe"

if %ERRORLEVEL% EQU 0 (
    echo Build Successful. Running probe...
    "%BIN_DIR%\uhd770_device_probe.exe" --out "%OUT_DIR%\report.json"
) else (
    echo Build Failed.
)

popd
endlocal
