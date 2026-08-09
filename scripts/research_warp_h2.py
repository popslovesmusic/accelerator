
import os
import sys
import json
import numpy as np
from pathlib import Path

# Add tool dir to path
tool_dir = Path("tools/signal_scope_phase_continuation_engine").resolve()

def run_collapse_experiment():
    run_id = "warp_collapse_h2"
    out_dir = Path("outputs/runs/h2_collapse_signature")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Add tool dir to path for imports
    sys.path.insert(0, str(tool_dir))
    
    # Generate signal using the tool's synthetic signal generator
    previous_cwd = Path.cwd()
    try:
        os.chdir(tool_dir)
        from native_platform.eeg_synthetic_signals import generate_alpha_tail_removed
        from native_platform.run_native_platform import run_platform
        
        sample_rate = 100
        duration = 2.0  # seconds
        signal = generate_alpha_tail_removed(sample_rate, duration, keep_ratio=0.5)
        
        # Run platform
        summary = run_platform(
            num_frames=len(signal),
            num_nodes=100,
            input_signals=signal,
            run_id=run_id,
            connected=True,
            connected_state="train",
            ablation_cfg={"use_integrated_cpp": False} 
        )
    finally:
        os.chdir(previous_cwd)
    
    # 3. Analyze results
    trace_path = tool_dir / summary["feedback_trace_path"]
    trace_data = []
    with open(trace_path, "r") as f:
        for line in f:
            trace_data.append(json.loads(line))
            
    # Save trace to out_dir
    with open(out_dir / "trace.json", "w") as f:
        json.dump(trace_data, f, indent=2)
        
    # Extract phase error and mismatch
    err = [r["phase_error"] for r in trace_data]
    
    # Identify transition point (t=100)
    pre_burst_err = np.mean(err[50:100])
    burst_err = err[100]
    post_burst_err = np.mean(err[150:200])
    
    print(f"Pre-burst error: {pre_burst_err:.4f}")
    print(f"Burst error: {burst_err:.4f}")
    print(f"Post-burst error: {post_burst_err:.4f}")
    
    results = {
        "pre_burst_err": pre_burst_err,
        "burst_err": burst_err,
        "post_burst_err": post_burst_err,
        "burst_ratio": burst_err / (pre_burst_err + 1e-6),
        "decay_ratio": post_burst_err / (burst_err + 1e-6)
    }
    
    with open(out_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Experiment completed. Results saved to {out_dir}")

if __name__ == "__main__":
    run_collapse_experiment()
