# Recompile and Run Validation for SignalScope Optimization

$ErrorActionPreference = "Stop"

Write-Host "Step 1: Recompiling Engine..."
powershell -NoProfile -ExecutionPolicy Bypass -File "tools/Simulation_engines_extracted_2026-04-25/build_python_bindings.ps1"

Write-Host "Step 2: Running Equivalence Test (Physics Only)..."
# Clear logs
if (Test-Path "tools/signal_scope_phase_continuation_engine/logs") {
    Remove-Item "tools/signal_scope_phase_continuation_engine/logs/*.jsonl" -ErrorAction SilentlyContinue
}

$env:PYTHONPATH = "D:\projects\acellorator\tools\signal_scope_phase_continuation_engine;D:\projects\acellorator\tools\signal_scope_phase_continuation_engine\native_platform;D:\projects\acellorator;$env:PYTHONPATH"
cd tools/signal_scope_phase_continuation_engine
python native_platform/verify_integrated_equivalence.py

Write-Host "Step 3: Running Long-Run Drift Test..."
python native_platform/long_run_drift_test.py

Write-Host "Step 4: Running Scaling Benchmark..."
python native_platform/benchmark_scaling.py

Write-Host "All validation steps attempted."
