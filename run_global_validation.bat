@echo off
REM Acellorator Global Validation Batch
REM Runs the Tier 1 Structural CI Harness

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%
set PYTHONPATH=%PROJECT_ROOT%

echo [GLOBAL VALIDATION] Initializing structural audit...
set SETVARS="C:\Program Files (x86)\Intel\oneAPI\setvars.bat"
if exist %SETVARS% (
    echo [INFO] Loading Intel oneAPI environment...
    call %SETVARS% >nul 2>&1
)
python %PROJECT_ROOT%\scripts\global_validate.py --root %PROJECT_ROOT%

if %errorlevel% neq 0 (
    echo [ERROR] Global validation failed.
    echo [ACTION] Consult docs/governance/GLOBAL_VALIDATION_ROUTINE.md for remediation steps.
    exit /b 1
)

echo [SUCCESS] Global ecosystem health is verified.
exit /b 0
