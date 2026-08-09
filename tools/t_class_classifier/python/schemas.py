from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ContinuationStep:
    stage: int
    from_node: int
    to_node: int

@dataclass
class ConnectivityRecord:
    num_vertices: int
    edges: List[List[int]]

@dataclass
class RealizedClosureTrace:
    fixture_id: Optional[str] = None
    run_id: Optional[str] = None
    continuation_trace: List[ContinuationStep] = field(default_factory=list)
    constraint_context_id: Optional[str] = None
    closure_adjacency: List[List[int]] = field(default_factory=list)
    connectivity_record: Optional[ConnectivityRecord] = None
    allowed_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TSig:
    C_count: int = 0      # Loop count / Closure count
    L_depth: int = 0      # Nesting depth
    R_conn: float = 0.0   # Connectivity persistence
    B_cross: int = 0      # Crossing/Braid proxy
    component_count: int = 0
    raw_edge_count: int = 0
    unique_edge_count: int = 0
    parallel_edge_count: int = 0

@dataclass
class ClassificationResult:
    t_sig: TSig
    t_class: str          # T_0, T_1, T_2, T_3, T_4, T_x
    is_valid_closure: bool
