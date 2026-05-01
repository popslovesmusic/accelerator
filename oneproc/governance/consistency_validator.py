import re
from typing import List, Dict, Any, Optional
from oneproc.utils.trace_capture import TraceCapture

class ConsistencyValidator:
    def __init__(self, tracer: Optional[TraceCapture] = None):
        self.tracer = tracer

    def validate(self, paper_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Metadata-Body Consistency Gate."""
        mismatches = []

        # 1. Independent measurement count
        meta_m_count = metadata.get("independent_measurement_count", 0)
        # Count measurement entries in body (approximate)
        body_m_count = len(re.findall(r"^#+\s+Measurement", paper_content, re.MULTILINE | re.IGNORECASE))
        if meta_m_count != body_m_count:
            mismatches.append(f"Measurement count mismatch: metadata={meta_m_count}, body={body_m_count}")

        # 2. Models used
        meta_models = set(metadata.get("models_used", []))
        # Find model names in Experimental Setup or Results (approximate)
        body_models = set(re.findall(r"Tool:\s*(\w+)", paper_content))
        missing_models = meta_models - body_models
        if missing_models:
            mismatches.append(f"Models listed in metadata but missing from body: {', '.join(missing_models)}")

        # 3. Falsification
        meta_fals_run = metadata.get("falsification_run", False)
        has_fals_section = bool(re.search(r"^#+\s+Falsification", paper_content, re.MULTILINE | re.IGNORECASE))
        if meta_fals_run and not has_fals_section:
            mismatches.append("Metadata declares falsification run but section is missing in body.")

        success = len(mismatches) == 0
        details = {"mismatches": mismatches}

        if self.tracer:
            self.tracer.capture("consistency_validator", "validate", "success" if success else "failed", details)

        return {"pass": success, "details": details}
