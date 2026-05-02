from typing import List, Dict, Any, Optional
from oneproc.utils.trace_capture import TraceCapture
from oneproc.governance.lexicon_validator import LexiconValidator
from oneproc.governance.cpp_preference import CppPreferenceValidator
from oneproc.governance.measurement_validator import MeasurementValidator
from oneproc.governance.template_validator import TemplateValidator
from oneproc.governance.falsification_validator import FalsificationValidator
from oneproc.governance.consistency_validator import ConsistencyValidator
from oneproc.governance.governance_loader import GovernanceLoader

class ClaimGate:
    def __init__(self, tracer: Optional[TraceCapture] = None):
        self.tracer = tracer
        self.loader = GovernanceLoader()
        self.lexicon_v = LexiconValidator(tracer=tracer)
        self.cpp_v = CppPreferenceValidator(tracer=tracer)
        self.measure_v = MeasurementValidator(tracer=tracer)
        self.template_v = TemplateValidator(tracer=tracer)
        self.falsification_v = FalsificationValidator(tracer=tracer)
        self.consistency_v = ConsistencyValidator(tracer=tracer)

    def process_claim(self, claim_data: Dict[str, Any], strict: bool = False, intent: str = "validate") -> Dict[str, Any]:
        """Data-driven Unified Claim Gate."""
        target_level = claim_data.get("requested_level", "C1")
        claim_id = claim_data.get("claim_id", "UNKNOWN")
        paper_content = claim_data.get("paper_content", "")
        
        intent_limits = self.loader.get_intent_limits()
        allowed_max = intent_limits.get(intent, "C2")
        
        results = {
            "claim_id": claim_id,
            "requested_level": target_level,
            "final_level": target_level,
            "gate_result": "pass",
            "checks": {
                "template_pass": True,
                "lexicon_pass": True,
                "measurement_pass": True,
                "cpp_preference_pass": True,
                "falsification_pass": True,
                "consistency_pass": True,
                "language_policy_pass": True
            },
            "downgrades_applied": [],
            "blocked_reasons": [],
            "intent": intent
        }

        levels = ["C0", "C1", "C2", "C3", "C4", "C5", "C6"]
        if levels.index(target_level) > levels.index(allowed_max):
            results["gate_result"] = "downgrade"
            results["final_level"] = allowed_max
            results["downgrades_applied"].append(f"Requested level {target_level} exceeds allowed max for intent '{intent}' ({allowed_max}).")
            target_level = allowed_max

        # 1. Template Check
        t_res = self.template_v.validate(paper_content)
        results["checks"]["template_pass"] = t_res["pass"]
        if not t_res["pass"]:
            results["gate_result"] = "block"
            if t_res["details"]["missing_sections"]:
                results["blocked_reasons"].append(f"Missing sections: {t_res['details']['missing_sections']}")
            if t_res["details"]["invalid_sections"]:
                results["blocked_reasons"].append(f"Invalid sections: {t_res['details']['invalid_sections']}")

        # 2. Consistency Check
        c_res = self.consistency_v.validate(paper_content, claim_data.get("metadata", {}))
        results["checks"]["consistency_pass"] = c_res["pass"]
        if not c_res["pass"]:
            results["gate_result"] = "block"
            results["blocked_reasons"].extend(c_res["details"]["mismatches"])

        # 3. Lexicon Check
        l_res = self.lexicon_v.lexicon_in_check(claim_data.get("lexicon_terms", []))
        if l_res["missing"]:
            results["checks"]["lexicon_pass"] = False
            results["final_level"] = "proposed_interpretation"
            results["downgrades_applied"].append(f"Missing lexicon terms: {l_res['missing']}")

        # 4. Measurement Check
        m_res = self.measure_v.validate(paper_content, claim_data.get("measurements", []), target_level)
        results["checks"]["measurement_pass"] = m_res["pass"]
        if not m_res["pass"] and target_level in ["C4", "C5", "C6"]:
            if results["gate_result"] != "block":
                results["gate_result"] = "downgrade"
            results["final_level"] = "C3"
            results["downgrades_applied"].append("Insufficient independent measurements for requested level.")

        # 5. Falsification Check
        f_res = self.falsification_v.validate(claim_data.get("falsification_data", []), target_level, strict=strict)
        results["checks"]["falsification_pass"] = f_res["pass"]
        if not f_res["pass"] and target_level in ["C4", "C5", "C6"]:
            if results["gate_result"] != "block":
                results["gate_result"] = "block" if strict else "downgrade"
            if not strict:
                results["final_level"] = "C3"
            results["blocked_reasons" if strict else "downgrades_applied"].append("Falsification check failed.")

        # 6. CPP Preference Check
        cpp_res = self.cpp_v.validate(claim_data.get("tools", []), target_level)
        results["checks"]["cpp_preference_pass"] = cpp_res["pass"]
        if not cpp_res["pass"]:
            mandate = self.loader.get_mandate(target_level)
            pref_action = mandate.get("cpp_preference", "warn")
            if pref_action == "block" or strict:
                results["gate_result"] = "block"
                results["blocked_reasons"].append("C++ preference violation.")
            elif pref_action == "downgrade":
                if results["gate_result"] != "block":
                    results["gate_result"] = "downgrade"
                results["final_level"] = "C3"
                results["downgrades_applied"].append("C++ preference violation (downgraded per Charter).")
            else:
                results["downgrades_applied"].append("C++ preference violation detected.")

        if self.tracer:
            self.tracer.capture("claim_gate", "process_claim", results["gate_result"], {
                "claim_id": claim_id,
                "results": results
            })
            
        return results
