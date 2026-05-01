from typing import List, Dict, Any, Optional
from oneproc.utils.trace_capture import TraceCapture

class FalsificationValidator:
    def __init__(self, tracer: Optional[TraceCapture] = None):
        self.tracer = tracer
        self.required_vectors = ["FV-1", "FV-2", "FV-3", "FV-4"]

    def validate(self, falsification_data: List[Dict[str, Any]], target_level: str, strict: bool = False) -> Dict[str, Any]:
        """
        Falsification Gate.
        Required for C4, C5, C6.
        """
        is_high_rigor = target_level in ["C4", "C5", "C6"]
        if not is_high_rigor:
            return {"pass": True, "details": {"reason": "Not required for this level."}}

        vectors_present = []
        reasons = []
        
        for f in falsification_data:
            vector_name = f.get("vector_name")
            if vector_name in self.required_vectors:
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

        vectors_missing = [v for v in self.required_vectors if v not in vectors_present]
        
        success = True
        if strict and vectors_missing:
            success = False
            reasons.append(f"Strict mode: Missing required falsification vectors: {', '.join(vectors_missing)}")
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
