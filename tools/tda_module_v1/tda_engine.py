import numpy as np
from scipy.ndimage import label
import networkx as nx

def compute_spatial_topology(grid, threshold=0.5):
    """
    Identifies connected components in a 2D grid above a threshold.
    """
    binary_mask = (grid > threshold).astype(int)
    
    # Label connected components
    # structure parameter defines connectivity (8-neighbor)
    structure = np.ones((3, 3), dtype=int)
    labeled_array, num_features = label(binary_mask, structure=structure)
    
    if num_features == 0:
        return {
            "count": 0,
            "max_size": 0,
            "mean_size": 0,
            "active_fraction": 0.0
        }
    
    # Calculate sizes
    # component 0 is background
    component_sizes = np.bincount(labeled_array.ravel())[1:]
    
    return {
        "count": int(num_features),
        "max_size": int(np.max(component_sizes)),
        "mean_size": float(np.mean(component_sizes)),
        "active_fraction": float(np.mean(binary_mask))
    }

def compute_network_topology(adj_matrix):
    """
    Identifies connected components in a graph.
    """
    G = nx.from_numpy_array(adj_matrix)
    components = list(nx.connected_components(G))
    num_features = len(components)
    
    if num_features == 0:
        return {
            "count": 0,
            "max_size": 0,
            "mean_size": 0
        }
    
    sizes = [len(c) for c in components]
    
    return {
        "count": int(num_features),
        "max_size": int(np.max(sizes)),
        "mean_size": float(np.mean(sizes))
    }
