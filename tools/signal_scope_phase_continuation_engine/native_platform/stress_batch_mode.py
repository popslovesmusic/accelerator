import numpy as np
import time
from tools.signal_scope_phase_continuation_engine.native_platform.run_native_platform import run_platform

def stress_batch_mode():
    print("🔥 Starting Batch Mode Stress Test (Monte Carlo Sweep)...")
    
    num_seeds = 10
    num_frames = 1000
    num_nodes = 500
    
    start_total = time.time()
    
    for i in range(num_seeds):
        print(f"🚀 Running Seed {i+1}/{num_seeds}...")
        np.random.seed(i)
        # Generate random signal for this seed
        input_signals = np.random.normal(0, 1.0, num_frames).astype(np.float32)
        
        run_platform(
            num_frames=num_frames,
            num_nodes=num_nodes,
            input_signals=input_signals,
            run_id=f"stress_mc_seed_{i}",
            ablation_cfg={"use_integrated_cpp": True}
        )
        
    duration = time.time() - start_total
    avg_per_seed = duration / num_seeds
    
    print(f"\n✅ Stress Test Complete.")
    print(f"Total Time for {num_seeds} seeds: {duration:.2f}s")
    print(f"Average Time per Seed:         {avg_per_seed:.2f}s")
    print(f"Throughput:                    {num_frames / avg_per_seed:.2f} frames/sec")

if __name__ == "__main__":
    stress_batch_mode()
