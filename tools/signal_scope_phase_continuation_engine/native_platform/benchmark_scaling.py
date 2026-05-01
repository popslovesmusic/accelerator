import numpy as np
import time
import matplotlib.pyplot as plt
from tools.signal_scope_phase_continuation_engine.native_platform.run_native_platform import run_platform

def benchmark_scaling():
    print("📊 Starting SignalScope Scaling Benchmark...")
    
    n_values = [10, 100, 500, 1000]
    steps_per_frame = [10, 20, 50, 100]
    num_frames = 100
    
    results = {}
    
    # 1. Scaling with N (Nodes)
    print("\n--- Scaling with N (Nodes) ---")
    results['N'] = []
    for n in n_values:
        start = time.time()
        run_platform(
            num_frames=num_frames,
            num_nodes=n,
            engine_steps_per_frame=20,
            run_id=f"bench_N_{n}",
            ablation_cfg={"use_integrated_cpp": True}
        )
        duration = time.time() - start
        results['N'].append(duration)
        print(f"N={n:4d} | Time: {duration:.4f}s")
        
    # 2. Scaling with Internal Steps
    print("\n--- Scaling with Internal Steps ---")
    results['steps'] = []
    for s in steps_per_frame:
        start = time.time()
        run_platform(
            num_frames=num_frames,
            num_nodes=100,
            engine_steps_per_frame=s,
            run_id=f"bench_steps_{s}",
            ablation_cfg={"use_integrated_cpp": True}
        )
        duration = time.time() - start
        results['steps'].append(duration)
        print(f"Steps={s:3d} | Time: {duration:.4f}s")

    print("\n✅ Benchmark Complete.")

if __name__ == "__main__":
    benchmark_scaling()
