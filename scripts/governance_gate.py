import json
import os
import re
import uuid
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# --- Trace Capture Logic ---

class TraceEntry:
    def __init__(self, component: str, action: str, status: str, details: Dict[str, Any] = None):
        self.timestamp = datetime.utcnow().isoformat()
        self.component = component
        self.action = action
        self.status = status
        self.details = details or {}

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "component": self.component,
            "action": self.action,
            "status": self.status,
            "details": self.details
        }

class TraceLog:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.start_time = datetime.utcnow().isoformat()
        self.entries: List[TraceEntry] = []

    def add_entry(self, component: str, action: str, status: str, details: Dict[str, Any] = None):
        entry = TraceEntry(component, action, status, details)
        self.entries.append(entry)

    call_to_dict = lambda self: {
        "run_id": self.run_id,
        "start_time": self.start_time,
        "entries": [e.to_dict() for e in self.entries]
    }

class TraceCapture:
    def __init__(self, run_id: str, output_dir: str):
        self.run_id = run_id
        self.output_dir = output_dir
        self.log = TraceLog(run_id)
        os.makedirs(output_dir, exist_ok=True)
        self.file_path = os.path.join(output_dir, f"trace_{run_id}.json")

    def capture(self, component: str, action: str, status: str, details: Dict[str, Any] = None):
        self.log.add_entry(component, action, status, details)
        self.save()

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.log.call_to_dict(), f, indent=2)

# --- Validators ---

class LexiconValidator:
    def __init__(self, registry_dir: str = "registry", tracer: Optional[TraceCapture] = None):
        self.registry_dir = registry_dir
        self.tracer = tracer
        self.canonical_path = os.path.join(registry_dir, "lexicon_canonical.json")
        self.alias_map_path = os.path.join(registry_dir, "lexicon_alias_map.json")
        self.lexicon = self._load_json(self.canonical_path)
        self.aliases = self._load_json(self.alias_map_path)

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def lexicon_in_check(self, terms: List[str]) -> Dict[str, Any]:
        results = {"valid": [], "missing": [], "aliases": {}}
        for term in terms:
            if term in self.lexicon:
                results["valid"].append(term)
            elif term in self.aliases:
                results["aliases"][term] = self.aliases[term]
                results["valid"].append(self.aliases[term])
            else:
                results["missing"].append(term)
        return results

class TemplateValidator:
    def __init__(self, mandates: Dict[str, Any], tracer: Optional[TraceCapture] = None):
        self.tracer = tracer
        self.required_sections = mandates.get("mandatory_sections", [])
        self.mandatory_prefix = mandates.get("mandatory_conclusion_prefix", "Within these models")

    def validate(self, paper_content: str) -> Dict[str, Any]:
        missing_sections = []
        invalid_sections = []
        sections = re.split(r"^#+\s+", paper_content, flags=re.MULTILINE)
        section_map = {}
        for s in sections:
            if not s.strip(): continue
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

        conclusion_body = section_map.get("conclusion")
        if conclusion_body and not conclusion_body.startswith(self.mandatory_prefix):
            invalid_sections.append(f"Conclusion (does not start with '{self.mandatory_prefix}')")

        return {"pass": not missing_sections and not invalid_sections, "details": {"missing_sections": missing_sections, "invalid_sections": invalid_sections}}

class MeasurementValidator:
    def __init__(self, mandates: Dict[str, Any], tracer: Optional[TraceCapture] = None):
        self.tracer = tracer
        self.mandates = mandates

    def validate(self, paper_content: str, measurement_data: List[Dict[str, Any]], target_level: str) -> Dict[str, Any]:
        level_mandate = self.mandates.get("claim_level_mandates", {}).get(target_level, {})
        min_required = level_mandate.get("min_independent_measurements", 0)
        if min_required == 0: return {"pass": True, "details": {}}
        
        has_section = bool(re.search(r"^#+\s+Measurement", paper_content, re.MULTILINE | re.IGNORECASE))
        valid_count = len([m for m in measurement_data if all(m.get(f) for f in ["tool", "measurement_class"])])
        
        success = valid_count >= min_required and has_section
        return {"pass": success, "details": {"found": valid_count, "required": min_required}}

class FalsificationValidator:
    def __init__(self, mandates: Dict[str, Any], tracer: Optional[TraceCapture] = None):
        self.tracer = tracer
        self.mandates = mandates

    def validate(self, falsification_data: List[Dict[str, Any]], target_level: str, strict: bool = False) -> Dict[str, Any]:
        level_mandate = self.mandates.get("claim_level_mandates", {}).get(target_level, {})
        required_vectors = level_mandate.get("required_falsification_vectors", [])
        if not required_vectors: return {"pass": True, "details": {}}

        present = [f.get("vector_name") for f in falsification_data if f.get("vector_name") in required_vectors]
        missing = [v for v in required_vectors if v not in present]
        
        success = (not strict or not missing) and len(present) > 0
        return {"pass": success, "details": {"missing": missing}}

