import json
from typing import Dict, Any
from schemas import RealizedClosureTrace, ContinuationStep, ConnectivityRecord

def read_trace_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def parse_trace(data: Dict[str, Any]) -> RealizedClosureTrace:
    trace_steps = []
    for step in data.get("continuation_trace", []):
        trace_steps.append(ContinuationStep(
            stage=step["stage"],
            from_node=step["from_node"],
            to_node=step["to_node"]
        ))
    
    conn_rec = data.get("connectivity_record")
    if conn_rec is not None:
        connectivity = ConnectivityRecord(
            num_vertices=conn_rec.get("num_vertices", 0),
            edges=conn_rec.get("edges", [])
        )
    else:
        connectivity = None

    return RealizedClosureTrace(
        fixture_id=data.get("fixture_id"),
        run_id=data.get("run_id"),
        continuation_trace=trace_steps,
        constraint_context_id=data.get("constraint_context_id"),
        closure_adjacency=data.get("closure_adjacency", []),
        connectivity_record=connectivity,
        allowed_metadata=data.get("allowed_metadata", {})
    )
