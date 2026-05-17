import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class RegistryValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.tool_manifest_path = self.root / "registry/tool_manifest.json"
        self.lexicon_val_path = self.root / "registry/lexicon_validation_registry.json"
        self.claim_reg_path = self.root / "registry/claim_registry.json"
        self.claim_scope_binding_path = self.root / "registry/claim_scope_binding_registry.json"
        self.gap_queue_path = self.root / "registry/lexicon_gap_queue.json"

    def validate_json_load(self, path):
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                return json.load(f), None
        except Exception as e:
            return None, str(e)

    def run(self):
        results = {"status": "success", "errors": []}
        
        # 1. Load all registries
        manifest, err = self.validate_json_load(self.tool_manifest_path)
        if err: results["errors"].append(f"Tool Manifest Load Error: {err}")
        
        lexicon, err = self.validate_json_load(self.lexicon_val_path)
        if err: results["errors"].append(f"Lexicon Registry Load Error: {err}")
        
        claims, err = self.validate_json_load(self.claim_reg_path)
        if err: results["errors"].append(f"Claim Registry Load Error: {err}")

        scope_bindings, err = self.validate_json_load(self.claim_scope_binding_path)
        if err: results["errors"].append(f"Claim Scope Binding Registry Load Error: {err}")

        gap_queue, err = self.validate_json_load(self.gap_queue_path)
        if err: results["errors"].append(f"Gap Queue Load Error: {err}")

        if results["errors"]:
            results["status"] = "failed"
            return results

        # 2a. Claim-scope binding must be referenced by claim registry meta
        meta = claims.get("meta", {}) if isinstance(claims, dict) else {}
        binding_ref = meta.get("claim_scope_binding_registry")
        if not binding_ref:
            results["errors"].append("Governance Error: claim_registry.meta.claim_scope_binding_registry is missing.")
        else:
            # Only require that it resolves to the canonical path or ends with the filename.
            if "claim_scope_binding_registry.json" not in str(binding_ref):
                results["errors"].append("Governance Error: claim_registry.meta.claim_scope_binding_registry does not reference claim_scope_binding_registry.json.")

        mandatory_phrase = None
        if isinstance(scope_bindings, dict):
            mandatory_phrase = (scope_bindings.get("meta") or {}).get("mandatory_scope_phrase")
        mandatory_phrase = mandatory_phrase or "Within these models..."

        # 2. Integrity Checks: All tools in lexicon registry must exist in tool manifest
        manifest_tools = {t["name"] for t in manifest.get("tools", [])}
        for term, data in lexicon.get("terms", {}).items():
            for role, role_data in data.get("roles", {}).items():
                for model in role_data.get("models_used", []):
                    if model not in manifest_tools and "_v1" not in model: # v1 often python counterparts
                        results["errors"].append(f"Integrity Error: Term '{term}' role '{role}' uses unregistered tool '{model}'")

        # 3. Claim registry: if a claim statement is present, enforce the mandatory scope phrase.
        for c in claims.get("claims", []):
            stmt = c.get("claim_statement")
            if not stmt:
                continue
            if mandatory_phrase not in stmt:
                results["errors"].append(f"Claim Scope Error: claim_id '{c.get('claim_id')}' claim_statement missing mandatory scope phrase '{mandatory_phrase}'.")

        # 4. Python↔C++ equivalence gate (manifest must declare reference implementation for C++ tools at/above C1)
        for tool in manifest.get("tools", []):
            if tool.get("implementation_language") != "cpp":
                continue
            level = str(tool.get("certification_level", "C0"))
            if level.startswith("C") and len(level) >= 2:
                try:
                    numeric = int(level[1])
                except:
                    numeric = 0
            else:
                numeric = 0
            if numeric >= 1:
                if not tool.get("reference_implementation") or not tool.get("has_reference_implementation"):
                    results["errors"].append(f"Equivalence Gate Error: C++ tool '{tool.get('name')}' (level {level}) missing reference_implementation/has_reference_implementation.")

        if results["errors"]:
            results["status"] = "failed"
        return results

class EngineValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.tool_manifest_path = self.root / "registry/tool_manifest.json"

    def run_smoke_test(self, tool_name, entry_point):
        wrapper = self.root / entry_point
        out_dir = self.root / f"outputs/debug/smoke_{tool_name}"
        out_dir.mkdir(parents=True, exist_ok=True)
        
        config = {"steps": 1, "nx": 8, "ny": 8, "nz": 8, "num_nodes": 8}
        config_path = out_dir / "smoke_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f)

        if wrapper.suffix == ".py":
            cmd = [sys.executable, str(wrapper.absolute()), "--config", str(config_path.absolute()), "--out", str(out_dir.absolute())]
        else:
            cmd = [str(wrapper.absolute()), "--config", str(config_path.absolute()), "--out", str(out_dir.absolute())]
            
        try:
            # Run in the tool's directory if it's an executable that might need local DLLs
            cwd = wrapper.parent.absolute()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=cwd)
            if result.returncode == 0:
                return True, None
            return False, result.stderr
        except Exception as e:
            return False, str(e)

    def run(self):
        results = {"status": "success", "tools_tested": [], "failures": [], "skipped": []}
        
        with open(self.tool_manifest_path, 'r', encoding='utf-8-sig') as f:
            manifest = json.load(f)

        for tool in manifest.get("tools", []):
            if tool.get("certification_level") == "C4":
                # Only smoke test tools with governed wrappers
                if "sim_governed.py" in tool.get("entry_point", ""):
                    success, err = self.smoke_test_tool(tool)
                    results["tools_tested"].append(tool["name"])
                    if not success:
                        results["failures"].append({"tool": tool["name"], "error": err})
                else:
                    results["skipped"].append(tool["name"])

        if results["failures"]:
            results["status"] = "failed"
        return results

    def smoke_test_tool(self, tool):
        # Specific logic for C++ engines elevated to C4
        name = tool["name"]
        entry = tool["entry_point"]
        return self.run_smoke_test(name, entry)

class HygieneValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.results_dir = self.root / "results"

    def run(self):
        results = {"status": "success", "violations": []}
        if not self.results_dir.exists():
            return results

        for folder in self.results_dir.iterdir():
            if not folder.is_dir(): continue
            
            # Check naming convention: YYYY-MM-DD_runNN_name
            name = folder.name
            try:
                parts = name.split('_')
                datetime.strptime(parts[0], "%Y-%m-%d")
                if not parts[1].startswith("run"): raise ValueError()
            except:
                results["violations"].append(f"Naming Violation: '{name}' does not follow date_runNN_name schema.")
                continue

            # Check contents: paper.md, data/, artifacts/
            if not (folder / "paper.md").exists():
                results["violations"].append(f"Missing Paper: '{name}/paper.md' not found.")
            if not (folder / "data").is_dir():
                results["violations"].append(f"Missing Data: '{name}/data/' directory not found.")
            if not (folder / "artifacts").is_dir():
                results["violations"].append(f"Missing Artifacts: '{name}/artifacts/' directory not found.")

        if results["violations"]:
            results["status"] = "failed"
        return results

class MathValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        # Legacy math registry (kept for backward compatibility if present)
        self.math_registry_path = self.root / "registry/math_registry.json"
        self.math_hashes_path = self.root / "registry/math_hashes.json"
        # Stabilized math-core lock (registry + codex)
        self.math_core_dir = self.root / "registry/math"
        self.math_codex_dir = self.root / "docs/math"
        self.math_core_hashes_path = self.root / "registry/math_core_hashes.json"

    def calculate_hash(self, path):
        import hashlib
        try:
            content = path.read_bytes()
            return hashlib.sha256(content).hexdigest()
        except:
            return None

    def run(self):
        results = {"status": "success", "errors": [], "warnings": []}
        
        # If neither legacy nor stabilized math core exists, treat as no-op.
        if (not self.math_registry_path.exists()) and (not self.math_core_dir.exists()) and (not self.math_codex_dir.exists()):
            return results

        # Legacy check (if present)
        if self.math_registry_path.exists():
            with open(self.math_registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)

            hashes = {}
            if self.math_hashes_path.exists():
                with open(self.math_hashes_path, 'r', encoding='utf-8') as f:
                    hashes = json.load(f)

            new_hashes = {}
            items = registry.get('lemmas', []) + registry.get('proofs', [])
            for item in items:
                item_id = item['item_id']
                path = self.root / item['path']
                if not path.exists():
                    results["errors"].append(f"Math Registry Sync Error: File for '{item_id}' not found at {item['path']}")
                    continue

                current_hash = self.calculate_hash(path)
                new_hashes[item_id] = current_hash

                if item_id in hashes and hashes[item_id] != current_hash:
                    if "TEMPLATE" in path.name:
                        continue
                    results["errors"].append(f"Governance Violation: Math file '{item['path']}' was modified (Additive-Only Rule Violation).")

            if not results["errors"]:
                with open(self.math_hashes_path, 'w', encoding='utf-8') as f:
                    json.dump(new_hashes, f, indent=2)

        # Stabilized math-core lock (hash registry/math/*.json and docs/math/*.md)
        core_paths = []
        if self.math_core_dir.is_dir():
            core_paths.extend(sorted(self.math_core_dir.glob("*.json")))
        if self.math_codex_dir.is_dir():
            core_paths.extend(sorted(self.math_codex_dir.glob("*.md")))

        if core_paths:
            prior = {}
            if self.math_core_hashes_path.exists():
                try:
                    with open(self.math_core_hashes_path, "r", encoding="utf-8-sig") as f:
                        prior = json.load(f)
                except Exception as e:
                    results["errors"].append(f"Math Core Hash Load Error: {e}")

            current = {"meta": {"generated_at": datetime.now().isoformat()}, "files": {}}
            for p in core_paths:
                rel = str(p.relative_to(self.root)).replace("\\", "/")
                current["files"][rel] = self.calculate_hash(p)

            if prior and isinstance(prior, dict) and "files" in prior:
                for rel, h in current["files"].items():
                    if rel in prior["files"] and prior["files"][rel] != h:
                        results["errors"].append(f"Math Core Lock Violation: '{rel}' changed since last lock baseline.")
            else:
                results["warnings"].append("Math Core Lock: baseline missing; writing initial math_core_hashes.json.")

            if not results["errors"]:
                with open(self.math_core_hashes_path, "w", encoding="utf-8") as f:
                    json.dump(current, f, indent=2)

        if results["errors"]:
            results["status"] = "failed"
        elif results["warnings"]:
            results["status"] = "warning"
        return results

class DBValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.db_path = self.root / "registry/db/acellorator_index.sqlite"
        self.schema_path = self.root / "registry/db/schema.sql"

    def run(self):
        try:
            from scripts.db.db_health_check import run_db_health_check
        except ImportError:
            import sys
            sys.path.append(str(self.root / "scripts/db"))
            try:
                from db_health_check import run_db_health_check
            except ImportError:
                return {"status": "failed", "errors": ["Could not import db_health_check script."]}

        health, errors = run_db_health_check(str(self.db_path), str(self.schema_path))
        
        results = {
            "status": "success" if health["status"] != "fail" else "failed",
            "errors": errors,
            "warnings": health["stale_index_warnings"],
            "db_health": health
        }
        
        if health["status"] == "warning":
            results["status"] = "warning"
            
        return results

class MathProgramValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)

    def run(self):
        try:
            from scripts.math.math_program_validate import validate_math_program
        except ImportError:
            import sys
            sys.path.append(str(self.root / "scripts/math"))
            try:
                from math_program_validate import validate_math_program
            except ImportError:
                return {"status": "failed", "errors": ["Could not import math_program_validate script."]}

        res = validate_math_program()
        return res["math_program_validation"]

class ImplementationValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.tool_manifest_path = self.root / "registry/tool_manifest.json"
        self.cert_reg_path = self.root / "registry/tool_certification_registry.json"
        self.equiv_failures_path = self.root / "registry/equivalence_failure_registry.json"

    def validate_json_load(self, path):
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                return json.load(f), None
        except Exception as e:
            return None, str(e)

    def run(self):
        results = {"status": "success", "errors": [], "warnings": []}
        
        manifest, err = self.validate_json_load(self.tool_manifest_path)
        if err: return {"status": "failed", "errors": [f"Manifest Load: {err}"]}
        
        cert_reg, err = self.validate_json_load(self.cert_reg_path)
        if err: results["errors"].append(f"Certification Registry Load: {err}")

        # 1. Compiled tools have reference declared
        for tool in manifest.get("tools", []):
            if tool.get("implementation_language") in ["cpp", "hybrid", "cuda"]:
                if tool.get("equivalence_required") is True:
                    ref = tool.get("reference_baseline")
                    if not ref or ref == "NOT_DECLARED":
                        results["errors"].append(f"Equivalence Error: Tool '{tool['name']}' missing reference_baseline.")

        # 2. Certification state valid
        if cert_reg:
            manifest_tool_names = {t["name"] for t in manifest.get("tools", [])}
            for entry in cert_reg.get("tools", []):
                tname = entry.get("name")
                if tname not in manifest_tool_names:
                    results["errors"].append(f"Certification Error: Registry tool '{tname}' missing from manifest.")
                
                state = entry.get("state")
                if state == "CERTIFIED_C4":
                    # Check tool manifest for equivalence verified status
                    mtool = next((t for t in manifest["tools"] if t["name"] == tname), None)
                    if mtool and mtool.get("latest_equivalence_packet") == "NONE":
                        results["warnings"].append(f"Certification Warning: Tool '{tname}' is C4 but has no equivalence packet indexed.")

        if results["errors"]:
            results["status"] = "failed"
        elif results["warnings"]:
            results["status"] = "warning"
        return results

class EvidenceValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.pb_reg_path = self.root / "registry/prediction_binding_registry.json"
        self.ds_reg_path = self.root / "registry/public_dataset_registry.json"

    def validate_json_load(self, path):
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                return json.load(f), None
        except Exception as e:
            return None, str(e)

    def run(self):
        results = {"status": "success", "errors": [], "warnings": []}
        
        pb, err = self.validate_json_load(self.pb_reg_path)
        if err: results["errors"].append(f"Prediction Binding Registry Load: {err}")
        
        ds, err = self.validate_json_load(self.ds_reg_path)
        if err: results["errors"].append(f"Public Dataset Registry Load: {err}")

        if results["errors"]:
            results["status"] = "failed"
            return results

        # 1. Prediction bindings have falsification conditions
        for binding in pb.get("bindings", []):
            if not binding.get("falsification_condition"):
                results["errors"].append(f"Evidence Error: Prediction binding '{binding['binding_id']}' missing falsification_condition.")

        # 2. Datasets have associated prediction bindings
        if ds:
            for dataset in ds.get("datasets", []):
                if not dataset.get("associated_prediction_bindings"):
                    results["warnings"].append(f"Evidence Warning: Dataset '{dataset['dataset_id']}' has no associated prediction bindings.")

        if results["errors"]:
            results["status"] = "failed"
        elif results["warnings"]:
            results["status"] = "warning"
        return results

class CampaignValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.tpl_reg_path = self.root / "registry/evidence_campaign_template_registry.json"
        self.cp_reg_path = self.root / "registry/cross_dataset_pairing_registry.json"

    def validate_json_load(self, path):
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                return json.load(f), None
        except Exception as e:
            return None, str(e)

    def run(self):
        results = {"status": "success", "errors": [], "warnings": []}
        
        tpl, err = self.validate_json_load(self.tpl_reg_path)
        if err: results["errors"].append(f"Campaign Template Registry Load: {err}")
        
        cp, err = self.validate_json_load(self.cp_reg_path)
        if err: results["errors"].append(f"Cross-Dataset Pairing Registry Load: {err}")

        if results["errors"]:
            results["status"] = "failed"
            return results

        # 1. Templates have counterexamples or null models
        for template in tpl.get("templates", []):
            if not template.get("counterexample_dataset") and not template.get("null_model"):
                results["errors"].append(f"Campaign Error: Template '{template['template_id']}' missing adversarial control.")

        # 2. Pairings are verified
        if cp:
            for pairing in cp.get("pairings", []):
                if pairing.get("status") != "VERIFIED":
                    results["warnings"].append(f"Campaign Warning: Pairing '{pairing['pairing_id']}' not yet verified.")

        if results["errors"]:
            results["status"] = "failed"
        elif results["warnings"]:
            results["status"] = "warning"
        return results

def main():
    parser = argparse.ArgumentParser(description="Global Ecosystem Validation Harness")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--out", default="outputs/audits/global_health_report.json", help="Report output path")
    args = parser.parse_args()

    root = Path(args.root)
    report = {
        "timestamp": datetime.now().isoformat(),
        "registry_validation": RegistryValidator(root).run(),
        "engine_validation": EngineValidator(root).run(),
        "hygiene_validation": HygieneValidator(root).run(),
        "math_validation": MathValidator(root).run(),
        "db_validation": DBValidator(root).run(),
        "math_program_validation": MathProgramValidator(root).run(),
        "implementation_validation": ImplementationValidator(root).run(),
        "evidence_validation": EvidenceValidator(root).run(),
        "campaign_validation": CampaignValidator(root).run()
    }

    report["overall_status"] = "pass" if all(v["status"] in ["success", "warning"] for k, v in report.items() if isinstance(v, dict)) else "fail"

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Global health report saved to {out_path}")
    if report["overall_status"] == "fail":
        sys.exit(1)

if __name__ == "__main__":
    main()
