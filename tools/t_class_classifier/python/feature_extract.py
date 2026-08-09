from typing import Tuple
from schemas import RealizedClosureTrace

def _normalize_connectivity_edge_indexing(trace: RealizedClosureTrace) -> bool:
    if not trace.connectivity_record or not trace.connectivity_record.edges:
        return False

    V = trace.connectivity_record.num_vertices
    endpoints = [
        node
        for edge in trace.connectivity_record.edges
        if len(edge) >= 2
        for node in edge[:2]
    ]
    if not endpoints or V <= 0:
        return False
    if any(node == 0 for node in endpoints):
        return False
    return all(1 <= node <= V for node in endpoints)

def compute_graph_metrics(trace: RealizedClosureTrace) -> Tuple[int, int, int, int, int, int]:
    # 1. Determine number of vertices V
    V = 0
    adj = trace.closure_adjacency
    if adj and len(adj) > 0:
        V = len(adj)
    elif trace.connectivity_record:
        V = trace.connectivity_record.num_vertices

    # 2. Build adjacency list representation (undirected)
    graph = {i: set() for i in range(V)}
    raw_edge_count = 0
    unique_edge_count = 0
    parallel_edge_count = 0

    # Ingest from closure_adjacency matrix. When present, this is the
    # authoritative graph source; the connectivity record is treated as
    # supporting provenance rather than a second edge source.
    if adj and len(adj) > 0:
        for i in range(len(adj)):
            for j in range(i + 1, len(adj[i])):
                if adj[i][j] != 0:
                    graph[i].add(j)
                    graph[j].add(i)
                    raw_edge_count += 1
                    unique_edge_count += 1
    elif trace.connectivity_record and trace.connectivity_record.edges:
        one_based_edges = _normalize_connectivity_edge_indexing(trace)
        seen_edges = set()
        for edge in trace.connectivity_record.edges:
            if len(edge) >= 2:
                u, v = edge[0], edge[1]
                raw_edge_count += 1
                if one_based_edges:
                    u -= 1
                    v -= 1
                if 0 <= u < V and 0 <= v < V:
                    key = tuple(sorted((u, v)))
                    if key in seen_edges:
                        parallel_edge_count += 1
                    else:
                        seen_edges.add(key)
                        unique_edge_count += 1
                        if u != v:
                            graph[u].add(v)
                            graph[v].add(u)

    # 3. Calculate components count C using DFS
    visited = [False] * V
    C = 0
    
    def dfs(node: int):
        stack = [node]
        while stack:
            curr = stack.pop()
            if not visited[curr]:
                visited[curr] = True
                for neighbor in graph[curr]:
                    if not visited[neighbor]:
                        stack.append(neighbor)

    for i in range(V):
        if not visited[i]:
            dfs(i)
            C += 1

    # 4. Count unique undirected edges E
    E = 0
    for u in graph:
        E += len(graph[u])
    E = E // 2

    # 5. Compute loop count (Betti-1 number)
    if V > 0:
        loop_count = E - V + C
    else:
        loop_count = 0

    return V, E, C, loop_count, raw_edge_count, parallel_edge_count

def estimate_braid_proxy(trace: RealizedClosureTrace, loop_count: int) -> int:
    if loop_count <= 1:
        return 1
    elif loop_count == 2:
        return 2
    else:
        return loop_count
