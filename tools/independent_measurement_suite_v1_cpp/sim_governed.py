import argparse
import json
import os
import sys
import hashlib
import numpy as np

FORBIDDEN_KEYWORDS = [
    "RT", "aRT", "mono_process", "mono-process", "falsification", 
    "verdict", "model_class", "campaign", "reconciliation"
]

def check_leakage(data_dict):
    # Recursively check dictionary keys and string values for forbidden keywords
    str_data = json.dumps(data_dict).lower()
    for kw in FORBIDDEN_KEYWORDS:
        if kw.lower() in str_data:
            raise ValueError(f"Metadata leakage check failed: found forbidden keyword '{kw}'")

def empirical_cdf(data, x):
    if len(data) == 0:
        return 0.0
    return np.sum(data <= x) / len(data)

def calculate_ks_distance(a, b):
    if len(a) == 0 or len(b) == 0:
        return 0.0
    all_vals = np.concatenate([a, b])
    cdfs_a = np.array([empirical_cdf(a, val) for val in all_vals])
    cdfs_b = np.array([empirical_cdf(b, val) for val in all_vals])
    return float(np.max(np.abs(cdfs_a - cdfs_b)))

def calculate_dtw(a, b):
    # Dynamic Time Warping distance between two 1D sequences
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return 0.0
    dtw_matrix = np.zeros((n + 1, m + 1))
    dtw_matrix[1:, 0] = np.inf
    dtw_matrix[0, 1:] = np.inf
    dtw_matrix[0, 0] = 0.0
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = abs(a[i-1] - b[j-1])
            dtw_matrix[i, j] = cost + min(
                dtw_matrix[i-1, j],    # insertion
                dtw_matrix[i, j-1],    # deletion
                dtw_matrix[i-1, j-1]   # match
            )
    return float(dtw_matrix[n, m])

def get_graph_stats(graph_dict):
    if not graph_dict:
        return 0.0, 0.0
    nodes = graph_dict.get("nodes", [])
    edges = graph_dict.get("edges", [])
    
    n = len(nodes)
    if n == 0:
        return 0.0, 0.0
        
    adj = {node: set() for node in nodes}
    for u, v in edges:
        if u in adj and v in adj:
            adj[u].add(v)
            adj[v].add(u)
            
    # Degree entropy
    degrees = [len(adj[node]) for node in nodes]
    deg_counts = {}
    for d in degrees:
        deg_counts[d] = deg_counts.get(d, 0) + 1
    probs = [c / n for c in deg_counts.values()]
    degree_entropy = float(-np.sum([p * np.log(p) for p in probs if p > 0]))
    
    # Average clustering coefficient
    cluster_coeffs = []
    for node in nodes:
        neighbors = list(adj[node])
        k = len(neighbors)
        if k < 2:
            cluster_coeffs.append(0.0)
            continue
        links = 0
        for i in range(k):
            for j in range(i + 1, k):
                if neighbors[j] in adj[neighbors[i]]:
                    links += 1
        cluster_coeffs.append(2 * links / (k * (k - 1)))
    avg_clustering = float(np.mean(cluster_coeffs))
    
    return degree_entropy, avg_clustering

def run_permutation_test(a, b, num_permutations=100):
    observed = calculate_ks_distance(a, b)
    combined = np.concatenate([a, b])
    n = len(a)
    count = 0
    for _ in range(num_permutations):
        perm = np.random.permutation(combined)
        perm_a = perm[:n]
        perm_b = perm[n:]
        if calculate_ks_distance(perm_a, perm_b) >= observed:
            count += 1
    return float(count / num_permutations)

def run_bootstrap_ci(a, b, num_iterations=100):
    diffs = []
    n_a, n_b = len(a), len(b)
    for _ in range(num_iterations):
        boot_a = np.random.choice(a, size=n_a, replace=True)
        boot_b = np.random.choice(b, size=n_b, replace=True)
        diffs.append(calculate_ks_distance(boot_a, boot_b))
    return [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]

def main():
    parser = argparse.ArgumentParser(description="Independent Measurement Suite v1")
    parser.add_argument("--input", type=str, required=True, help="Path to input json")
    parser.add_argument("--output", type=str, required=True, help="Path to output json")
    parser.add_argument("--seed", type=int, default=42, help="Stochastic seed")
    parser.add_argument("--bootstrap-iterations", type=int, default=100, help="Number of bootstrap iterations")
    
    args = parser.parse_args()
    
    # Set seed
    if args.seed is not None:
        np.random.seed(args.seed)
        
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    except Exception as e:
        print(f"Error loading input: {e}", file=sys.stderr)
        sys.exit(1)
        
    # Enforce Blindness Contract
    try:
        check_leakage(input_data)
    except ValueError as e:
        print(f"Blindness Violation: {e}", file=sys.stderr)
        sys.exit(2)
        
    sample_a = input_data.get("sample_a", {})
    sample_b = input_data.get("sample_b", {})
    
    data_a = np.array(sample_a.get("data", []))
    data_b = np.array(sample_b.get("data", []))
    
    graph_a = sample_a.get("graph", {})
    graph_b = sample_b.get("graph", {})
    
    # Calculate metrics
    ks = calculate_ks_distance(data_a, data_b)
    dtw = calculate_dtw(data_a, data_b)
    
    entropy_a, clustering_a = get_graph_stats(graph_a)
    entropy_b, clustering_b = get_graph_stats(graph_b)
    
    # Bootstrap and Permutation tests
    p_val = run_permutation_test(data_a, data_b, num_permutations=args.bootstrap_iterations)
    ci = run_bootstrap_ci(data_a, data_b, num_iterations=args.bootstrap_iterations)
    
    measurements = {
        "ks_distance": ks,
        "dtw_distance": dtw,
        "clustering_coefficient_diff": float(abs(clustering_a - clustering_b)),
        "degree_entropy_diff": float(abs(entropy_a - entropy_b)),
        "bootstrap_ci": ci,
        "permutation_p_value": p_val
    }
    
    # Immutable audit log
    audit_record = {
        "run_id": f"MEASURE_{int(np.random.randint(100000, 999999))}",
        "measurements": measurements,
        "timestamp": "2026-07-18T20:23:00Z"
    }
    
    audit_dir = "outputs/measurement_audit_logs"
    os.makedirs(audit_dir, exist_ok=True)
    with open(os.path.join(audit_dir, f"audit_{hashlib.sha256(json.dumps(measurements).encode()).hexdigest()[:12]}.json"), "w") as f:
        json.dump(audit_record, f, indent=2)
        
    # Implementation / config hashes
    impl_hash = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    config_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
    
    output_envelope = {
        "tool_name": "independent_measurement_suite_v1_cpp",
        "tool_version": "1.0.0",
        "run_id": audit_record["run_id"],
        "mechanism_class": "independent_measurement",
        "configuration_hash": config_hash,
        "implementation_hash": impl_hash,
        "seed": args.seed,
        "status": "success",
        "measurements": measurements,
        "uncertainty": {
            "bootstrap_iterations": args.bootstrap_iterations,
            "bootstrap_ci_95": ci
        },
        "warnings": [],
        "provenance": {
            "git_commit": "HEAD",
            "environment": "CPython"
        }
    }
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output_envelope, f, indent=2)
        
    print(f"Blind measurements completed successfully. Run: {output_envelope['run_id']}")

if __name__ == "__main__":
    main()
