from typing import List, Dict, Any, Optional
from oneproc.utils.trace_capture import TraceCapture
from oneproc.governance.governance_loader import GovernanceLoader

class FalsificationValidator:
    def __init__(self, tracer: Optional[TraceCapture] = None):
        self.tracer = tracer
        self.loader = GovernanceLoader()

    def validate(self, falsification_data: List[Dict[str, Any]], target_level: str, strict: bool = False) -> Dict[str, Any]:
        """Data-driven Falsification Gate."""
        mandate = self.loader.get_mandate(target_level)
        required_vectors = mandate.get("required_falsification_vectors", [])
        
        if not required_vectors:
            return {"pass": True, "details": {"reason": "Not required for this level."}}

        vectors_present = []
        reasons = []
        
        for f in falsification_data:
            vector_name = f.get("vector_name")
            if vector_name in required_vectors:
                # Validate vector fields
                required_fields = [
                    "adversarial_condition", "expected_failure_behavior",
                    "observed_behavior", "result"
                ]
                missing_fields = [field for field in required_fields if not f.get(field)]
                if not missing_fields:
                    vectors_present.append(vector_name)
                else:
                    reasons.append(f"Vector {vector_name} missing fields: {', '.join(missing_fields)}")

        vectors_missing = [v for v in required_vectors if v not in vectors_present]
        
        success = True
        if strict and vectors_missing:
            success = False
            reasons.append(f"Strict mode: Missing required falsification vectors from Charter: {', '.join(vectors_missing)}")
        elif not vectors_present:
            success = False
            reasons.append("No valid falsification vectors found.")

        details = {
            "vectors_present": vectors_present,
            "vectors_missing": vectors_missing,
            "reasons": reasons
        }

        if self.tracer:
            self.tracer.capture("falsification_validator", "validate", "success" if success else "failed", details)

        return {"pass": success, "details": details}
