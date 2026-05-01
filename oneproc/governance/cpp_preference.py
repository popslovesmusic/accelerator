from typing import List, Dict, Any, Optional
from oneproc.utils.trace_capture import TraceCapture

class CppPreferenceValidator:
    def __init__(self, tracer: Optional[TraceCapture] = None):
        self.tracer = tracer

    def validate(self, tools_used: List[Dict[str, Any]], target_level: str) -> Dict[str, Any]:
        """
        Rule: For C4+ claims, prefer C++ when available.
        python_allowed_if: no C++ equivalent exists, exploratory run, explicit justification logged.
        """
        is_high_rigor = target_level in ["C4", "C5", "C6"]
        violations = []
        
        if not is_high_rigor:
            return {"pass": True, "violations": []}

        for tool in tools_used:
            lang = tool.get("implementation_language", "unknown")
            cpp_available = tool.get("cpp_equivalent_available", False)
            justification = tool.get("justification", None)
            
            if lang == "python" and cpp_available and not justification:
                violations.append({
                    "tool": tool.get("tool_name"),
                    "reason": "Python tool used while C++ equivalent exists without justification."
                })

        success = len(violations) == 0
        if self.tracer:
            self.tracer.capture("cpp_preference_validator", "validate", "success" if success else "failed", {
                "target_level": target_level,
                "violations": violations
            })
        
        return {"pass": success, "violations": violations}
