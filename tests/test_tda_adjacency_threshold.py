import numpy as np
import pytest
from tda_module_v1.tda_engine import compute_network_topology

def test_tiny_noise_does_not_connect_when_thresholded():
    # 3 nodes, nodes 0 and 1 are intentionally connected
    # node 2 has tiny noise connection to 1
    adj = np.array([
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 1e-15],
        [0.0, 1e-15, 0.0]
    ])
    
    # Without threshold, all 3 are connected (1 component)
    res_legacy = compute_network_topology(adj, adjacency_threshold=0.0)
    assert res_legacy["count"] == 1
    
    # With threshold, noise is ignored (2 components: {0,1} and {2})
    res_thresholded = compute_network_topology(adj, adjacency_threshold=1e-12)
    assert res_thresholded["count"] == 2
    assert res_thresholded["max_size"] == 2

def test_intentional_edges_survive_threshold():
    adj = np.array([
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 0.5],
        [0.0, 0.5, 0.0]
    ])
    
    # Threshold 0.1 should preserve all edges
    res = compute_network_topology(adj, adjacency_threshold=0.1)
    assert res["count"] == 1
    assert res["max_size"] == 3

def test_legacy_threshold_zero_preserves_existing_behavior():
    adj = np.array([
        [0.0, 1e-15],
        [1e-15, 0.0]
    ])
    
    # Default behavior (0.0) connects everything nonzero
    res = compute_network_topology(adj)
    assert res["count"] == 1
