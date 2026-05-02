from typing import List, Dict, Any, Optional
from oneproc.utils.trace_capture import TraceCapture
from oneproc.governance.governance_loader import GovernanceLoader

class MeasurementValidator:
    def __init__(self, tracer: Optional[TraceCapture] = None):
        self.tracer = tracer
        self.loader = GovernanceLoader()

    def validate(self, paper_content: str, measurement_data: List[Dict[str, Any]], target_level: str) -> Dict[str, Any]:
        """Data-driven Measurement Gate."""
        mandate = self.loader.get_mandate(target_level)
        min_required = mandate.get("min_independent_measurements", 0)
        
        if min_required == 0:
            return {"pass": True, "details": {"reason": "No measurements required for this level."}}

        valid_measurements = []
        reasons = []

        import re
        has_section = re.search(r"^#+\s+Measurement", paper_content, re.MULTILINE | re.IGNORECASE)
        if not has_section:
            reasons.append("Measurement section missing from paper body.")

        for m in measurement_data:
            m_reasons = []
            required_fields = ["tool", "measurement_class", "input_sources", "observables_measured", "result_summary"]
            for field in required_fields:
                if not m.get(field):
                    m_reasons.append(f"Missing field: {field}")
            
            if not m.get("quantitative_or_structural_result_present", False):
                m_reasons.append("Quantitative or structural results not declared.")
            
            if not m.get("measurement_artifact_path"):
                m_reasons.append("Measurement artifact path not recorded.")

            if not m_reasons:
                valid_measurements.append(m)
            else:
                reasons.append(f"Invalid measurement entry ({m.get('tool', 'unknown')}): {', '.join(m_reasons)}")

        success = len(valid_measurements) >= min_required and bool(has_section)
        
        details = {
            "target_level": target_level,
            "required": min_required,
            "found": len(valid_measurements),
            "measurement_section_present": bool(has_section),
            "valid_measurements": valid_measurements,
            "reasons": reasons
        }
        
        if self.tracer:
            self.tracer.capture("measurement_validator", "validate", "success" if success else "failed", details)
            
        return {"pass": success, "details": details}
