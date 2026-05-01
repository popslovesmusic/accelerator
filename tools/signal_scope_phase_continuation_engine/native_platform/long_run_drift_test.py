import numpy as np
import json
from tools.signal_scope_phase_continuation_engine.native_platform.run_native_platform import run_platform

def test_long_run_drift():
    print("⏳ Starting Long-Run Drift Test (Numerical Stability)...")
    
    num_frames = 5000 # Long mission
    num_nodes = 100
    engine_steps = 20
    
    # Run integrated mission
    res = run_platform(
        num_frames=num_frames,
        num_nodes=num_nodes,
        engine_steps_per_frame=engine_steps,
        run_id="drift_test_long",
        ablation_cfg={"use_integrated_cpp": True}
    )
    
    # Analyze phase vector norms over time
    norms = []
    with open(res['feedback_trace_path'], 'r') as f:
        for line in f:
            entry = json.loads(line)
            phi = np.array(entry['phi_current'])
            norms.append(np.linalg.norm(phi))
            
    norms = np.array(norms)
    drift = np.abs(norms - 1.0)
    max_drift = np.max(drift)
    avg_drift = np.mean(drift)
    
    print(f"\nPhase Vector Normalization Drift (after {num_frames} frames):")
    print(f"Max Deviation from 1.0: {max_drift:.2e}")
    print(f"Avg Deviation from 1.0: {avg_drift:.2e}")
    
    # C4 Criteria: Drift should not accumulate significantly
    if max_drift < 1e-4:
        print("\n✅ Numerical Stability Verified (Drift within bounds).")
    else:
        print("\n❌ Numerical Stability FAILED (Significant drift detected).")

if __name__ == "__main__":
    test_long_run_drift()
