import json
import os
import re
import uuid
import sys
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# --- Trace Capture Logic ---

class TraceEntry:
    def __init__(self, component: str, action: str, status: str, details: Dict[str, Any] = None):
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
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
        self.start_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
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
        self.validation_registry_path = os.path.join(registry_dir, "lexicon_validation_registry.json")
        self.lexicon = self._load_json(self.canonical_path)
        self.aliases = self._load_json(self.alias_map_path).get("aliases", {})
        self.validation_registry = self._load_json(self.validation_registry_path)

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_json(self, path: str, data: Dict[str, Any]):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    def normalize_term(self, term: str) -> str:
        if not term:
            return ""
        term = term.strip()
        return self.aliases.get(term, self.aliases.get(term.lower(), term.lower()))

    def lexicon_in_check(self, terms: List[str]) -> Dict[str, Any]:
        results = {"valid": [], "missing": [], "aliases": {}}
        for term in terms:
            norm = self.normalize_term(term)
            if norm in self.lexicon:
                results["valid"].append(norm)
            else:
                results["missing"].append(norm or term)
        return results

    def lexicon_validation_check(self, term_roles: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Validate required term-roles against registry/lexicon_validation_registry.json.

        Conservative rule: if role is missing or not found for a term, treat as L0 (unbound),
        which caps claim classification at Proposed Interpretation and blocks Supported/L3.
        """
        reg_terms = self.validation_registry.get("terms", {})
        checked = []
        gaps = []
        below_l2 = []

        for tr in term_roles:
            raw_term = (tr.get("term") or "").strip()
            raw_role = (tr.get("role") or "").strip()
            term = self.normalize_term(raw_term)
            role = raw_role

            entry = {
                "term": term or raw_term,
                "role": role or "",
                "registry_status": "GAP_OPEN",
                "allowed_claim_usage": "proposed_interpretation_only",
            }

            term_entry = reg_terms.get(term)
            if not term_entry:
                gaps.append({"term": term or raw_term, "role": role, "reason": "term_missing_from_validation_registry"})
                checked.append(entry)
                continue

            roles = term_entry.get("roles", {})
            if not role or role not in roles:
                entry["registry_status"] = "L0"
                entry["allowed_claim_usage"] = "proposed_interpretation_only"
                below_l2.append({"term": term, "role": role or "", "status": "L0", "reason": "missing_or_unbound_role"})
                checked.append(entry)
                continue

            role_entry = roles.get(role, {})
            status = role_entry.get("status", "L0")
            entry["registry_status"] = status
            if status in ("L3",):
                entry["allowed_claim_usage"] = "supported_ok_for_this_role"
            elif status in ("L2",):
                entry["allowed_claim_usage"] = "partially_supported_ok"
            else:
                entry["allowed_claim_usage"] = "proposed_interpretation_only"
                below_l2.append({"term": term, "role": role, "status": status})

            checked.append(entry)

        cap = "proposed_interpretation" if (gaps or below_l2) else None
        return {
            "pass": cap is None,
            "details": {
                "cap_classification": cap,
                "terms_checked": checked,
                "gaps": gaps,
                "below_L2": below_l2,
            },
        }

    def record_term_role_evidence(
        self,
        claim_id: str,
        evidence_id: str,
        term_roles: List[Dict[str, str]],
        mechanism_classes: List[str],
        observables: List[str],
        output_paths: List[str],
        downgrade_reasons: List[str],
    ) -> Dict[str, Any]:
        """
        Append evidence pointers for term-roles without auto-promoting L-levels.
        """
        if not claim_id:
            return {"updated": False, "reason": "missing_claim_id"}

        data = self.validation_registry
        data.setdefault("terms", {})
        updated = False

        for tr in term_roles:
            term = self.normalize_term(tr.get("term", ""))
            role = (tr.get("role") or "").strip()
            if not term:
                continue
            if not role:
                role = "unbound_role_in_paper"

            term_entry = data["terms"].setdefault(term, {"roles": {}})
            roles = term_entry.setdefault("roles", {})
            role_entry = roles.setdefault(role, {"status": "L0"})

            if not role_entry.get("claim_id"):
                role_entry["claim_id"] = claim_id
                updated = True
            if not role_entry.get("evidence_id"):
                role_entry["evidence_id"] = evidence_id
                updated = True

            role_entry.setdefault("mechanism_classes", [])
            role_entry.setdefault("observables", [])
            role_entry.setdefault("output_paths", [])
            role_entry.setdefault("downgrade_reasons", [])

            for mc in mechanism_classes or []:
                if mc and mc not in role_entry["mechanism_classes"]:
                    role_entry["mechanism_classes"].append(mc)
                    updated = True
            for ob in observables or []:
                if ob and ob not in role_entry["observables"]:
                    role_entry["observables"].append(ob)
                    updated = True
            for op in output_paths or []:
                if op and op not in role_entry["output_paths"]:
                    role_entry["output_paths"].append(op)
                    updated = True
            for dr in downgrade_reasons or []:
                if dr and dr not in role_entry["downgrade_reasons"]:
                    role_entry["downgrade_reasons"].append(dr)
                    updated = True

        if updated:
            self._save_json(self.validation_registry_path, data)
        return {"updated": updated}

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

    def validate(self, paper_content: str, measurement_data: List[Dict[str, Any]], target_level: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        # New Multi-Seed Invariance Check (MPF_MULTI_SEED_INVARIANCE_HARD_RULE_V1)
        level_mandate = self.mandates.get("claim_level_mandates", {}).get(target_level, {})
        if not level_mandate:
            # Fallback to legacy or default
            level_mandate = self.mandates.get("legacy_claim_level_mandates_backup", {}).get(target_level, {})
        
        min_seeds_required = level_mandate.get("min_seeds", 0)
        seeds_used = metadata.get("seeds_used", 0)
        
        results = {"pass": True, "errors": [], "details": {}}
        
        # 1. Seed Count Enforcement
        if seeds_used < min_seeds_required:
            results["pass"] = False
            results["errors"].append(f"Multi-Seed Invariance Violation: Level {target_level} requires {min_seeds_required} seeds (found {seeds_used}). Claim downgraded to exploratory.")

        # 2. Measurement Count (Legacy Support)
        min_required_m = level_mandate.get("min_independent_measurements", 0)
        valid_count = len([m for m in measurement_data if all(m.get(f) for f in ["tool", "measurement_class"])])
        if min_required_m > 0:
            has_section = bool(re.search(r"^#+\s+Measurement", paper_content, re.MULTILINE | re.IGNORECASE))
            if valid_count < min_required_m or not has_section:
                results["pass"] = False
                results["errors"].append(f"Measurement Rigor: Level {target_level} requires {min_required_m} measurements (found {valid_count}).")

        # 3. Adversarial Protection (Mandatory for C4+)
        level_order = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "L0_exploratory", "L1_structural", "L2_supported", "L3_strong_support", "L4_mechanism_independent", "L5_rigor_endorsed"]
        target_idx = level_order.index(target_level) if target_level in level_order else 0
        c4_idx = level_order.index("C4")
        l2_idx = level_order.index("L2_supported")
        
        if target_idx >= c4_idx or target_idx >= l2_idx:
            outputs = metadata.get("recoverable_outputs", [])
            has_protected = False
            for out_path in outputs:
                shadow_path = Path(out_path) / "artifacts/shadow_report.json"
                if shadow_path.exists():
                    has_protected = True
                    break
            
            if not has_protected:
                results["pass"] = False
                results["errors"].append(f"Adversarial Integrity: Level {target_level} requires adversarial protection (shadow_report.json not found in outputs).")

        results["details"] = {
            "seeds_found": seeds_used,
            "seeds_required": min_seeds_required,
            "measurements_found": valid_count,
            "adversary_protected": has_protected if (target_idx >= c4_idx or target_idx >= l2_idx) else "not_required"
        }
        return results

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

class SemanticProjectionValidator:
    def __init__(self, policy_path: str = "registry/governance/semantic_projection_policy.json"):
        self.policy_path = policy_path
        self.policy = self._load_json(policy_path).get("semantic_projection_governance", {})
        self.protected_terms = self.policy.get("protected_ontology_terms", [])
        self.blocked_identity_phrases = [
            p.lower() for p in self.policy.get("blocked_identity_phrases", [])
        ]
        self.scope_requirements = self.policy.get("classification_scope_requirements", {})

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _find_unmarked_protected_terms(self, text: str) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            lower = line.lower()
            for term in self.protected_terms:
                pattern = r"\b" + re.escape(term) + r"\b"
                if re.search(pattern, lower):
                    violations.append({
                        "term": term,
                        "line": line_no,
                        "excerpt": line.strip()[:240],
                    })
        return violations

    def _find_identity_language(self, text: str) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        lines = text.splitlines()
        regexes = [
            r"\b(gravity|space|time|matter|energy|field|particle|vacuum|cosmos|universe|relativity|quantum)\b\s+(?:is|are|equals|equivalent to)\b",
            r"\b(proves physics|demonstrates reality|is literally)\b",
        ]
        for line_no, line in enumerate(lines, start=1):
            lower = line.lower()
            if any(phrase in lower for phrase in self.blocked_identity_phrases):
                violations.append({
                    "line": line_no,
                    "excerpt": line.strip()[:240],
                    "rule": "blocked_identity_phrase",
                })
                continue
            for pattern in regexes:
                if re.search(pattern, lower):
                    violations.append({
                        "line": line_no,
                        "excerpt": line.strip()[:240],
                        "rule": "identity_shape",
                    })
                    break
        return violations

    def validate(self, paper_content: str, requested_classification: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        unmarked_terms = self._find_unmarked_protected_terms(paper_content)
        identity_violations = self._find_identity_language(paper_content)

        scope_phrase = self.scope_requirements.get((requested_classification or "").lower())
        scope_violation = None
        if scope_phrase and scope_phrase.lower() not in paper_content.lower():
            scope_violation = {
                "required_phrase": scope_phrase,
                "requested_classification": requested_classification,
            }

        return {
            "pass": not unmarked_terms and not identity_violations and scope_violation is None,
            "details": {
                "unmarked_protected_terms": unmarked_terms,
                "identity_violations": identity_violations,
                "scope_violation": scope_violation,
                "policy_path": self.policy_path,
            },
        }

class CppPreferenceValidator:
    def __init__(self, mandates: Dict[str, Any]):
        self.mandates = mandates

    def validate(self, tools: List[Dict[str, Any]], target_level: str) -> Dict[str, Any]:
        if target_level not in ["C4", "C5", "C6"]: return {"pass": True, "violations": []}
        violations = [
            t.get("tool_name") for t in tools 
            if t.get("implementation_language") == "python" 
            and t.get("cpp_equivalent_available") 
            and not t.get("justification")
            and t.get("status") != "FROZEN"
        ]
        return {"pass": len(violations) == 0, "violations": violations}

class MathValidator:
    def __init__(self, mandates: Dict[str, Any] = None, registry_dir: str = "registry"):
        self.registry_path = os.path.join(registry_dir, "math_registry.json")
        self.registry = self._load_json(self.registry_path)
        self.mandates = mandates.get("math_mandates", {}) if mandates else {}

    def _load_json(self, path: str) -> Dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def validate(self, lemma_ids: List[str], target_level: str) -> Dict[str, Any]:
        """
        Ensure lemmas have required validation status and proof type for the target claim level.
        C5/C6 require 'simulated' or 'formally_proven'.
        Heuristic proof type caps level at C2.
        Constructive proof type caps level at C4.
        """
        results = {"pass": True, "errors": [], "details": []}
        if not lemma_ids:
            return results

        # Index the registry for fast lookup (support both item_id and lemma_id)
        lemma_map = {}
        for l in self.registry.get("lemmas", []):
            lid = l.get("lemma_id") or l.get("item_id")
            if lid: lemma_map[lid] = l
            
        proof_map = {}
        for p in self.registry.get("proofs", []):
            pid = p.get("proof_id") or p.get("item_id")
            if pid: proof_map[pid] = p

        level_order = ["C0", "C1", "C2", "C3", "C4", "C5", "C6"]
        target_idx = level_order.index(target_level) if target_level in level_order else 0

        # Get mandates from charter
        proof_limits = self.mandates.get("proof_type_limits", {"heuristic": "C2", "constructive": "C4"})
        status_reqs = self.mandates.get("status_requirements", {"C5": ["simulated", "formally_proven"], "C6": ["simulated", "formally_proven"]})

        for lid in lemma_ids:
            item = lemma_map.get(lid) or proof_map.get(lid)
            if not item:
                results["errors"].append(f"Math Error: referenced ID '{lid}' not found in math_registry.json")
                continue
            
            status = item.get("status", "unverified").lower()
            proof_type = item.get("proof_type", "heuristic").lower()
            
            item_details = {"id": lid, "status": status, "proof_type": proof_type}
            results["details"].append(item_details)

            # Check status vs level (e.g. C5/C6)
            required_statuses = status_reqs.get(target_level)
            if required_statuses and status not in [s.lower() for s in required_statuses]:
                results["pass"] = False
                results["errors"].append(f"Math Error: Level {target_level} requires ID '{lid}' to be one of {required_statuses} (currently '{status}').")

            # Check proof type vs level (Patch Group B1)
            limit_level = proof_limits.get(proof_type)
            if limit_level and target_idx > level_order.index(limit_level):
                results["pass"] = False
                results["errors"].append(f"Math Error: ID '{lid}' has proof type '{proof_type}', which caps claim level at {limit_level} (requested {target_level}).")

        if results["errors"]:
            results["pass"] = False
        return results

# --- Main Gate ---

class GovernanceGate:
    def __init__(self, tracer: TraceCapture):
        self.tracer = tracer
        
        # --- Runtime Governance Check (PCD_RUNTIME_GOVERNANCE_ENGINE_SCAFFOLD_V1) ---
        try:
            import scripts.runtime_governance_check as rgc
            self.runtime_status = rgc.run_checks()
            if self.runtime_status["status"] == "BLOCK":
                 print(f"FATAL: Runtime Governance Block. Details: {json.dumps(self.runtime_status['failures'], indent=2)}")
                 sys.exit(1)
        except ImportError:
            self.runtime_status = {"status": "MISSING", "failures": [{"error": "runtime_governance_check.py not found"}]}
        
        # --- Empirical Governance Check (PCD_EMPIRICAL_GOVERNANCE_RUNTIME_INTEGRATION_V1) ---
        try:
            import scripts.check_empirical_governance as ceg
            # Note: This would pass the paper path or claim ID in process()
            self.empirical_governance_status = {"status": "ACTIVE", "script": "scripts/check_empirical_governance.py"}
        except ImportError:
            self.empirical_governance_status = {"status": "MISSING", "error": "check_empirical_governance.py not found"}
        
        with open("registry/compliance_charter_v2_3.json", "r", encoding="utf-8") as f:
            self.charter = json.load(f).get("governance_enforcement_v2", {})
        self.lexicon_v = LexiconValidator(tracer=tracer)
        self.template_v = TemplateValidator(self.charter, tracer=tracer)
        self.measure_v = MeasurementValidator(self.charter, tracer=tracer)
        self.falsification_v = FalsificationValidator(self.charter, tracer=tracer)
        self.consistency_v = ConsistencyValidator()
        self.semantic_projection_v = SemanticProjectionValidator()
        self.cpp_v = CppPreferenceValidator(self.charter)
        self.math_v = MathValidator(self.charter)

    def _write_json(self, path: str, data: Dict[str, Any]):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    def _load_json(self, path: str) -> Any:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _extract_json_blocks(self, text: str) -> List[Dict[str, Any]]:
        blocks: List[Dict[str, Any]] = []
        # Extremely robust extraction
        for m in re.finditer(r"```json(.*?)```", text, re.DOTALL | re.IGNORECASE):
            raw = m.group(1).strip()
            try:
                parsed = json.loads(raw)
            except Exception:
                continue
            if isinstance(parsed, dict):
                blocks.append(parsed)
        return blocks

    def _detect_narrative_terms_from_paper(self, content: str) -> List[str]:
        """
        Pull candidate narrative terms from the Classification section text, if present.
        Example line: '(Misalignment Threshold, Forced Lock, No Ringdown Technosignature)'
        """
        candidates: List[str] = []
        m = re.search(r"downgraded\s+from.*?\(([^)]+)\)", content, re.IGNORECASE | re.DOTALL)
        if not m:
            return candidates
        raw = m.group(1)
        for part in raw.split(","):
            t = part.strip().strip("`\"'")
            if t:
                candidates.append(t)
        return candidates

    def _compute_evidence_level(self, model_classes: List[str], seeds_used: int, falsification_vectors: List[str]) -> str:
        if not model_classes or seeds_used <= 0:
            return "L0"
        if len(set(model_classes)) >= 2 and seeds_used >= 3 and {"FV-1", "FV-2"}.issubset(set(falsification_vectors or [])):
            return "L2"
        return "L1"

    def _update_unified_manifest(self, claim_id: str, paper_path: str, metadata: Dict[str, Any], gate_result: str, final_level: str, tools_used: List[str]):
        manifest_path = "registry/governance_manifest.json"
        if not os.path.exists(manifest_path):
            return {"updated": False, "reason": "manifest_not_found"}

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            nodes = manifest.get("nodes", {})
            edges = manifest.get("edges", [])

            # 1. Update/Add Claim Node
            nodes[claim_id] = {
                "type": "claim",
                "status": final_level,
                "data": {
                    "paper_path": paper_path,
                    "gate_result": gate_result,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
            }

            # 2. Add Run Node (if available)
            run_id = metadata.get("run_id") or os.path.basename(os.path.dirname(paper_path))
            nodes[run_id] = {
                "type": "run",
                "status": "complete",
                "data": {
                    "path": os.path.dirname(paper_path),
                    "tools": tools_used
                }
            }

            # 3. Add Edges
            # Claim -> Paper
            edges.append({"source": claim_id, "target": paper_path, "relation": "documented_in"})
            # Claim -> Run
            edges.append({"source": claim_id, "target": run_id, "relation": "supported_by"})
            # Run -> Tools
            for tool in tools_used:
                edges.append({"source": run_id, "target": tool, "relation": "executed_via"})

            # Deduplicate edges
            seen = set()
            new_edges = []
            for e in edges:
                key = (e["source"], e["target"], e["relation"])
                if key not in seen:
                    new_edges.append(e)
                    seen.add(key)
            manifest["edges"] = new_edges

            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)

            return {"updated": True}
        except Exception as e:
            return {"updated": False, "reason": str(e)}

    def _update_evidence_index(self, claim_id: str, output_paths: List[str], tools_used: List[str], seeds_used: int):
        """
        Append a minimal evidence index entry. Does not overwrite existing entries.
        """
        if not claim_id:
            return {"updated": False, "reason": "missing_claim_id"}
        path = "registry/evidence_index.json"
        data = self._load_json(path)
        if data is None:
            data = []
        if not isinstance(data, list):
            return {"updated": False, "reason": "unexpected_evidence_index_shape"}

        if any(isinstance(e, dict) and e.get("run_id") == claim_id for e in data):
            return {"updated": False, "reason": "already_present"}

        entry = {
            "run_id": claim_id,
            "run_path": f"outputs\\\\runs\\\\{claim_id}",
            "tools_used": tools_used or [],
            "seeds": list(range(1, seeds_used + 1)) if seeds_used and seeds_used <= 64 else [],
            "claim_gate_input": None,
            "certification_evidence_packet": None,
            "logs_path": f"outputs\\\\runs\\\\{claim_id}\\\\logs",
            "status": "partial",
            "linked_paths": output_paths or [],
        }
        data.append(entry)
        self._write_json(path, data)
        return {"updated": True}

    def _ensure_claim_registry_entry(self, claim_id: str, paper_path: str, metadata: Dict[str, Any], term_roles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ensure a claim exists in registry/claim_registry.json. Append-only if missing.
        """
        if not claim_id:
            return {"updated": False, "reason": "missing_claim_id"}
        path = "registry/claim_registry.json"
        data = self._load_json(path) or {}
        if not isinstance(data, dict):
            return {"updated": False, "reason": "unexpected_claim_registry_shape"}
        data.setdefault("claims", [])
        if any(isinstance(c, dict) and c.get("claim_id") == claim_id for c in data["claims"]):
            return {"updated": False, "reason": "already_present"}

        entry = {
            "claim_id": claim_id,
            "source_claim_id": claim_id,
            "title": str(metadata.get("title", "") or os.path.basename(paper_path)),
            "claim_statement": str(metadata.get("claim_statement", "") or "See linked paper for scoped claim statement."),
            "status": "C2_test_designed",
            "claim_type": str(metadata.get("charter_classification", "provisional")).lower(),
            "classification": str(metadata.get("classification", "proposed_interpretation")).lower(),
            "model_class": "multi_mechanism",
            "models_used": metadata.get("models_used", []),
            "model_classes": metadata.get("model_classes", []),
            "seeds_used": metadata.get("seeds_used", 0),
            "falsification_run": metadata.get("falsification_run", False),
            "evidence_paths": metadata.get("recoverable_outputs", []),
            "terms_used": [{"term": tr.get("term", ""), "role": tr.get("role", "")} for tr in term_roles],
            "paper_path": paper_path,
            "last_updated": datetime.datetime.now(datetime.timezone.utc).date().isoformat(),
        }
        data["claims"].append(entry)
        self._write_json(path, data)
        return {"updated": True}

    def _ensure_gap_queue_terms(self, terms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add missing narrative/derived terms to registry/lexicon_gap_queue.json candidate_new_terms.
        Does not promote anything.
        """
        path = "registry/lexicon_gap_queue.json"
        data = self._load_json(path) or {}
        if not isinstance(data, dict):
            return {"updated": False, "reason": "unexpected_gap_queue_shape"}
        data.setdefault("candidate_new_terms", [])
        existing = {str(t.get("term", "")).strip().lower() for t in data["candidate_new_terms"] if isinstance(t, dict)}

        appended = 0
        for t in terms:
            term = str(t.get("term", "")).strip()
            if not term:
                continue
            if term.lower() in existing:
                continue
            data["candidate_new_terms"].append(t)
            existing.add(term.lower())
            appended += 1

        if appended:
            self._write_json(path, data)
        return {"updated": appended > 0, "appended": appended}

    def _ensure_validation_registry_terms(self, term_role_bindings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add/update role-specific entries in registry/lexicon_validation_registry.json.
        Evidence may be attached, but status is capped by computed evidence level and never auto-promoted beyond it.
        """
        path = "registry/lexicon_validation_registry.json"
        data = self._load_json(path) or {}
        if not isinstance(data, dict):
            return {"updated": False, "reason": "unexpected_validation_registry_shape"}
        data.setdefault("terms", {})
        updated = False

        for b in term_role_bindings:
            term = self.lexicon_v.normalize_term(str(b.get("term", "")).strip())
            role = str(b.get("role", "")).strip()
            if not term or not role:
                continue
            term_entry = data["terms"].setdefault(term, {"roles": {}})
            roles = term_entry.setdefault("roles", {})
            role_entry = roles.setdefault(role, {})
            # Status: do not increase beyond computed evidence level if already present and higher.
            desired = str(b.get("evidence_level", "L0"))
            existing = str(role_entry.get("status", "L0"))
            order = {"GAP_OPEN": 0, "L0": 0, "L1": 1, "L2": 2, "L3": 3}
            if order.get(existing, 0) > order.get(desired, 0):
                desired = existing
            if role_entry.get("status") != desired:
                role_entry["status"] = desired
                updated = True

            # Evidence pointers (append-only sets)
            for k in ("evidence_paths", "models_used", "mechanism_classes", "observables", "output_paths", "downgrade_reasons"):
                role_entry.setdefault(k, [])
            for ep in b.get("evidence_paths", []) or []:
                if ep not in role_entry["evidence_paths"]:
                    role_entry["evidence_paths"].append(ep)
                    updated = True
            for tool in b.get("tools", []) or []:
                if tool not in role_entry["models_used"]:
                    role_entry["models_used"].append(tool)
                    updated = True
            for mc in b.get("model_classes", []) or []:
                if mc not in role_entry["mechanism_classes"]:
                    role_entry["mechanism_classes"].append(mc)
                    updated = True
            for ob in b.get("observables", []) or []:
                if ob not in role_entry["observables"]:
                    role_entry["observables"].append(ob)
                    updated = True
            for op in b.get("output_paths", []) or []:
                if op not in role_entry["output_paths"]:
                    role_entry["output_paths"].append(op)
                    updated = True
            for dr in b.get("downgrade_reasons", []) or []:
                if dr not in role_entry["downgrade_reasons"]:
                    role_entry["downgrade_reasons"].append(dr)
                    updated = True

        if updated:
            self._write_json(path, data)
        return {"updated": updated}

    def _apply_paper_lexicon_role_binding_patch(
        self,
        paper_path: str,
        content: str,
        claim_id: str,
        term_roles: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Inserts '### 2.1 Lexicon Role Binding' after Theoretical Mapping (### 2.) if missing,
        and adds metadata.lexicon.terms_used to bind term-roles for the gate.
        """
        if "### 2.1 Lexicon Role Binding" not in content:
            insert = "### 2.1 Lexicon Role Binding\n```json\n" + json.dumps({"term_roles": term_roles}, indent=2, ensure_ascii=False) + "\n```\n\n"
            # place after Theoretical Mapping JSON block if possible
            m = re.search(r"(###\s*2\.\s*Theoretical Mapping.*?```json\s*\n.*?\n```)", content, re.DOTALL | re.IGNORECASE)
            if m:
                content = content[: m.end(1)] + "\n\n" + insert + content[m.end(1) :]
            else:
                content = insert + content

        # Update metadata JSON block to include lexicon terms_used
        blocks = self._extract_json_blocks(content)
        if not blocks:
            return {"patched": False, "reason": "no_metadata_json_block"}
        meta = blocks[0]
        meta.setdefault("lexicon", {})
        meta["lexicon"]["terms_used"] = [{"term": tr.get("term", ""), "role": tr.get("role", "")} for tr in term_roles]
        # rewrite first json block in content
        def repl_first(match):
            return "```json\n" + json.dumps(meta, indent=2, ensure_ascii=False) + "\n```"
        content_new = re.sub(r"```json\s*\n(.*?)\n```", repl_first, content, count=1, flags=re.DOTALL | re.IGNORECASE)

        with open(paper_path, "w", encoding="utf-8") as f:
            f.write(content_new)
        return {"patched": True}

    def _lexicon_failure_recovery(self, paper_path: str, content: str, metadata: Dict[str, Any], lexicon_validation: Dict[str, Any], downgrades: List[str]):
        claim_id = str(metadata.get("claim_id", "")).strip() if isinstance(metadata, dict) else ""
        if not claim_id:
            claim_id = self.tracer.run_id

        out_dir = os.path.join("outputs", "runs", claim_id)
        os.makedirs(out_dir, exist_ok=True)

        failed_terms = []
        details = lexicon_validation.get("details", {}) if isinstance(lexicon_validation, dict) else {}
        for item in details.get("below_L2", []) + details.get("gaps", []):
            if isinstance(item, dict):
                failed_terms.append(item.get("term") or item.get("raw_term") or "")
        failed_terms.extend(self._detect_narrative_terms_from_paper(content))
        failed_terms = [t for t in dict.fromkeys([str(t).strip() for t in failed_terms]) if t]

        primitives = {"epsilon", "residue", "rho", "coupling", "delta", "orientation_minus_i"}
        classified = []
        for t in failed_terms:
            norm = self.lexicon_v.normalize_term(t)
            layer = "primitive" if norm in primitives else "narrative_label"
            classified.append({"term": t, "normalized": norm, "layer": layer})

        # Reduction mapping for known narrative labels (warp paper)
        replacements = {
            "misalignment threshold": {
                "reduced_term": "threshold_transition",
                "role_name": "threshold_transition",
                "process_rewrite": "A parameter boundary where bounded -(i) selection changes stability or cardinality.",
                "primitive_basis": ["epsilon", "residue", "orientation_minus_i"],
                "observable": "alignment_success_rate jump",
                "metric": "alignment_success_rate",
                "falsification_condition": "No categorical transition near s_crit under sweep.",
            },
            "forced lock": {
                "reduced_term": "stable_selection_regime",
                "role_name": "stable_selection_regime",
                "process_rewrite": "A regime where -(i) remains uniquely selected under forcing.",
                "primitive_basis": ["epsilon", "orientation_minus_i", "residue"],
                "observable": "alignment_success_rate approaching 1.0",
                "metric": "alignment_success_rate",
                "falsification_condition": "Super-threshold forcing does not produce stable selection.",
            },
            "no ringdown technosignature": {
                "reduced_term": "non_oscillatory_collapse_signature",
                "role_name": "non_oscillatory_collapse_signature",
                "process_rewrite": "A collapse signature where selection failure occurs without dominant oscillatory relaxation.",
                "primitive_basis": ["delta", "rho", "orientation_minus_i"],
                "observable": "dominant_power_fraction below control ringdown level",
                "metric": "dominant_power_fraction",
                "falsification_condition": "Collapse shows dominant-mode ringdown comparable to control.",
            },
        }

        reduced = []
        for t in failed_terms:
            key = t.strip().lower()
            if key in replacements:
                base = replacements[key]
                reduced.append(
                    {
                        "original_term": t,
                        "reduced_term": base["reduced_term"],
                        "role_name": base["role_name"],
                        "process_rewrite": base["process_rewrite"],
                        "primitive_basis": base["primitive_basis"],
                        "observable": base["observable"],
                        "metric": base["metric"],
                        "falsification_condition": base["falsification_condition"],
                        "allowed_claim_usage": "proposed_interpretation",
                    }
                )

        # Bind evidence (conservative L1/L2 only; never L3 auto-promotion here)
        model_classes = metadata.get("model_classes", []) if isinstance(metadata, dict) else []
        models_used = metadata.get("models_used", []) if isinstance(metadata, dict) else []
        seeds_used = int(metadata.get("seeds_used", 0) or 0) if isinstance(metadata, dict) else 0
        falsification_vectors = metadata.get("falsification_vectors", []) if isinstance(metadata, dict) else []
        recoverable = metadata.get("recoverable_outputs", []) if isinstance(metadata, dict) else []

        evidence_level = self._compute_evidence_level(model_classes, seeds_used, falsification_vectors)
        if evidence_level == "L2":
            # Recovery system never auto-promotes to L3.
            evidence_level = "L2"

        bindings = []
        for r in reduced:
            bindings.append(
                {
                    "term": r["reduced_term"],
                    "role": r["role_name"],
                    "claim_id": claim_id,
                    "evidence_paths": recoverable,
                    "tools": models_used,
                    "model_classes": model_classes,
                    "seeds_used": seeds_used,
                    "observables": [r["metric"]],
                    "falsification_vectors": falsification_vectors,
                    "evidence_level": evidence_level if evidence_level != "L0" else "L1",
                    "promotion_allowed": False,
                    "downgrade_reasons": downgrades,
                    "output_paths": recoverable,
                }
            )

        # Update gap queue for narrative labels (if missing)
        gap_terms = []
        for r in reduced:
            gap_terms.append(
                {
                    "term": r["original_term"],
                    "status": "GAP_OPEN",
                    "default_claim_status": "PROVISIONAL",
                    "reason_for_induction": "Auto-detected during lexicon failure recovery.",
                    "source_context": {"source_type": "governance_gate_recovery", "source_path_or_note": paper_path},
                    "proposed_definition": r["reduced_term"],
                    "process_rewrite": r["process_rewrite"],
                    "primitive_mapping": {p: p for p in r["primitive_basis"]},
                    "proposed_roles": [
                        {
                            "role_name": r["role_name"],
                            "operational_definition": r["process_rewrite"],
                            "metrics": [r["metric"]],
                            "candidate_tools": models_used,
                            "falsification_condition": r["falsification_condition"],
                            "evidence_level": "L0",
                            "charter_classification": "provisional",
                        }
                    ],
                }
            )

        gap_update = self._ensure_gap_queue_terms(gap_terms)
        val_update = self._ensure_validation_registry_terms(bindings)
        ev_update = self._update_evidence_index(claim_id, recoverable, models_used, seeds_used)

        # Patch paper: bind roles and insert section 2.1
        paper_term_roles = [
            {
                "term": b["term"],
                "role": b["role"],
                "process_rewrite": next((x["process_rewrite"] for x in reduced if x["reduced_term"] == b["term"]), ""),
                "primitive_basis": next((x["primitive_basis"] for x in reduced if x["reduced_term"] == b["term"]), []),
                "observable": b["observables"][0] if b.get("observables") else "",
                "metric": b["observables"][0] if b.get("observables") else "",
                "evidence_paths": recoverable,
                "mechanism_classes": model_classes,
                "evidence_level": b["evidence_level"],
                "claim_usage": "proposed_interpretation",
            }
            for b in bindings
        ][:3]
        paper_patch_result = self._apply_paper_lexicon_role_binding_patch(paper_path, content, claim_id, paper_term_roles)

        claim_reg_update = self._ensure_claim_registry_entry(claim_id, paper_path, metadata, paper_term_roles)

        # Required outputs
        self._write_json(os.path.join(out_dir, "lexicon_failure_report.json"), {"claim_id": claim_id, "lexicon_failure_terms": failed_terms, "classified_terms": classified})
        self._write_json(os.path.join(out_dir, "lexicon_reduction_map.json"), {"claim_id": claim_id, "reductions": reduced})
        with open(os.path.join(out_dir, "lexicon_role_binding_patch.md"), "w", encoding="utf-8") as f:
            f.write(f"# Lexicon Role Binding Patch for {paper_path}\n\n")
            f.write("This gate run applied an in-place patch to bind term roles. See updated paper.\n")
        self._write_json(
            os.path.join(out_dir, "lexicon_registry_update_summary.json"),
            {"gap_queue": gap_update, "validation_registry": val_update, "evidence_index": ev_update, "claim_registry": claim_reg_update, "paper_patch": paper_patch_result},
        )

        return {
            "out_dir": out_dir,
            "paper_patch": paper_patch_result,
            "gap_queue": gap_update,
            "validation_registry": val_update,
            "evidence_index": ev_update,
            "claim_registry": claim_reg_update,
        }

    def process(self, paper_path: str, target_level: str = "C4", intent: str = "validate", strict: bool = False, _recovery_enabled: bool = True):
        # --- Empirical Governance Check (PCD_EMPIRICAL_GOVERNANCE_RUNTIME_INTEGRATION_V1) ---
        if hasattr(self, 'empirical_governance_status') and self.empirical_governance_status["status"] == "ACTIVE":
             import scripts.check_empirical_governance as ceg
             empirical_res = ceg.check_empirical_governance(paper_path)
             if empirical_res["final_result"] == "BLOCKED":
                  print(f"FATAL: Empirical Governance Block. Details: {json.dumps(empirical_res['blocking_failures'], indent=2)}")
                  sys.exit(1)
        
        with open(paper_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        json_blocks = self._extract_json_blocks(content)
        # Find the metadata block (must contain claim_id)
        metadata = {}
        for b in json_blocks:
            if "claim_id" in b:
                metadata = b
                break
        if not metadata and json_blocks:
            metadata = json_blocks[0]

        # Heuristic: the first non-metadata JSON block containing lexicon primitives is treated as Theoretical Mapping.
        theoretical_mapping: Dict[str, Any] = {}
        for b in json_blocks[1:]:
            if any(k in b for k in ("epsilon", "residue", "rho", "coupling", "delta", "orientation_minus_i")):
                theoretical_mapping = b
                break

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
        
        # Load manifest to check status
        manifest = {}
        manifest_path = "registry/tool_manifest.json"
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except: pass
        
        tool_status_map = {t.get("name"): t.get("status", "ACTIVE") for t in manifest.get("tools", [])}
        
        tools = []
        for tn in tool_names:
            if tn == "unknown": continue
            status = tool_status_map.get(tn, "ACTIVE")
            tools.append({
                "tool_name": tn,
                "status": status,
                "implementation_language": "cpp" if "cpp" in tn.lower() else "python",
                "cpp_equivalent_available": True # Assume True for gate logic to trigger check
            })

        # --- Lexicon validation (term-role gating) ---
        required_term_roles: List[Dict[str, str]] = []
        lexicon_meta = metadata.get("lexicon", {}) if isinstance(metadata, dict) else {}
        terms_used = lexicon_meta.get("terms_used") if isinstance(lexicon_meta, dict) else None

        if isinstance(terms_used, list) and terms_used:
            for item in terms_used:
                if isinstance(item, dict):
                    required_term_roles.append(
                        {"term": str(item.get("term", "")).strip(), "role": str(item.get("role", "")).strip()}
                    )
                elif isinstance(item, str):
                    required_term_roles.append({"term": item.strip(), "role": ""})
        else:
            for t in metadata.get("primitive_mapping", []) if isinstance(metadata, dict) else []:
                if isinstance(t, str):
                    required_term_roles.append({"term": t.strip(), "role": ""})
            for k in theoretical_mapping.keys() if isinstance(theoretical_mapping, dict) else []:
                if isinstance(k, str):
                    required_term_roles.append({"term": k.strip(), "role": ""})

        # de-dup term-role pairs
        seen = set()
        deduped: List[Dict[str, str]] = []
        for tr in required_term_roles:
            term_key = (tr.get("term") or "").strip().lower()
            role_key = (tr.get("role") or "").strip().lower()
            if not term_key:
                continue
            key = (term_key, role_key)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(tr)
        required_term_roles = deduped

        lexicon_validation = self.lexicon_v.lexicon_validation_check(required_term_roles)

        # --- Math validation (foundational support) ---
        # Extract LNNN and PNNN references from content
        found_lemmas = sorted(list(set(re.findall(r"\b(L\d{3})\b", content))))
        found_proofs = sorted(list(set(re.findall(r"\b(P\d{3})\b", content))))
        math_validation = self.math_v.validate(found_lemmas + found_proofs, target_level)

        requested_classification = ""
        if isinstance(metadata, dict):
            requested_classification = str(
                metadata.get("classification", metadata.get("requested_classification", "")) or ""
            ).strip().lower()

        semantic_projection_validation = self.semantic_projection_v.validate(content, requested_classification, metadata)

        results = {
            "template": self.template_v.validate(content),
            "consistency": self.consistency_v.validate(content, metadata),
            "measurement": self.measure_v.validate(content, measurements, target_level, metadata),
            "falsification": self.falsification_v.validate(falsification, target_level, strict),
            "cpp": self.cpp_v.validate(tools, target_level),
            "lexicon_validation": lexicon_validation,
            "math_validation": math_validation,
            "semantic_projection": semantic_projection_validation,
        }

        final_classification = requested_classification or ""
        downgrades_applied: List[str] = []
        blocked_reasons: List[str] = []

        final_pass = all(v["pass"] for k, v in results.items() if k not in ["cpp", "math_validation"])
        if not math_validation["pass"] and target_level in ["C5", "C6"]:
             final_pass = False # Math failure blocks C5/C6
             blocked_reasons.append("unverified_mathematical_foundations")
        if not semantic_projection_validation["pass"]:
             final_pass = False
             if semantic_projection_validation["details"].get("unmarked_protected_terms"):
                 blocked_reasons.append("semantic_projection_unmarked_protected_term")
             if semantic_projection_validation["details"].get("identity_violations"):
                 blocked_reasons.append("semantic_projection_identity_language")
             if semantic_projection_validation["details"].get("scope_violation") is not None:
                 blocked_reasons.append("semantic_projection_scope_phrase_missing")

        if not final_pass: gate_result = "block"
        else: gate_result = "pass"

        cap = (lexicon_validation.get("details", {}) or {}).get("cap_classification")
        if cap:
            downgrades_applied.append("lexicon_term_below_L2_caps_classification")
            final_classification = "proposed_interpretation"
            if requested_classification in ("supported", "verified"):
                gate_result = "downgrade" if gate_result != "block" else "block"

        # Apply intent limits
        intent_limits = self.charter.get("intent_limits", {})
        allowed_max = intent_limits.get(intent, "C2")
        levels = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "L0_exploratory", "L1_structural", "L2_supported", "L3_strong_support", "L4_mechanism_independent", "L5_rigor_endorsed"]
        final_level = target_level
        # For legacy logic, map L levels to C limits if necessary
        try:
            if levels.index(target_level) > levels.index(allowed_max):
                final_level = allowed_max
                gate_result = "downgrade"
                downgrades_applied.append("intent_limit_applied")
        except ValueError:
            pass

        # --- Lexicon Failure Recovery System (PATCH_LEXICON_FAILURE_RECOVERY_SYSTEM_V1) ---
        recovery_triggered = (not lexicon_validation.get("pass", True)) or ("lexicon_term_below_L2_caps_classification" in downgrades_applied)
        recovery_context_ok = intent in ("validate", "publish", "claim_review")
        recovery_result = {"triggered": False}

        if _recovery_enabled and recovery_triggered and recovery_context_ok:
            recovery_result = {"triggered": True}
            try:
                recovery_updates = self._lexicon_failure_recovery(paper_path, content, metadata, lexicon_validation, downgrades_applied)
                recovery_result.update({"updates": recovery_updates})
                # Re-run gate once after recovery (disable re-entry to avoid loops).
                rerun = self.process(paper_path, target_level, intent, strict, _recovery_enabled=False)
                out_dir = os.path.join("outputs", "runs", str(metadata.get("claim_id", "")).strip() or self.tracer.run_id)
                rerun["lexicon_failure_recovery"] = recovery_result
                self._write_json(os.path.join(out_dir, "rerun_gate_result.json"), rerun)
                return rerun
            except Exception as e:
                recovery_result.update({"error": str(e)})

        # Persist evidence pointers back into lexicon_validation_registry without promoting term statuses.
        claim_id = str(metadata.get("claim_id", "")).strip() if isinstance(metadata, dict) else ""
        evidence_id = str(metadata.get("evidence_id", "")).strip() if isinstance(metadata, dict) else ""
        if not evidence_id:
            evidence_id = f"gate:{os.path.basename(paper_path)}"
        mechanism_classes = metadata.get("model_classes", []) if isinstance(metadata, dict) else []
        output_paths = metadata.get("recoverable_outputs", []) if isinstance(metadata, dict) else []
        seeds_used = metadata.get("seeds_used", 0) if isinstance(metadata, dict) else 0
        tools_used = list(tool_names)

        lexicon_record = self.lexicon_v.record_term_role_evidence(
            claim_id=claim_id,
            evidence_id=evidence_id,
            term_roles=required_term_roles,
            mechanism_classes=[str(x) for x in mechanism_classes if isinstance(x, str)],
            observables=[],
            output_paths=[str(x) for x in output_paths if isinstance(x, str)],
            downgrade_reasons=downgrades_applied,
        )

        # Always update evidence index
        evidence_index_update = self._update_evidence_index(claim_id, output_paths, tools_used, seeds_used)

        # Update Unified Manifest (Task 3.2: Relational Graph)
        manifest_update = self._update_unified_manifest(claim_id, paper_path, metadata, gate_result, final_level, tools_used)

        # Update claim registry with gate outcome (non-destructive merge).
        claim_registry_update = {"updated": False, "reason": "not_attempted"}
        if claim_id and os.path.exists("registry/claim_registry.json"):
            try:
                with open("registry/claim_registry.json", "r", encoding="utf-8") as f:
                    cr = json.load(f)
                claims = cr.get("claims", [])
                
                found = False
                for c in claims:
                    if c.get("claim_id") == claim_id or c.get("source_claim_id") == claim_id:
                        c["last_gate_check"] = {
                            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            "paper_path": paper_path,
                            "target_level": target_level,
                            "final_level": final_level,
                            "gate_result": gate_result,
                            "requested_classification": requested_classification,
                            "final_classification": final_classification,
                            "downgrades_applied": downgrades_applied,
                            "blocked_reasons": blocked_reasons,
                        }
                        # If gate passed, update top-level status
                        if gate_result == "pass":
                            c["status"] = self.charter.get("claim_level_mandates", {}).get(final_level, {}).get("status_ladder_target", c.get("status"))
                        
                        claim_registry_update = {"updated": True, "action": "updated_existing"}
                        found = True
                        break
                
                if not found and gate_result == "pass":
                    # Register new claim
                    new_claim = {
                        "claim_id": claim_id,
                        "title": os.path.basename(os.path.dirname(paper_path)),
                        "claim_statement": f"Within these models... See {os.path.basename(paper_path)} for details.",
                        "status": self.charter.get("claim_level_mandates", {}).get(final_level, {}).get("status_ladder_target", "C4_dual_mechanism_supported"),
                        "claim_type": metadata.get("claim_type", "empirical"),
                        "classification": final_classification,
                        "model_classes": mechanism_classes,
                        "models_used": tools_used,
                        "seeds_used": seeds_used,
                        "falsification_run": metadata.get("falsification_run", False),
                        "evidence_paths": output_paths,
                        "paper_path": paper_path,
                        "last_updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
                        "last_gate_check": {
                            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                            "paper_path": paper_path,
                            "target_level": target_level,
                            "final_level": final_level,
                            "gate_result": gate_result,
                            "requested_classification": requested_classification,
                            "final_classification": final_classification,
                            "downgrades_applied": downgrades_applied,
                            "blocked_reasons": blocked_reasons,
                        }
                    }
                    claims.append(new_claim)
                    claim_registry_update = {"updated": True, "action": "registered_new"}

                if claim_registry_update.get("updated"):
                    with open("registry/claim_registry.json", "w", encoding="utf-8") as f:
                        json.dump(cr, f, indent=2, ensure_ascii=False)
                        f.write("\n")
            except Exception as e:
                claim_registry_update = {"updated": False, "reason": str(e)}

        output = {
            "gate_result": gate_result,
            "final_level": final_level,
            "requested_classification": requested_classification,
            "final_classification": final_classification,
            "downgrades_applied": downgrades_applied,
            "blocked_reasons": blocked_reasons,
            "lexicon_failure_recovery": recovery_result,
            "registry_updates": {
                "lexicon_validation_registry": lexicon_record,
                "evidence_index": evidence_index_update,
                "claim_registry": claim_registry_update,
            },
            "checks": results,
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
