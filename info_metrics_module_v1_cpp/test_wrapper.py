import numpy as np
from metrics_cpp_wrapper import MetricsEngineCPP

def test_metrics():
    print("Initializing MetricsEngineCPP...")
    engine = MetricsEngineCPP()
    
    # Test data: normal distribution
    n = 100000
    data = np.random.normal(0, 1, n).astype(np.float32)
    
    print(f"Testing Entropy on {n} samples...")
    h = engine.compute_entropy(data, bins=100, range=(-3, 3))
    print(f"Entropy: {h:.4f} bits")
    
    # Test data: correlated variables
    x = np.random.normal(0, 1, n).astype(np.float32)
    y = x + np.random.normal(0, 0.1, n).astype(np.float32)
    
    print(f"Testing Mutual Information on {n} samples...")
    mi = engine.compute_mutual_information(x, y, bins=100, x_range=(-3, 3), y_range=(-3, 3))
    print(f"Mutual Information: {mi:.4f} bits")

if __name__ == "__main__":
    test_metrics()
