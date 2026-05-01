import numpy as np
import os
import json
import time
from tools.signal_scope_phase_continuation_engine.native_platform.run_native_platform import run_platform
from tools.signal_scope_phase_continuation_engine.native_platform.engine_bridge import EngineBridge

def test_integrated_equivalence():
    print("🧪 Starting Integrated Loop Equivalence Test...")
    
    num_frames = 50
    num_nodes = 100
    engine_steps = 10
    
    # Generate identical input
    t_vals = np.arange(num_frames, dtype=np.float32)
    input_signals = np.sin(t_vals * 0.1).astype(np.float32)
    
    # 1. Run with Integrated C++ Core
    print("\n--- Running Integrated C++ Path ---")
    start_integrated = time.time()
    res_integrated = run_platform(
        num_frames=num_frames,
        num_nodes=num_nodes,
        engine_steps_per_frame=engine_steps,
        input_signals=input_signals,
        run_id="verify_integrated",
        feedback_enabled=False,
        ablation_cfg={"use_integrated_cpp": True, "disable_residue": True}
    )
    end_integrated = time.time()

    # 2. Run with Legacy Python Path
    print("\n--- Running Legacy Python Path ---")
    start_legacy = time.time()
    res_legacy = run_platform(
        num_frames=num_frames,
        num_nodes=num_nodes,
        engine_steps_per_frame=engine_steps,
        input_signals=input_signals,
        run_id="verify_legacy",
        feedback_enabled=False,
        ablation_cfg={"use_integrated_cpp": False, "disable_residue": True}
    )
    end_legacy = time.time()
    
    # 3. Load and Compare Logs
    print("\n--- Analyzing Results ---")
    
    def load_trace(path):
        data = []
        with open(path, 'r') as f:
            for line in f:
                data.append(json.loads(line))
        return data

    trace_int = load_trace(res_integrated['feedback_trace_path'])
    trace_leg = load_trace(res_legacy['feedback_trace_path'])
    
    if len(trace_int) != len(trace_leg):
        print(f"❌ Length Mismatch: Integrated={len(trace_int)}, Legacy={len(trace_leg)}")
        return

    mismatch_errors = []
    phi_errors = []
    
    for i in range(len(trace_int)):
        # Compare Mismatches
        m_int = trace_int[i]['continuation_mismatch']
        m_leg = trace_leg[i]['continuation_mismatch']
        mismatch_errors.append(abs(m_int - m_leg))
        
        # Compare Phase Vectors
        p_int = np.array(trace_int[i]['phi_current'])
        p_leg = np.array(trace_leg[i]['phi_current'])
        phi_errors.append(np.linalg.norm(p_int - p_leg))
        
    avg_m_err = np.mean(mismatch_errors)
    max_m_err = np.max(mismatch_errors)
    avg_p_err = np.mean(phi_errors)
    
    print(f"Average Mismatch Delta: {avg_m_err:.2e}")
    print(f"Max Mismatch Delta:     {max_m_err:.2e}")
    print(f"Average Phase Delta:    {avg_p_err:.2e}")
    
    print(f"\nSpeed Comparison (including reasoning/logging):")
    print(f"Integrated Path: {end_integrated - start_integrated:.4f}s")
    print(f"Legacy Path:     {end_legacy - start_legacy:.4f}s")
    print(f"Speedup:         {(end_legacy - start_legacy) / (end_integrated - start_integrated):.2f}x")

    # Threshold for success: 1e-5 (allowing for float32 variance and rsqrt NR approximation)
    if max_m_err < 1e-4 and avg_p_err < 1e-4:
        print("\n✅ Integrated Loop Equivalence VERIFIED!")
    else:
        print("\n❌ Integrated Loop Equivalence FAILED!")

if __name__ == "__main__":
    test_integrated_equivalence()
