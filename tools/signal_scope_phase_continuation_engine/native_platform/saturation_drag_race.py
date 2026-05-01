import numpy as np
import os
import sys
import time

# Ensure we can load dase_engine
engine_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Simulation_engines_extracted_2026-04-25"))
if sys.platform == "win32" and os.path.exists(engine_root):
    os.add_dll_directory(engine_root)

try:
    import dase_engine
except ImportError:
    print("❌ Error: dase_engine.pyd not found.")
    sys.exit(1)

def run_saturation_race():
    print("🔥 INITIALIZING SATURATION-CLASS DRAG RACE 🔥")
    print("===========================================")
    
    # Scale to 1 Million Nodes to saturate cache and provide enough parallel work
    # 1,048,576 * 64 bytes = 64 MB (Fits in many L3 caches or fills L2/RAM)
    num_nodes = 1048576 
    num_iterations = 10000 
    num_steps = 100
    
    print(f"🚀 Grid Size:   {num_nodes:,} nodes")
    print(f"🚀 Workload:    {num_iterations:,} iterations per node")
    print(f"🚀 Steps:       {num_steps:,} steps")
    print(f"🚀 Total Ops:   {(num_nodes * num_iterations * num_steps * 12) / 1e9:.2f} Billion FLOPs")
    
    engine = dase_engine.AnalogCellularEngineAVX2(num_nodes)
    
    print("\nStarting SUSTAINED Saturated Run (Monitor Task Manager for 100% CPU)...")
    
    input_signals = np.ones(num_steps, dtype=np.float64) 
    control_patterns = np.ones(num_steps, dtype=np.float64)
    
    start_time = time.time()
    
    # Run the sustained update loop
    engine.run_mission_optimized_phase4c(input_signals, control_patterns, num_steps, num_iterations)
    
    end_time = time.time()
    duration = end_time - start_time
    
    metrics = engine.get_metrics()
    
    print("\n🏁 SATURATION RESULTS 🏁")
    print("===========================================")
    print(f"Total Execution Time: {duration:.4f} s")
    print(f"Effective Throughput: {metrics.throughput_gflops:.2f} GFLOPS")
    print(f"Node Processes/sec:   {metrics.current_ops_per_second / 1e6:.2f} Million")
    print("===========================================")
    
    if metrics.throughput_gflops > 100.0:
        print("💎 GOD-TIER HARDWARE SATURATION REACHED!")
    elif metrics.throughput_gflops > 50.0:
        print("🏆 ELITE THROUGHPUT VERIFIED.")
    else:
        print("⚠️  Scaling limited. Check memory bandwidth or thread count.")

if __name__ == "__main__":
    run_saturation_race()
