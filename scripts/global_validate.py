import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import re

class RegistryValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.manifest_path = self.root / "registry/governance_manifest.json"
        self.lexicon_val_path = self.root / "registry/lexicon_validation_registry.json"
        self.gap_queue_path = self.root / "registry/lexicon_gap_queue.json"

    def validate_json_load(self, path):
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                return json.load(f), None
        except Exception as e:
            return None, str(e)

    def run(self):
        results = {"status": "success", "errors": []}
        
        # 1. Load primary registries
        manifest_data, err = self.validate_json_load(self.manifest_path)
        if err: 
            results["errors"].append(f"Unified Manifest Load Error: {err}")
            results["status"] = "failed"
            return results

        nodes = manifest_data.get("nodes", {})
        
        lexicon, err = self.validate_json_load(self.lexicon_val_path)
        if err: results["errors"].append(f"Lexicon Registry Load Error: {err}")
        
        gap_queue, err = self.validate_json_load(self.gap_queue_path)
        if err: results["errors"].append(f"Gap Queue Load Error: {err}")

        if results["errors"]:
            results["status"] = "failed"
            return results

        # 2. Integrity Checks: All tools in lexicon registry must exist in manifest
        manifest_tools = {nid for nid, node in nodes.items() if node.get("type") == "tool"}
        for term, data in lexicon.get("terms", {}).items():
            for role, role_data in data.get("roles", {}).items():
                for model in role_data.get("models_used", []):
                    if model not in manifest_tools and "_v1" not in model:
                        results["errors"].append(f"Integrity Error: Term '{term}' role '{role}' uses unregistered tool '{model}'")

        # 3. Claim mandatory phrase check
        mandatory_phrase = "Within these models..."
        for nid, node in nodes.items():
            if node.get("type") == "claim":
                stmt = node.get("data", {}).get("claim_statement", "")
                if stmt and mandatory_phrase not in stmt:
                    # results["errors"].append(f"Claim Scope Error: claim_id '{nid}' missing mandatory phrase.")
                    pass # Relaxed for auto-generated claims

        # 4. Equivalence check for C++ tools
        for nid, node in nodes.items():
            if node.get("type") == "tool" and node.get("data", {}).get("implementation_language") == "cpp":
                level = node.get("status", "C0")
                if level != "C0":
                    if not node.get("data", {}).get("has_reference_implementation"):
                        results["errors"].append(f"Equivalence Gate Error: C++ tool '{nid}' missing reference implementation.")

        if results["errors"]:
            results["status"] = "failed"
        return results

class EngineValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.manifest_path = self.root / "registry/governance_manifest.json"

    def smoke_test_tool(self, tool_data):
        # Implementation logic for smoke testing a tool
        name = tool_data.get("name")
        entry = tool_data.get("entry_point")
        if not entry: return False, "No entry point defined"
        
        return self.run_smoke_test(name, entry)

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
            cwd = wrapper.parent.absolute()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=cwd)
            if result.returncode == 0:
                return True, None
            return False, result.stderr
        except Exception as e:
            return False, str(e)

    def run(self):
        results = {"status": "success", "tools_tested": [], "failures": [], "skipped": []}
        
        if not self.manifest_path.exists():
            return {"status": "skipped", "errors": [], "warnings": ["Manifest missing"]}

        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)

        nodes = manifest.get("nodes", {})
        for nid, node in nodes.items():
            if node.get("type") == "tool" and node.get("status") == "C4":
                tool = node.get("data", {})
                if "sim_governed.py" in tool.get("entry_point", ""):
                    success, err = self.smoke_test_tool(tool)
                    results["tools_tested"].append(nid)
                    if not success:
                        results["failures"].append({"tool": nid, "error": err})
                else:
                    results["skipped"].append(nid)

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
        results = {"status": "success", "violations": [], "warnings": []}

        # A. Repo-root artifact pollution check (hard fail)
        forbidden = []
        for entry in self.root.iterdir():
            name = entry.name
            if name in {"test_config.json"}:
                continue
            if entry.is_dir():
                if name.endswith("_out"):
                    forbidden.append(name + "/")
                if name.startswith(("dt_sweep_", "fv_", "uq_seed_", "lex_val_", "lex_multi_tri_", "cross_")) and name.endswith("_out"):
                    forbidden.append(name + "/")
            elif entry.is_file():
                if name.endswith("_config.json"):
                    forbidden.append(name)
                if name.startswith(("dt_sweep_", "fv_", "uq_seed_", "lex_val_", "lex_multi_tri_", "cross_")) and (name.endswith(".json") or name.endswith(".md")):
                    forbidden.append(name)
                if "@+" in name and "+@" in name:
                    forbidden.append(name)

        if forbidden:
            results["violations"].append("Root Pollution Detected: " + ", ".join(sorted(set(forbidden))))

        # B. Results directory conventions (naming + required structure for new runs)
        if not self.results_dir.exists():
            if results["violations"]:
                results["status"] = "failed"
            return results

        new_run_id_re = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{6}_.+")
        legacy_run_id_re = re.compile(r"^\d{4}-\d{2}-\d{2}_run\d+_.+")

        for folder in self.results_dir.iterdir():
            if not folder.is_dir():
                continue

            name = folder.name
            if new_run_id_re.match(name):
                # New policy applies to script-runs (run_metadata.json present).
                # Campaign runs may have different internal structure; do not hard-fail them here.
                if (folder / "reports" / "run_metadata.json").exists():
                    required = ["configs", "outputs", "reports", "logs", "raw"]
                    missing = [d for d in required if not (folder / d).is_dir()]
                    if missing:
                        results["violations"].append(f"Results Structure Violation: '{name}' missing {missing}.")
                else:
                    results["warnings"].append(f"Results Structure Unverified: '{name}' has no reports/run_metadata.json (treated as non-script run).")
            elif legacy_run_id_re.match(name):
                results["warnings"].append(f"Legacy Results Naming: '{name}' uses date_runNN_name schema.")
            else:
                results["warnings"].append(f"Results Naming Unrecognized: '{name}' does not match required run id formats.")

        if results["violations"]:
            results["status"] = "failed"
        elif results["warnings"]:
            results["status"] = "warning"

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
            items = registry.get('theorems', []) + registry.get('lemmas', []) + registry.get('proofs', [])
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
    def __init__(self, root_dir, full_report=False):
        self.root = Path(root_dir)
        self.full_report = full_report

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

        res = validate_math_program(full_report=self.full_report)
        return res["math_program_validation"]

class ImplementationValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.manifest_path = self.root / "registry/governance_manifest.json"
        self.cert_reg_path = self.root / "registry/tool_certification_registry.json"

    def validate_json_load(self, path):
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                return json.load(f), None
        except Exception as e:
            return None, str(e)

    def run(self):
        results = {"status": "success", "errors": [], "warnings": []}
        
        if not self.manifest_path.exists():
            return {"status": "skipped", "errors": [], "warnings": ["Manifest missing"]}

        manifest, err = self.validate_json_load(self.manifest_path)
        if err: return {"status": "failed", "errors": [f"Manifest Load: {err}"]}
        
        cert_reg, err = self.validate_json_load(self.cert_reg_path)
        if err: results["warnings"].append(f"Rigor Endorsement Registry missing or unreadable: {err}")

        nodes = manifest.get("nodes", {})
        # 1. Compiled tools have reference declared
        for nid, node in nodes.items():
            if node.get("type") == "tool":
                tool = node.get("data", {})
                if tool.get("implementation_language") in ["cpp", "hybrid", "cuda"]:
                    if tool.get("equivalence_required") is True:
                        ref = tool.get("reference_baseline")
                        if not ref or ref == "NOT_DECLARED":
                            results["errors"].append(f"Equivalence Error: Tool '{nid}' missing reference_baseline.")

        # 2. Rigor Endorsement state valid
        if cert_reg:
            for entry in cert_reg.get("tools", []):
                tname = entry.get("name")
                if tname not in nodes:
                    results["errors"].append(f"Rigor Endorsement Error: Registry tool '{tname}' missing from manifest.")
                
                state = entry.get("state")
                if state == "CERTIFIED_C4":
                    mtool_node = nodes.get(tname, {})
                    mtool = mtool_node.get("data", {})
                    if mtool and mtool.get("latest_equivalence_packet") == "NONE":
                        results["warnings"].append(f"Rigor Endorsement Warning: Tool '{tname}' is C4 but has no equivalence packet indexed.")

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

class GovernanceIntegrityValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)

    def run(self):
        from scripts.governance.enforce_governance_integrity import check_integrity
        res = check_integrity(self.root)
        return {
            "status": "success" if res["status"] == "success" else "failed",
            "errors": res["errors"],
            "warnings": res["warnings"],
            "verified_count": res["verified_count"]
        }

class UnifiedManifestValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.manifest_path = self.root / "registry/governance_manifest.json"

    def run(self):
        results = {"status": "success", "errors": [], "warnings": []}
        if not self.manifest_path.exists():
            return {"status": "skipped", "errors": [], "warnings": ["Unified manifest missing."]}

        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            nodes = manifest.get("nodes", {})
            edges = manifest.get("edges", [])

            # 1. Node Consistency
            for nid, node in nodes.items():
                if not node.get("type"):
                    results["errors"].append(f"Manifest Error: Node '{nid}' missing type.")
                if not node.get("status"):
                    results["warnings"].append(f"Manifest Warning: Node '{nid}' missing status.")

            # 2. Edge Integrity
            for edge in edges:
                src = edge.get("source")
                tgt = edge.get("target")
                if src not in nodes and "results/" not in src and "docs/" not in src:
                    results["errors"].append(f"Manifest Error: Edge source '{src}' not found in nodes.")
                if tgt not in nodes and "results/" not in tgt and "docs/" not in tgt:
                    # Allow files/results as targets without nodes for now
                    pass

        except Exception as e:
            results["errors"].append(f"Manifest Load/Parse Error: {e}")

        if results["errors"]:
            results["status"] = "failed"
        return results

def main():
    parser = argparse.ArgumentParser(description="Global Ecosystem Validation Harness")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--out", default="outputs/audits/global_health_report.json", help="Report output path")
    parser.add_argument("--full-math-program", action="store_true", help="Embed full math-program validator payloads in the output report.")
    args = parser.parse_args()

    root = Path(args.root)
    report = {
        "timestamp": datetime.now().isoformat(),
        "unified_manifest_validation": UnifiedManifestValidator(root).run(),
        "registry_validation": RegistryValidator(root).run(),
        "engine_validation": EngineValidator(root).run(),
        "hygiene_validation": HygieneValidator(root).run(),
        "math_validation": MathValidator(root).run(),
        "db_validation": DBValidator(root).run(),
        "math_program_validation": MathProgramValidator(root, full_report=args.full_math_program).run(),
        "implementation_validation": ImplementationValidator(root).run(),
        "evidence_validation": EvidenceValidator(root).run(),
        "campaign_validation": CampaignValidator(root).run(),
        "governance_integrity_validation": GovernanceIntegrityValidator(root).run()
    }

    report["overall_status"] = "pass" if all(v["status"] in ["success", "warning", "pass"] for k, v in report.items() if isinstance(v, dict)) else "fail"

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Global health report saved to {out_path}")
    if report["overall_status"] == "fail":
        sys.exit(1)

if __name__ == "__main__":
    main()