class ConsistencyValidator:
    def validate(self, paper_content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        mismatches = []
        meta_m_count = metadata.get("independent_measurement_count", 0)
        body_m_count = len(re.findall(r"^#+\s+Measurement", paper_content, re.MULTILINE | re.IGNORECASE))
        if meta_m_count != body_m_count:
            mismatches.append(f"Measurement count mismatch: metadata={meta_m_count}, body={body_m_count}")
        return {"pass": len(mismatches) == 0, "details": {"mismatches": mismatches}}

class CppPreferenceValidator:
    def __init__(self, mandates: Dict[str, Any]):
        self.mandates = mandates

    def validate(self, tools: List[Dict[str, Any]], target_level: str) -> Dict[str, Any]:
        if target_level not in ["C4", "C5", "C6"]: return {"pass": True, "violations": []}
        violations = [t.get("tool_name") for t in tools if t.get("implementation_language") == "python" and t.get("cpp_equivalent_available") and not t.get("justification")]
        return {"pass": len(violations) == 0, "violations": violations}

# --- Main Gate ---

class GovernanceGate:
    def __init__(self, tracer: TraceCapture):
        self.tracer = tracer
        with open("registry/compliance_charter_v2_3.json", "r", encoding="utf-8") as f:
            self.charter = json.load(f).get("governance_enforcement_v2", {})
        self.lexicon_v = LexiconValidator(tracer=tracer)
        self.template_v = TemplateValidator(self.charter, tracer=tracer)
        self.measure_v = MeasurementValidator(self.charter, tracer=tracer)
        self.falsification_v = FalsificationValidator(self.charter, tracer=tracer)
        self.consistency_v = ConsistencyValidator()
        self.cpp_v = CppPreferenceValidator(self.charter)

    def process(self, paper_path: str, target_level: str = "C4", intent: str = "validate", strict: bool = False):
        with open(paper_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        metadata = {}
        meta_match = re.search(r"```json\n(.*?)\n```", content, re.DOTALL)
        if meta_match: metadata = json.loads(meta_match.group(1))

        measurements = []
        for m_match in re.finditer(r"^#+\s+Measurement\b(.*?)(?=\n#+|$)", content, re.MULTILINE | re.IGNORECASE | re.DOTALL):
            m_body = m_match.group(1)
            tool = re.search(r"Tool:\s*`?([\w\-_.]+)`?", m_body)
            cls = re.search(r"Class:\s*`?([\w\-_.]+)`?", m_body)
            measurements.append({"tool": tool.group(1) if tool else "unknown", "measurement_class": cls.group(1) if cls else "unknown"})

        falsification = [{"vector_name": v} for v in set(re.findall(r"(FV-\d)", content))]
        
        # Tools extraction: include models from metadata and measurements
        tool_names = set(metadata.get("models_used", []))
        for m in measurements: tool_names.add(m["tool"])
        
        tools = []
        for tn in tool_names:
            if tn == "unknown": continue
            tools.append({
                "tool_name": tn,
                "implementation_language": "cpp" if "cpp" in tn.lower() else "python",
                "cpp_equivalent_available": True # Assume True for gate logic to trigger check
            })

        results = {
            "template": self.template_v.validate(content),
            "consistency": self.consistency_v.validate(content, metadata),
            "measurement": self.measure_v.validate(content, measurements, target_level),
            "falsification": self.falsification_v.validate(falsification, target_level, strict),
            "cpp": self.cpp_v.validate(tools, target_level)
        }

        final_pass = all(v["pass"] for k, v in results.items() if k != "cpp")
        if not final_pass: gate_result = "block"
        else: gate_result = "pass"

        # Apply intent limits
        intent_limits = self.charter.get("intent_limits", {})
        allowed_max = intent_limits.get(intent, "C2")
        levels = ["C0", "C1", "C2", "C3", "C4", "C5", "C6"]
        final_level = target_level
        if levels.index(target_level) > levels.index(allowed_max):
            final_level = allowed_max
            gate_result = "downgrade"

        output = {
            "gate_result": gate_result,
            "final_level": final_level,
            "checks": results
        }
        self.tracer.capture("governance_gate", "process", gate_result, output)
        return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/governance_gate.py <paper_path> [target_level] [intent] [strict]")
        sys.exit(1)
    
    p_path = sys.argv[1]
    lvl = sys.argv[2] if len(sys.argv) > 2 else "C4"
    intent = sys.argv[3] if len(sys.argv) > 3 else "validate"
    strict = sys.argv[4].lower() == "true" if len(sys.argv) > 4 else False
    
    run_id = str(uuid.uuid4())[:8]
    tracer = TraceCapture(run_id, f"outputs/runs/{run_id}")
    gate = GovernanceGate(tracer)
    res = gate.process(p_path, lvl, intent, strict)
    print(json.dumps(res, indent=2))
