import numpy as np
import os
import sys

# Ensure we can load dase_engine
engine_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "Simulation_engines_extracted_2026-04-25"))
if sys.platform == "win32" and os.path.exists(engine_root):
    os.add_dll_directory(engine_root)

try:
    import dase_engine
except ImportError:
    print("❌ Error: dase_engine.pyd not found. Please compile first.")
    sys.exit(1)

def run_drag_race():
    print("🏎️  Initializing SignalScope DRAG RACE Benchmark...")
    print("   Target: High-intensity node processing burst (10,000 iterations/node)")
    
    # Standard Drag Race Config: 1024 nodes (standard grid)
    num_nodes = 1024
    engine = dase_engine.AnalogCellularEngineAVX2(num_nodes)
    
    print(f"   Hardware: AVX2 Accelerated, OpenMP Parallelized")
    print(f"   Node Count: {num_nodes}")
    
    # Run Drag Race
    # This calls the internal C++ loop that bypasses all Python logic
    avg_time_ms = engine.run_drag_race_benchmark(5)
    
    # Calculate GFLOPS / metrics
    metrics = engine.get_metrics()
    
    print("\n🏁 FINAL DRAG RACE RESULTS 🏁")
    print("================================")
    print(f"Average Burst Time:  {avg_time_ms:.2f} ms")
    print(f"Peak Throughput:     {metrics.throughput_gflops:.2f} GFLOPS")
    print(f"Ops per Second:      {metrics.current_ops_per_second / 1e6:.2f} Million")
    print(f"Speedup vs Scalar:   {metrics.speedup_factor:.2f}x")
    print("================================")
    
    if metrics.throughput_gflops > 50.0:
        print("🏆 ELITE PERFORMANCE ACHIEVED!")
    elif metrics.throughput_gflops > 20.0:
        print("✅ Production Performance Verified.")
    else:
        print("⚠️  Performance below peak. Check thermal throttling.")

if __name__ == "__main__":
    run_drag_race()
