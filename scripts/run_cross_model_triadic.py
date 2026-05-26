import json
import subprocess
import os

def run_triadic():
    config = {"triads": 1024, "steps": 1000, "dt": 0.01, "seed": 42}
    with open("cross_triadic_config.json", 'w') as f: json.dump(config, f)
    subprocess.run(["python", "tools/triadic_closure_substrate_cpp/sim_governed.py", "--config", "cross_triadic_config.json", "--out", "cross_triadic_out"], capture_output=True)
    with open("cross_triadic_out/summary.json", 'r') as f: return json.load(f)

def run_optical():
    # Optical Reservoir baseline
    cmd = ["python", "tools/optical_reservoir/simulate_optical_reservoir.py", "--steps", "1000", "--dt", "0.01", "--triads", "3", "--feedback", "--network-mode", "triad_network"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    # Optical Reservoir outputs JSON to stdout in triad_network mode
    # But wait, earlier I saw it might have UTF-16 BOM or other issues if redirected.
    # Let's try to capture it cleanly.
    return json.loads(res.stdout.strip().lstrip('\ufeff'))

print("Running cross-model comparison...")
triadic = run_triadic()
optical = run_optical()

t_sync = triadic["observables"]["space_app_ordering_metric"]
o_sync = optical["network"]["synchronization_index"]

print("-" * 50)
print(f"Triadic Closure Ordering: {t_sync:.6f}")
print(f"Optical Reservoir Sync:   {o_sync:.6f}")
print("-" * 50)

# Qualitative assessment
if abs(t_sync - o_sync) < 0.5:
    print("VERDICT: Qualitative Alignment Confirmed (Mechanism Independence Supported)")
else:
    print("VERDICT: Divergent behavior observed (Requires further investigation)")
