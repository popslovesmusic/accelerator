import re
from typing import List, Dict, Any, Optional
from oneproc.utils.trace_capture import TraceCapture

class TemplateValidator:
    def __init__(self, tracer: Optional[TraceCapture] = None):
        self.tracer = tracer
        self.required_sections = [
            "Abstract", "Theoretical Mapping", "Experimental Setup", 
            "Observables", "Results", "Cross-Model Comparison", 
            "Falsification", "Artifact Analysis", "Classification", "Conclusion"
        ]

    def validate(self, paper_content: str) -> Dict[str, Any]:
        """Hardened Template Gate V2."""
        missing_sections = []
        invalid_sections = []
        
        # Split by headers
        sections = re.split(r"^#+\s+", paper_content, flags=re.MULTILINE)
        section_map = {}
        for s in sections:
            if not s.strip():
                continue
            lines = s.split("\n", 1)
            header = lines[0].strip().lower()
            body = lines[1].strip() if len(lines) > 1 else ""
            section_map[header] = body

        for section in self.required_sections:
            body_text = section_map.get(section.lower())
            if body_text is None:
                missing_sections.append(section)
                continue
            
            if not body_text:
                invalid_sections.append(f"{section} (empty body)")
                continue
            
            if "TODO" in body_text or "FIXME" in body_text or "[insert" in body_text.lower():
                invalid_sections.append(f"{section} (contains placeholders)")

        # Mandatory conclusion prefix
        conclusion_body = section_map.get("conclusion")
        if conclusion_body:
            if not conclusion_body.startswith("Within these models"):
                invalid_sections.append("Conclusion (does not start with 'Within these models')")

        success = not missing_sections and not invalid_sections
        details = {
            "missing_sections": missing_sections,
            "invalid_sections": invalid_sections
        }
        
        if self.tracer:
            self.tracer.capture("template_validator", "validate", "success" if success else "failed", details)
            
        return {"pass": success, "details": details}
