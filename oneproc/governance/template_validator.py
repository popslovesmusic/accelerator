import re
from typing import List, Dict, Any, Optional
from oneproc.utils.trace_capture import TraceCapture
from oneproc.governance.governance_loader import GovernanceLoader

class TemplateValidator:
    def __init__(self, tracer: Optional[TraceCapture] = None):
        self.tracer = tracer
        self.loader = GovernanceLoader()
        mandates = self.loader.get_template_mandates()
        self.required_sections = mandates.get("mandatory_sections", [])
        self.mandatory_prefix = mandates.get("mandatory_conclusion_prefix", "Within these models")

    def validate(self, paper_content: str) -> Dict[str, Any]:
        """Data-driven Template Gate."""
        missing_sections = []
        invalid_sections = []
        
        # Split by headers
        sections = re.split(r"^#+\s+", paper_content, flags=re.MULTILINE)
        section_map = {}
        for s in sections:
            if not s.strip():
                continue
            lines = s.split("\n", 1)
            header = re.sub(r'^[0-9\.]+\s+', '', lines[0])
            header = re.sub(r'[:\(\)].*$', '', header).strip().lower()
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
            if not conclusion_body.startswith(self.mandatory_prefix):
                invalid_sections.append(f"Conclusion (does not start with '{self.mandatory_prefix}')")

        success = not missing_sections and not invalid_sections
        details = {
            "missing_sections": missing_sections,
            "invalid_sections": invalid_sections
        }
        
        if self.tracer:
            self.tracer.capture("template_validator", "validate", "success" if success else "failed", details)
            
        return {"pass": success, "details": details}
