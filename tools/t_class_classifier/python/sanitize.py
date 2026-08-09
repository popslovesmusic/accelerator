from typing import Dict, Any

FORBIDDEN_FIELDS = ["C_orient", "-(i)", "𝒪", "orientation_regime", "orientation_label", "S_closure"]

def validate_schema_integrity(data: Dict[str, Any]) -> None:
    # Check if essential keys exist
    required = ["continuation_trace", "closure_adjacency", "connectivity_record"]
    for req in required:
        if req not in data:
            raise ValueError(f"Missing required field in trace JSON: '{req}'")

def strip_forbidden_fields(data: Dict[str, Any], action: str = "reject") -> Dict[str, Any]:
    # Check for forbidden fields anywhere in the dictionary keys or nested metadata
    def find_forbidden(d: Any) -> bool:
        if isinstance(d, dict):
            for k, v in d.items():
                if k in FORBIDDEN_FIELDS:
                    return True
                if find_forbidden(v):
                    return True
        elif isinstance(d, list):
            for item in d:
                if find_forbidden(item):
                    return True
        return False

    if find_forbidden(data):
        if action == "reject":
            raise ValueError(f"Forbidden field detected in input trace data: Rejecting execution.")
        elif action == "strip":
            # Recursively strip forbidden fields
            def strip_dict(d: Any) -> Any:
                if isinstance(d, dict):
                    return {k: strip_dict(v) for k, v in d.items() if k not in FORBIDDEN_FIELDS}
                elif isinstance(d, list):
                    return [strip_dict(item) for item in d]
                return d
            return strip_dict(data)
            
    return data
