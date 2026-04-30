import numpy as np
import zlib
from scipy.stats import entropy

def compute_entropy(data, bins=50):
    """
    Computes Shannon entropy of the data after binning.
    """
    if len(data) == 0:
        return 0.0
    
    # Histogram to get probabilities
    counts, _ = np.histogram(data, bins=bins, density=True)
    # Filter zeros to avoid log issues
    probs = counts[counts > 0]
    return entropy(probs)

def compute_complexity(data):
    """
    Computes a complexity score using zlib compression ratio.
    """
    if len(data) == 0:
        return 0.0
    
    # Convert to bytes
    byte_data = data.tobytes()
    original_size = len(byte_data)
    compressed_size = len(zlib.compress(byte_data))
    
    return compressed_size / original_size

def compute_mutual_information(data, bins=50):
    """
    Computes Mutual Information between the first and second half of the data
    (or can be adapted for spatial MI).
    """
    n = len(data)
    if n < 2:
        return 0.0
    
    mid = n // 2
    x = data[:mid]
    y = data[mid:2*mid] # ensure equal length
    
    # Mutual Info I(X;Y) = H(X) + H(Y) - H(X,Y)
    h_x = compute_entropy(x, bins=bins)
    h_y = compute_entropy(y, bins=bins)
    
    # Joint entropy H(X,Y)
    xy = np.vstack((x, y)).T
    h_xy = compute_joint_entropy(x, y, bins=bins)
    
    return max(0.0, h_x + h_y - h_xy)

def compute_joint_entropy(x, y, bins=50):
    if len(x) != len(y):
        return 0.0
    
    # 2D histogram for joint distribution
    joint_counts, _, _ = np.histogram2d(x, y, bins=bins, density=True)
    probs = joint_counts[joint_counts > 0]
    return entropy(probs)
