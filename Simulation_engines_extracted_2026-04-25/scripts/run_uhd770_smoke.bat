@echo off
setlocal
pushd "%~dp0.."

call "C:\Program Files (x86)\Intel\oneAPI\setvars.bat"

set OUT_DIR=outputs\uhd770\cli_smoke
if not exist "%OUT_DIR%" mkdir "%OUT_DIR%"

set CLI=build_uhd770\dase_cli_json.exe
if not exist "%CLI%" set CLI=bin\uhd770\dase_cli_json_uhd770.exe

if not exist "%CLI%" (
    echo No UHD 770 CLI binary found. Build with CMake or scripts\build_uhd770_cli.bat first.
    popd
    exit /b 1
)

(
echo {"command":"get_acceleration_status","params":{"run_probe":true}}
echo {"command":"create_engine","params":{"engine_type":"phase4b","num_nodes":2048}}
echo {"command":"run_mission","params":{"engine_id":"engine_001","num_steps":64,"iterations_per_node":8,"backend":"uhd770","drift_check":true}}
echo {"command":"get_metrics","params":{"engine_id":"engine_001"}}
) > "%OUT_DIR%\commands.jsonl"

"%CLI%" < "%OUT_DIR%\commands.jsonl" > "%OUT_DIR%\responses.jsonl"

echo Smoke responses written to %OUT_DIR%\responses.jsonl

popd
endlocal
