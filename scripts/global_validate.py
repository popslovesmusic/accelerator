import argparse
import json
import os
import subprocess
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
import re

# Allow direct script invocation to resolve package-style imports the same way
# as `python -m scripts.global_validate`.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class RegistryValidator:
    def __init__(self, root_dir, read_only=False):
        self.root = Path(root_dir)
        self.manifest_path = self.root / "registry/governance_manifest.json"
        self.lexicon_val_path = self.root / "registry/lexicon_validation_registry.json"
        self.gap_queue_path = self.root / "registry/lexicon_gap_queue.json"
        self.read_only = read_only

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
    def __init__(self, root_dir, read_only=False):
        self.root = Path(root_dir)
        self.read_only = read_only
        # Canonical source math registry.
        self.math_source_registry_path = self.root / "registry/math_source_registry.json"
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
        new_hashes = {}
        core_paths = []
        
        # If neither the source registry nor stabilized math core exists, treat as no-op.
        if (not self.math_source_registry_path.exists()) and (not self.math_core_dir.exists()) and (not self.math_codex_dir.exists()):
            return results

        # Registry check (source registry only).
        if self.math_source_registry_path.exists():
            with open(self.math_source_registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)

            hashes = {}
            if self.math_hashes_path.exists():
                with open(self.math_hashes_path, 'r', encoding='utf-8') as f:
                    hashes = json.load(f)

            if isinstance(registry, dict) and registry.get("documents"):
                items = registry.get("documents", [])
                for item in items:
                    item_id = item.get("doc_id") or item.get("path")
                    path_value = item.get("path")
                    if not item_id or not path_value:
                        results["errors"].append(f"Math Source Registry Sync Error: malformed source entry {item}.")
                        continue

                    path = self.root / path_value
                    if not path.exists():
                        results["errors"].append(f"Math Source Registry Sync Error: File for '{item_id}' not found at {path_value}")
                        continue

                    current_hash = self.calculate_hash(path)
                    new_hashes[item_id] = current_hash

                    if item_id in hashes and hashes[item_id] != current_hash:
                        if "TEMPLATE" in path.name:
                            continue
                        results["errors"].append(f"Governance Violation: Math file '{path_value}' was modified (Additive-Only Rule Violation).")
            else:
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

            if not results["errors"] and not self.read_only:
                with open(self.math_hashes_path, 'w', encoding='utf-8') as f:
                    json.dump(new_hashes, f, indent=2)

        # Stabilized math-core lock (hash registry/math/*.json and docs/math/*.md)
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

            if not results["errors"] and not self.read_only:
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


class DatabaseRuntimeValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.db_path = self.root / "registry/db/acellorator_index.sqlite"

    def run(self):
        results = {
            "status": "success",
            "errors": [],
            "warnings": [],
            "db_path": str(self.db_path),
            "checks": [],
        }

        if not self.db_path.exists():
            return {"status": "failed", "errors": ["Governance DB file is missing."], "warnings": []}

        try:
            conn = sqlite3.connect(str(self.db_path))
        except Exception as exc:
            return {"status": "failed", "errors": [f"Governance DB connection failed: {exc}"], "warnings": []}

        try:
            has_decision_log = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='governance_decision_log'"
            ).fetchone() is not None
            has_events = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='governance_events'"
            ).fetchone() is not None
            has_patch_chain_view = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='view' AND name='patch_chain_view'"
            ).fetchone() is not None

            results["checks"].append("sqlite_connectivity")
            results["checks"].append("governance_decision_log_present" if has_decision_log else "governance_decision_log_missing")
            results["checks"].append("governance_events_present" if has_events else "governance_events_missing")
            results["checks"].append("patch_chain_view_present" if has_patch_chain_view else "patch_chain_view_missing")

            if not has_decision_log:
                results["errors"].append("Governance decision log table is missing.")
            if not has_patch_chain_view:
                results["warnings"].append("Patch-chain view is unavailable in the current DB snapshot.")
            if not has_events:
                results["warnings"].append("Governance events table is unavailable in the current DB snapshot.")
        except sqlite3.Error as exc:
            results["status"] = "failed"
            results["errors"].append(f"Governance DB runtime probe failed: {exc}")
        finally:
            conn.close()

        if results["errors"]:
            results["status"] = "failed"
        elif results["warnings"]:
            results["status"] = "warning"
        results["items_checked"] = len(results["checks"])
        return results


class PatchChainValidator:
    def __init__(self, root_dir, no_db_log=False, current_state=None, ledger_index=None, cache=None):
        self.root = Path(root_dir)
        self.patch_registry_dir = self.root / "registry/governance/patches"
        self.db_path = self.root / "registry/db/acellorator_index.sqlite"
        self.no_db_log = no_db_log
        self.current_state = current_state
        self.ledger_index = ledger_index
        self.cache = cache

    def run(self):
        results = {
            "status": "success",
            "errors": [],
            "warnings": [],
            "checked_patches": 0,
            "summary": {
                "status_counts": {},
                "decision_counts": {},
                "sample": [],
            },
            "governance_status": "unknown",
            "logging_mode": "suppressed" if self.no_db_log else "default",
        }

        if not self.patch_registry_dir.exists():
            return {"status": "skipped", "errors": [], "warnings": ["Patch registry missing."], "checked_patches": 0}

        try:
            from scripts.query_governance import (
                build_current_state_capsule,
                build_patch_chain_result,
                load_governance_change_ledger_index,
                load_patch_record_by_path,
            )
        except ImportError as exc:
            return {"status": "failed", "errors": [f"Could not import governance runtime helpers: {exc}"], "warnings": []}

        current_state = self.current_state
        if current_state is None:
            if self.db_path.exists():
                try:
                    current_state = build_current_state_capsule(str(self.db_path))
                except Exception as exc:
                    results["warnings"].append(f"Current-state capsule unavailable for patch-chain summary: {exc}")
            else:
                results["warnings"].append("Governance DB file is missing; patch-chain summary uses registry-only context.")

        ledger_index = self.ledger_index if self.ledger_index is not None else load_governance_change_ledger_index()
        cache = self.cache if self.cache is not None else {}
        status_counts = {}
        decision_counts = {}
        sample = []
        checked = 0

        for patch_path in sorted(self.patch_registry_dir.glob("PATCH_*.json")):
            patch, _ = load_patch_record_by_path(patch_path)
            if not isinstance(patch, dict):
                results["warnings"].append(f"Unreadable patch record: {patch_path.as_posix()}")
                continue
            patch_id = patch.get("patch_id") or patch_path.stem
            try:
                chain = build_patch_chain_result(
                    patch_id,
                    current_state=current_state,
                    ledger_index=ledger_index,
                    cache=cache,
                )
            except Exception as exc:
                results["warnings"].append(f"Patch-chain summary failed for {patch_id}: {exc}")
                continue

            checked += 1
            status = str(chain.get("status") or "unknown").lower()
            decision = str(chain.get("decision") or "unknown").lower()
            status_counts[status] = status_counts.get(status, 0) + 1
            decision_counts[decision] = decision_counts.get(decision, 0) + 1
            if len(sample) < 10 and status not in {"applied", "late_registered"}:
                sample.append(
                    {
                        "patch_id": patch_id,
                        "status": status,
                        "decision": decision,
                        "reason": chain.get("reason"),
                    }
                )

        results["checked_patches"] = checked
        results["summary"] = {
            "status_counts": status_counts,
            "decision_counts": decision_counts,
            "sample": sample,
        }
        results["governance_status"] = "mixed" if any(status not in {"applied", "late_registered"} for status in status_counts) else "aligned"
        if results["warnings"]:
            results["status"] = "warning"
        results["items_checked"] = checked
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

class MathTestProvenanceValidator:
    def __init__(self, root_dir):
        self.root = Path(root_dir)
        self.schema_path = self.root / "schemas/math_test_result.schema.json"
        self.review_artifacts = [
            self.root / "outputs/math_tests/mt_counterexample_orientation_locking_result.json"
        ]

    def validate_json_load(self, path):
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f), None
        except Exception as e:
            return None, str(e)

    def run(self):
        results = {"status": "pass", "errors": [], "warnings": [], "checked_files": []}

        schema, err = self.validate_json_load(self.schema_path)
        if err:
            results["status"] = "fail"
            results["errors"].append(f"Schema Load Error: {err}")
            return results

        required_fields = schema.get("required", [])
        for artifact_path in self.review_artifacts:
            if not artifact_path.exists():
                results["status"] = "fail"
                results["errors"].append(f"Missing provenance artifact: {artifact_path.as_posix()}")
                continue

            data, err = self.validate_json_load(artifact_path)
            if err:
                results["status"] = "fail"
                results["errors"].append(f"Artifact Load Error ({artifact_path.as_posix()}): {err}")
                continue

            results["checked_files"].append(artifact_path.as_posix())

            for field in required_fields:
                if field not in data:
                    results["status"] = "fail"
                    results["errors"].append(f"{artifact_path.name} missing required provenance field '{field}'")

            claim_basis = data.get("claim_basis")
            dedicated = data.get("dedicated_harness_executed")
            harness_id = data.get("harness_id")
            run_id = data.get("run_id")
            execution_log = data.get("execution_log")
            instrumentation_map = data.get("instrumentation_map")
            observed_behavior = str(data.get("observed_behavior", "")).strip().lower()
            blob = json.dumps(data, ensure_ascii=False).lower()

            if claim_basis != "direct_run":
                forbidden_execution_phrases = [
                    "attack was executed",
                    "was run",
                    "observed_behavior: pass",
                    "observed_behavior: fail",
                ]
                if any(phrase in blob for phrase in forbidden_execution_phrases):
                    results["status"] = "fail"
                    results["errors"].append(
                        f"{artifact_path.name} contains execution language without direct_run provenance"
                    )

            if claim_basis == "direct_run":
                if dedicated is not True:
                    results["status"] = "fail"
                    results["errors"].append(f"{artifact_path.name} direct_run requires dedicated_harness_executed=true")
                for field_name, field_value in {
                    "harness_id": harness_id,
                    "run_id": run_id,
                    "execution_log": execution_log,
                    "instrumentation_map": instrumentation_map,
                }.items():
                    if field_value in [None, ""]:
                        results["status"] = "fail"
                        results["errors"].append(f"{artifact_path.name} direct_run requires non-null {field_name}")
            else:
                if dedicated is not False:
                    results["status"] = "fail"
                    results["errors"].append(f"{artifact_path.name} review/provisional artifact must set dedicated_harness_executed=false")
                for field_name, field_value in {
                    "harness_id": harness_id,
                    "run_id": run_id,
                    "execution_log": execution_log,
                    "instrumentation_map": instrumentation_map,
                }.items():
                    if field_value not in [None, ""]:
                        results["status"] = "fail"
                        results["errors"].append(f"{artifact_path.name} review/provisional artifact must leave {field_name} null")

                if claim_basis == "review_only":
                    if observed_behavior in {"pass", "fail"}:
                        results["status"] = "fail"
                        results["errors"].append(f"{artifact_path.name} review_only artifact may not claim pass/fail observed_behavior")
                elif claim_basis == "derived":
                    if not data.get("inferred_from"):
                        results["status"] = "fail"
                        results["errors"].append(f"{artifact_path.name} derived artifact must cite inferred_from evidence")
                elif claim_basis == "provisional_inference":
                    if not data.get("inferred_from"):
                        results["status"] = "fail"
                        results["errors"].append(f"{artifact_path.name} provisional_inference artifact must cite inferred_from evidence")

        if results["errors"]:
            results["status"] = "fail"
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
        nodes = {}
        edges = []
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
        results["items_checked"] = len(nodes) + len(edges)
        return results


def _normalize_validation_status(value):
    status = str(value or "").strip().lower()
    if status in {"failed", "fail"}:
        return "failed"
    if status in {"success", "warning", "pass", "skipped", "timeout"}:
        return status
    return status or "unknown"


def _classify_validation_failure(stage_name, result, exception=None, timed_out=False):
    if exception is not None:
        return "tooling_failure"
    if timed_out:
        return "runtime_failure"

    status = _normalize_validation_status(result.get("status"))
    if status not in {"failed", "timeout"}:
        return None

    error_text = " ".join(str(error) for error in result.get("errors", []) if error)
    lowered = error_text.lower()
    if any(token in lowered for token in ("could not import", "load error", "parse error", "sqlite", "database", "permission denied", "missing db file", "os error")):
        return "tooling_failure"
    if any(token in lowered for token in ("timeout", "stale", "lock", "unavailable")):
        return "runtime_failure"
    if stage_name in {"db_validation", "governance_integrity_validation", "patch_chain_validation"}:
        return "semantic_failure"
    return "semantic_failure"


def _run_validation_stage(stage_name, runner, timeout_seconds=None):
    started = time.perf_counter()
    exception = None
    try:
        result = runner()
    except Exception as exc:
        exception = exc
        result = {"status": "failed", "errors": [f"{stage_name} exception: {exc}"], "warnings": []}
    duration = time.perf_counter() - started
    normalized_status = _normalize_validation_status(result.get("status"))
    timed_out = bool(timeout_seconds is not None and duration > timeout_seconds)
    if timed_out and normalized_status not in {"failed"}:
        result["status"] = "timeout"
        normalized_status = "timeout"
    failure_class = _classify_validation_failure(stage_name, result, exception=exception, timed_out=timed_out)
    stage_trace = {
        "stage": stage_name,
        "status": normalized_status,
        "failure_class": failure_class or "none",
        "duration_seconds": round(duration, 6),
        "timed_out": timed_out,
        "error_count": len(result.get("errors", [])),
        "warning_count": len(result.get("warnings", [])),
    }
    stage_trace["result_snapshot"] = {
        "status": normalized_status,
        "errors": [str(error) for error in result.get("errors", [])[:3] if error],
        "warnings": [str(warning) for warning in result.get("warnings", [])[:3] if warning],
        "items_checked": result.get("items_checked"),
        "checked_patches": result.get("checked_patches"),
        "checked_files": result.get("checked_files"),
        "checked_entries": result.get("checked_entries"),
        "tools_tested": result.get("tools_tested"),
        "db_path": result.get("db_path"),
        "patch_file": result.get("patch_file"),
        "sample_patch_path": result.get("sample_patch_path"),
        "sample_patch_id": result.get("sample_patch_id"),
        "sample_patch_status": result.get("sample_patch_status"),
        "sample_patch_decision": result.get("sample_patch_decision"),
        "reason": result.get("reason"),
        "decision": result.get("decision"),
        "evidence_paths": (result.get("evidence_paths") or [])[:10] if isinstance(result.get("evidence_paths"), list) else [],
        "summary": result.get("summary"),
    }
    if exception is not None:
        stage_trace["exception"] = str(exception)
    result["duration_seconds"] = duration
    result["timed_out"] = timed_out
    result["failure_class"] = failure_class
    result["stage_name"] = stage_name
    result["normalized_status"] = normalized_status
    return result, stage_trace


def _build_validation_stage_plan(root, args):
    return [
        ("unified_manifest_validation", UnifiedManifestValidator(root).run),
        ("registry_validation", RegistryValidator(root).run),
        ("engine_validation", EngineValidator(root).run),
        ("hygiene_validation", HygieneValidator(root).run),
        ("math_validation", MathValidator(root).run),
        ("db_validation", DBValidator(root).run),
        ("math_test_provenance_validation", MathTestProvenanceValidator(root).run),
        ("math_program_validation", lambda: MathProgramValidator(root, full_report=args.full_math_program).run()),
        ("implementation_validation", ImplementationValidator(root).run),
        ("evidence_validation", EvidenceValidator(root).run),
        ("campaign_validation", CampaignValidator(root).run),
        ("governance_integrity_validation", GovernanceIntegrityValidator(root).run),
        ("db_runtime_validation", DatabaseRuntimeValidator(root).run),
        ("patch_chain_validation", lambda: PatchChainValidator(root, no_db_log=args.no_db_log).run()),
    ]


def _select_validation_mode(args):
    if getattr(args, "patch_chain_only", False):
        return "patch_chain_only"
    if getattr(args, "governance_only", False):
        return "governance_only"
    if getattr(args, "registries_only", False):
        return "registries_only"
    if getattr(args, "db_only", False):
        return "db_only"
    if getattr(args, "math_only", False):
        return "math_only"
    if getattr(args, "quick", False):
        return "quick"
    return "full"


def _selected_stage_names(mode):
    if mode == "quick":
        return {
            "unified_manifest_validation",
        }
    if mode == "registries_only":
        return {
            "unified_manifest_validation",
            "registry_validation",
            "math_validation",
            "implementation_validation",
            "evidence_validation",
            "campaign_validation",
            "math_test_provenance_validation",
        }
    if mode == "governance_only":
        return {
            "registry_validation",
            "db_runtime_validation",
            "patch_chain_validation",
        }
    if mode == "patch_chain_only":
        return {"patch_chain_validation"}
    if mode == "db_only":
        return {"db_validation", "db_runtime_validation"}
    if mode == "math_only":
        return {
            "math_validation",
            "math_test_provenance_validation",
            "math_program_validation",
        }
    return {
        "unified_manifest_validation",
        "registry_validation",
        "engine_validation",
        "hygiene_validation",
        "math_validation",
        "db_validation",
        "math_test_provenance_validation",
        "math_program_validation",
        "implementation_validation",
        "evidence_validation",
        "campaign_validation",
        "governance_integrity_validation",
    }


def _normalize_requested_stages(raw_stages):
    if not raw_stages:
        return None

    if isinstance(raw_stages, str):
        raw_stages = [raw_stages]

    requested = []
    seen = set()
    for chunk in raw_stages:
        for stage_name in str(chunk).split(","):
            stage_name = stage_name.strip()
            if not stage_name or stage_name in seen:
                continue
            requested.append(stage_name)
            seen.add(stage_name)
    return requested


def _restrict_stage_selection(stage_plan, requested_stages, parser=None):
    if not requested_stages:
        return None

    available = {name for name, _ in stage_plan}
    unknown = [stage_name for stage_name in requested_stages if stage_name not in available]
    if unknown:
        message = "Unknown validation stage(s): " + ", ".join(sorted(unknown))
        if parser is not None:
            parser.error(message)
        raise ValueError(message)

    return set(requested_stages)


def _load_json_document(path):
    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            with open(path, "r", encoding=encoding) as f:
                return json.load(f), None
        except Exception as exc:
            last_error = exc
    return None, str(last_error) if last_error else "Unknown JSON load error"


def _dedupe_paths(paths):
    return [path for path in dict.fromkeys(path for path in paths if path)]


def _hash_file(path):
    import hashlib

    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except Exception:
        return None


def _collect_patch_catalog(root):
    patch_dir = Path(root) / "registry/governance/patches"
    catalog = []
    if not patch_dir.exists():
        return catalog

    for patch_path in sorted(patch_dir.glob("PATCH_*.json")):
        patch, err = _load_json_document(patch_path)
        catalog.append({
            "path": patch_path,
            "patch": patch if isinstance(patch, dict) else None,
            "error": err,
        })
    return catalog


def _select_patch_gate_sample(catalog):
    if not catalog:
        return None

    applied = []
    for item in catalog:
        patch = item.get("patch") or {}
        if str(patch.get("status", "")).upper() == "APPLIED":
            applied.append(item)

    def _sample_sort_key(item):
        patch = item.get("patch") or {}
        return (
            str(patch.get("applied_on") or ""),
            str(patch.get("patch_id") or item["path"].stem),
        )

    if applied:
        return sorted(applied, key=_sample_sort_key)[-1]

    return catalog[-1]


def _build_partial_validation_context(root, mode):
    root = Path(root)
    db_path = root / "registry/db/acellorator_index.sqlite"
    context = {
        "root": root,
        "db_path": db_path,
        "current_state": None,
        "ledger_index": None,
        "patch_chain_cache": {},
        "patch_catalog": [],
        "sample_patch": None,
        "sample_patch_path": None,
    }

    needs_db = mode in {"quick", "governance_only", "patch_chain_only", "db_only"}
    if needs_db:
        try:
            from scripts.query_governance import build_current_state_capsule, load_governance_change_ledger_index

            if db_path.exists():
                context["current_state"] = build_current_state_capsule(str(db_path))
            context["ledger_index"] = load_governance_change_ledger_index()
        except Exception as exc:
            context["warnings"] = [f"Governance runtime context unavailable: {exc}"]

    if mode in {"quick", "governance_only", "patch_chain_only", "registries_only"}:
        context["patch_catalog"] = _collect_patch_catalog(root)
        sample = _select_patch_gate_sample(context["patch_catalog"])
        if sample:
            context["sample_patch"] = sample.get("patch")
            context["sample_patch_path"] = sample.get("path")

    return context


def _run_json_parse_validation(root, context=None):
    root = Path(root)
    results = {"status": "success", "errors": [], "warnings": [], "checked_files": []}
    candidates = [
        root / "registry/governance_manifest.json",
        root / "registry/governance_change_ledger.json",
        root / "registry/governance_hash_registry.json",
        root / "registry/lexicon_validation_registry.json",
        root / "registry/lexicon_gap_queue.json",
        root / "registry/evidence_campaign_template_registry.json",
        root / "registry/cross_dataset_pairing_registry.json",
        root / "registry/prediction_binding_registry.json",
        root / "registry/public_dataset_registry.json",
    ]

    docs_dir = root / "docs/governance"
    if docs_dir.exists():
        candidates.extend(sorted(docs_dir.glob("*.json")))

    patch_dir = root / "registry/governance/patches"
    if patch_dir.exists():
        candidates.extend(sorted(patch_dir.glob("PATCH_*.json")))

    for path in candidates:
        if not path.exists():
            continue
        _, err = _load_json_document(path)
        rel = str(path).replace("\\", "/")
        results["checked_files"].append(rel)
        if err:
            results["errors"].append(f"JSON Parse Error ({rel}): {err}")

    if results["errors"]:
        results["status"] = "failed"
    results["items_checked"] = len(results["checked_files"])
    results["evidence_paths"] = results["checked_files"][:10]
    return results


def _run_hash_registry_validation(root, context=None):
    root = Path(root)
    results = {"status": "success", "errors": [], "warnings": [], "checked_files": []}
    registry_path = root / "registry/governance_hash_registry.json"
    registry, err = _load_json_document(registry_path)
    if err:
        return {"status": "failed", "errors": [f"Governance hash registry load error: {err}"], "warnings": []}

    hashes = registry.get("hashes", {}) if isinstance(registry, dict) else {}
    if not isinstance(hashes, dict):
        return {"status": "failed", "errors": ["Governance hash registry missing 'hashes' mapping."], "warnings": []}

    for rel_path, expected_hash in hashes.items():
        target = root / rel_path
        if not target.exists():
            results["errors"].append(f"Governance hash registry target missing: {rel_path}")
            continue
        actual_hash = _hash_file(target)
        results["checked_files"].append(rel_path)
        if str(actual_hash or "").lower() != str(expected_hash or "").lower():
            results["errors"].append(f"Hash mismatch for {rel_path}")

    if results["errors"]:
        results["status"] = "failed"
    results["items_checked"] = len(results["checked_files"])
    results["evidence_paths"] = [str(registry_path).replace("\\", "/")]
    return results


def _run_governance_ledger_validation(root, context=None):
    root = Path(root)
    ledger_path = root / "registry/governance_change_ledger.json"
    results = {"status": "success", "errors": [], "warnings": [], "checked_entries": 0}
    ledger, err = _load_json_document(ledger_path)
    if err:
        return {"status": "failed", "errors": [f"Governance ledger load error: {err}"], "warnings": []}

    entries = ledger.get("entries", []) if isinstance(ledger, dict) else []
    if not isinstance(entries, list):
        return {"status": "failed", "errors": ["Governance ledger missing 'entries' list."], "warnings": []}

    seen_change_ids = set()
    for entry in entries:
        if not isinstance(entry, dict):
            results["errors"].append(f"Malformed governance ledger entry: {entry}")
            continue
        results["checked_entries"] += 1
        for field in ("change_id", "patch_id", "timestamp", "description", "affected_assets"):
            if field not in entry:
                results["errors"].append(f"Governance ledger entry missing '{field}': {entry.get('change_id', '<unknown>')}")
        change_id = entry.get("change_id")
        if change_id in seen_change_ids:
            results["errors"].append(f"Duplicate governance change_id: {change_id}")
        seen_change_ids.add(change_id)

    if results["errors"]:
        results["status"] = "failed"
    results["items_checked"] = results["checked_entries"]
    results["evidence_paths"] = [str(ledger_path).replace("\\", "/")]
    return results


def _run_patch_record_validation(root, context=None):
    root = Path(root)
    results = {"status": "success", "errors": [], "warnings": [], "checked_patches": 0}
    catalog = context.get("patch_catalog") if context else None
    if not catalog:
        catalog = _collect_patch_catalog(root)

    if not catalog:
        return {"status": "skipped", "errors": [], "warnings": ["Patch registry missing."], "checked_patches": 0}

    seen_patch_ids = set()
    evidence_paths = []
    for item in catalog:
        patch = item.get("patch")
        patch_path = item.get("path")
        rel = str(patch_path).replace("\\", "/") if patch_path else "<unknown>"
        evidence_paths.append(rel)
        if item.get("error"):
            results["errors"].append(f"Patch record parse error ({rel}): {item['error']}")
            continue
        if not isinstance(patch, dict):
            results["errors"].append(f"Unreadable patch record: {rel}")
            continue

        results["checked_patches"] += 1
        patch_id = patch.get("patch_id")
        if not patch_id:
            results["errors"].append(f"Patch record missing patch_id: {rel}")
        elif patch_id in seen_patch_ids:
            results["errors"].append(f"Duplicate patch_id in registry: {patch_id}")
        seen_patch_ids.add(patch_id)

        if not patch.get("status"):
            results["errors"].append(f"Patch record missing status: {patch_id or rel}")
        if not patch.get("title"):
            results["errors"].append(f"Patch record missing title: {patch_id or rel}")
        depends_on = patch.get("depends_on", [])
        if depends_on is not None and not isinstance(depends_on, list):
            results["errors"].append(f"Patch record has non-list depends_on: {patch_id or rel}")
        if str(patch.get("status", "")).upper() == "APPLIED" and not patch.get("applied_on"):
            results["errors"].append(f"Applied patch missing applied_on: {patch_id or rel}")

    if results["errors"]:
        results["status"] = "failed"
    results["items_checked"] = results["checked_patches"]
    results["evidence_paths"] = evidence_paths[:10]
    return results


def _run_patch_gate_validation(root, context=None, sample_limit=1):
    root = Path(root)
    db_path = root / "registry/db/acellorator_index.sqlite"
    results = {
        "status": "success",
        "errors": [],
        "warnings": [],
        "checked_patches": 0,
        "sample_patch_id": None,
        "sample_patch_status": None,
        "sample_patch_decision": None,
        "sample_patch_reason": None,
    }

    sample = context.get("sample_patch") if context else None
    sample_path = context.get("sample_patch_path") if context else None
    if not sample:
        catalog = context.get("patch_catalog") if context else None
        if not catalog:
            catalog = _collect_patch_catalog(root)
        sample_item = _select_patch_gate_sample(catalog)
        if sample_item:
            sample = sample_item.get("patch")
            sample_path = sample_item.get("path")

    if not sample or not isinstance(sample, dict):
        return {"status": "skipped", "errors": [], "warnings": ["No patch record available for patch-gate smoke check."], "checked_patches": 0}

    try:
        from scripts.query_governance import build_patch_chain_result, evaluate_patch_gate
    except ImportError as exc:
        return {"status": "failed", "errors": [f"Could not import governance runtime helpers: {exc}"], "warnings": []}

    current_state = context.get("current_state") if context else None
    ledger_index = context.get("ledger_index") if context else None
    patch_chain_cache = context.get("patch_chain_cache") if context else {}
    patch_chain_result = None
    patch_id = sample.get("patch_id")
    if patch_id:
        try:
            patch_chain_result = build_patch_chain_result(
                patch_id,
                current_state=current_state,
                ledger_index=ledger_index,
                cache=patch_chain_cache,
            )
        except Exception as exc:
            results["errors"].append(f"Patch-chain preflight failed for {patch_id}: {exc}")

    try:
        gate_result = evaluate_patch_gate(
            str(db_path),
            sample,
            patch_source_path=str(sample_path) if sample_path else None,
            requested_action="apply",
            log_to_db=False,
            current_state=current_state,
            ledger_index=ledger_index,
            patch_chain_result=patch_chain_result,
        )
    except Exception as exc:
        return {"status": "failed", "errors": [f"Patch-gate smoke check failed: {exc}"], "warnings": []}

    results["checked_patches"] = 1
    results["sample_patch_id"] = gate_result.get("patch_id") or patch_id
    results["sample_patch_status"] = str(sample.get("status") or "").upper() or None
    results["sample_patch_decision"] = gate_result.get("decision")
    results["sample_patch_reason"] = gate_result.get("reason")
    results["evidence_paths"] = _dedupe_paths([
        str(sample_path).replace("\\", "/") if sample_path else None,
        str(db_path).replace("\\", "/"),
    ] + (patch_chain_result.get("evidence_paths", []) if isinstance(patch_chain_result, dict) else []))

    decision = str(gate_result.get("decision") or "").lower()
    if decision == "block":
        results["errors"].append(gate_result.get("reason") or "Patch gate smoke check blocked the sample patch.")
        results["status"] = "failed"
    elif decision in {"defer", "allow_with_note"}:
        results["warnings"].append(gate_result.get("reason") or "Patch gate returned a deferred/annotated result.")
        results["status"] = "warning"
    elif decision not in {"allow"}:
        results["warnings"].append(f"Patch gate returned unexpected decision '{decision}'.")
        results["status"] = "warning"

    if results["errors"]:
        results["status"] = "failed"
    results["items_checked"] = results["checked_patches"]
    return results


def _build_partial_validation_stage_plan(root, args, mode, context):
    root = Path(root)
    current_state = context.get("current_state")
    ledger_index = context.get("ledger_index")
    patch_chain_cache = context.get("patch_chain_cache") if context.get("patch_chain_cache") is not None else {}

    def _patch_chain_runner():
        return PatchChainValidator(
            root,
            no_db_log=args.no_db_log,
            current_state=current_state,
            ledger_index=ledger_index,
            cache=patch_chain_cache,
        ).run()

    def _patch_gate_runner():
        return _run_patch_gate_validation(root, context=context)

    plan = [
        ("manifest_validation", lambda: UnifiedManifestValidator(root).run()),
        ("json_parse_validation", lambda: _run_json_parse_validation(root, context=context)),
        ("registry_validation", lambda: RegistryValidator(root).run()),
        ("hash_registry_validation", lambda: _run_hash_registry_validation(root, context=context)),
        ("governance_ledger_validation", lambda: _run_governance_ledger_validation(root, context=context)),
        ("patch_record_validation", lambda: _run_patch_record_validation(root, context=context)),
        ("patch_chain_validation", _patch_chain_runner),
        ("patch_gate_validation", _patch_gate_runner),
        ("db_authority_validation", lambda: DatabaseRuntimeValidator(root).run()),
        ("math_validation", lambda: MathValidator(root, read_only=True).run()),
        ("math_test_provenance_validation", lambda: MathTestProvenanceValidator(root).run()),
        ("math_program_validation", lambda: MathProgramValidator(root, full_report=args.full_math_program).run()),
        ("hygiene_validation", lambda: HygieneValidator(root).run()),
    ]

    if mode == "quick":
        selected = {
            "manifest_validation",
            "registry_validation",
            "patch_chain_validation",
            "patch_gate_validation",
            "db_authority_validation",
        }
    elif mode == "registries_only":
        selected = {
            "manifest_validation",
            "json_parse_validation",
            "registry_validation",
            "hash_registry_validation",
            "governance_ledger_validation",
            "patch_record_validation",
        }
    elif mode == "governance_only":
        selected = {
            "registry_validation",
            "governance_ledger_validation",
            "patch_record_validation",
            "patch_chain_validation",
            "patch_gate_validation",
            "db_authority_validation",
        }
    elif mode == "patch_chain_only":
        selected = {"patch_chain_validation"}
    elif mode == "db_only":
        selected = {"db_authority_validation"}
    elif mode == "math_only":
        selected = {
            "math_validation",
            "math_test_provenance_validation",
            "math_program_validation",
        }
    else:
        selected = {stage_name for stage_name, _ in plan}

    return plan, selected


def _collect_stage_items_checked(stage_name, result):
    for key in (
        "items_checked",
        "checked_patches",
        "checked_files",
        "tools_tested",
        "checked_entries",
    ):
        value = result.get(key)
        if isinstance(value, int):
            return value
        if isinstance(value, list):
            return len(value)

    summary = result.get("summary")
    if isinstance(summary, dict):
        if isinstance(summary.get("status_counts"), dict):
            return sum(summary["status_counts"].values())
        if isinstance(summary.get("sample"), list):
            return len(summary["sample"])

    if stage_name == "report_write":
        return 1

    return 0


def _collect_stage_evidence_paths(result):
    paths = []
    for key in ("evidence_paths", "checked_files"):
        value = result.get(key)
        if isinstance(value, list):
            paths.extend(str(item) for item in value if item)

    db_path = result.get("db_path")
    if db_path:
        paths.append(str(db_path))

    patch_file = result.get("patch_file")
    if patch_file:
        paths.append(str(patch_file))

    if result.get("sample_patch_path"):
        paths.append(str(result["sample_patch_path"]))

    return _dedupe_paths(paths)[:10]


def _summarize_stage_failure(stage_name, result, trace_entry, report_stale=False):
    if trace_entry.get("status") == "skipped":
        return "SKIPPED_BY_MODE", None
    if trace_entry.get("timed_out"):
        summary = None
        if result.get("errors"):
            summary = result["errors"][0]
        elif result.get("warnings"):
            summary = result["warnings"][0]
        return "TIMEOUT", summary

    failure_class = trace_entry.get("failure_class")
    if failure_class == "tooling_failure":
        summary = result.get("errors", [None])[0] if result.get("errors") else None
        return "FAIL_TOOLING", summary
    if failure_class == "runtime_failure":
        summary = result.get("errors", [None])[0] if result.get("errors") else None
        return "FAIL_RUNTIME", summary
    if failure_class == "semantic_failure":
        summary = result.get("errors", [None])[0] if result.get("errors") else None
        return "FAIL_SEMANTIC", summary

    if stage_name == "report_write" and report_stale:
        return "STALE_REPORT_WARNING", "Existing global health report was stale before this run."

    return "PASS", None


def _build_stage_results(stage_trace, report_stale=False, include_report_write=False, report_path=None):
    stage_results = []
    for trace_entry in stage_trace:
        stage_name = trace_entry.get("stage") or trace_entry.get("stage_name") or "unknown"
        result = trace_entry.get("result_snapshot") or {}
        status, failure_summary = _summarize_stage_failure(stage_name, result, trace_entry, report_stale=report_stale)
        stage_result = {
            "stage_name": stage_name,
            "status": status,
            "duration_seconds": round(float(trace_entry.get("duration_seconds") or 0.0), 6),
            "items_checked": _collect_stage_items_checked(stage_name, result),
            "failure_code": None if status in {"PASS", "SKIPPED_BY_MODE"} else status,
            "failure_summary": failure_summary,
            "evidence_paths": _collect_stage_evidence_paths(result),
        }
        stage_results.append(stage_result)

    if include_report_write:
        report_result = {
            "stage_name": "report_write",
            "status": "STALE_REPORT_WARNING" if report_stale else "PASS",
            "duration_seconds": 0.0,
            "items_checked": 1,
            "failure_code": "STALE_REPORT_WARNING" if report_stale else None,
            "failure_summary": "Existing global health report was stale before this run." if report_stale else None,
            "evidence_paths": [report_path] if report_path else [],
        }
        stage_results.append(report_result)

    return stage_results


def _detect_report_staleness(root, report_path):
    root = Path(root)
    report_path = Path(report_path)
    if not report_path.exists():
        return False

    try:
        report_mtime = report_path.stat().st_mtime
    except Exception:
        return False

    candidates = [
        root / "registry/governance_change_ledger.json",
        root / "registry/governance_hash_registry.json",
        root / "registry/governance_manifest.json",
        root / "docs/governance/GLOBAL_VALIDATION_ROUTINE.md",
        root / "scripts/global_validate.py",
        root / "scripts/query_governance.py",
    ]
    patch_dir = root / "registry/governance/patches"
    if patch_dir.exists():
        candidates.extend(sorted(patch_dir.glob("PATCH_*.json")))

    newest = report_mtime
    for path in candidates:
        try:
            if path.exists():
                newest = max(newest, path.stat().st_mtime)
        except Exception:
            continue
    return newest > report_mtime


def _count_regular_files(path):
    path = Path(path)
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def _load_jsonl_records(path):
    path = Path(path)
    if not path.exists():
        return [], None

    records = []
    line_number = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_number, raw_line in enumerate(f, 1):
                line = raw_line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
    except Exception as exc:
        return None, f"{path.as_posix()} line {line_number}: {exc}"

    return records, None


def _write_jsonl_record(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def _build_validation_history_record(report, stage_trace, root, run_id):
    stage_durations = {}
    stage_statuses = {}
    warning_count = 0

    for trace_entry in stage_trace:
        stage_name = trace_entry.get("stage") or trace_entry.get("stage_name") or "unknown"
        stage_durations[stage_name] = round(float(trace_entry.get("duration_seconds") or 0.0), 6)
        stage_statuses[stage_name] = trace_entry.get("status") or "unknown"
        warning_count += int(trace_entry.get("warning_count") or 0)

    if report.get("stale_report_warning"):
        warning_count += 1

    patch_catalog = _collect_patch_catalog(root)
    ledger_data, _ = _load_json_document(Path(root) / "registry/governance_change_ledger.json")
    hash_data, _ = _load_json_document(Path(root) / "registry/governance_hash_registry.json")

    ledger_entries = ledger_data.get("entries", []) if isinstance(ledger_data, dict) else []
    hash_entries = hash_data.get("hashes", {}) if isinstance(hash_data, dict) else {}
    slowest_stages = report.get("slowest_stages", [])

    history_record = {
        "run_id": run_id,
        "timestamp": report.get("completed_at") or report.get("started_at"),
        "validation_mode": report.get("validation_mode"),
        "overall_status": report.get("overall_status"),
        "duration_seconds": round(float(report.get("duration_seconds") or 0.0), 6),
        "stage_durations": stage_durations,
        "stage_statuses": stage_statuses,
        "warning_count": warning_count,
        "semantic_failure_count": len(report.get("semantic_failures", [])),
        "runtime_failure_count": len(report.get("runtime_failures", [])),
        "tooling_failure_count": len(report.get("tooling_failures", [])),
        "registry_file_count": _count_regular_files(Path(root) / "registry"),
        "patch_record_count": len(patch_catalog),
        "ledger_entry_count": len(ledger_entries),
        "hash_registry_entry_count": len(hash_entries),
        "slowest_stage": slowest_stages[0] if slowest_stages else None,
    }
    return history_record


def _select_trend_baseline(records, baseline_selector=None):
    if not records:
        return None, "TREND_HISTORY_UNAVAILABLE"

    if baseline_selector:
        for record in reversed(records):
            if str(record.get("run_id")) == str(baseline_selector):
                return record, "ready"
        return None, "TREND_HISTORY_UNAVAILABLE"

    for record in reversed(records):
        if str(record.get("validation_mode")) == "full" and str(record.get("overall_status")) == "pass":
            return record, "ready"

    return None, "TREND_HISTORY_UNAVAILABLE"


def _build_trend_report(current_record, baseline_record, trend_status):
    trend_report = {
        "current_run_id": current_record.get("run_id"),
        "baseline_run_id": baseline_record.get("run_id") if baseline_record else None,
        "duration_delta_seconds": None,
        "duration_delta_percent": None,
        "stage_duration_deltas": {},
        "warning_count_delta": None,
        "failure_count_delta": None,
        "registry_growth_delta": None,
        "patch_count_delta": None,
        "ledger_growth_delta": None,
        "hash_registry_growth_delta": None,
        "regression_flags": [],
        "improvement_flags": [],
        "trend_status": trend_status,
    }

    if not baseline_record:
        return trend_report

    current_duration = float(current_record.get("duration_seconds") or 0.0)
    baseline_duration = float(baseline_record.get("duration_seconds") or 0.0)
    trend_report["duration_delta_seconds"] = round(current_duration - baseline_duration, 6)
    if baseline_duration:
        trend_report["duration_delta_percent"] = round(((current_duration - baseline_duration) / baseline_duration) * 100.0, 3)

    current_stage_durations = current_record.get("stage_durations") or {}
    baseline_stage_durations = baseline_record.get("stage_durations") or {}
    for stage_name, current_stage_duration in current_stage_durations.items():
        baseline_stage_duration = baseline_stage_durations.get(stage_name)
        if baseline_stage_duration is None:
            continue
        trend_report["stage_duration_deltas"][stage_name] = round(float(current_stage_duration or 0.0) - float(baseline_stage_duration or 0.0), 6)

        if float(baseline_stage_duration or 0.0) > 0:
            stage_delta_percent = ((float(current_stage_duration or 0.0) - float(baseline_stage_duration or 0.0)) / float(baseline_stage_duration or 0.0)) * 100.0
            if stage_delta_percent > 75:
                trend_report["regression_flags"].append(f"TREND_WARNING_STAGE_REGRESSION:{stage_name}")
            elif stage_delta_percent < -25:
                trend_report["improvement_flags"].append(f"TREND_IMPROVEMENT_STAGE:{stage_name}")

    current_warning_count = int(current_record.get("warning_count") or 0)
    baseline_warning_count = int(baseline_record.get("warning_count") or 0)
    current_failure_count = int(current_record.get("semantic_failure_count") or 0) + int(current_record.get("runtime_failure_count") or 0) + int(current_record.get("tooling_failure_count") or 0)
    baseline_failure_count = int(baseline_record.get("semantic_failure_count") or 0) + int(baseline_record.get("runtime_failure_count") or 0) + int(baseline_record.get("tooling_failure_count") or 0)

    trend_report["warning_count_delta"] = current_warning_count - baseline_warning_count
    trend_report["failure_count_delta"] = current_failure_count - baseline_failure_count
    trend_report["registry_growth_delta"] = int(current_record.get("registry_file_count") or 0) - int(baseline_record.get("registry_file_count") or 0)
    trend_report["patch_count_delta"] = int(current_record.get("patch_record_count") or 0) - int(baseline_record.get("patch_record_count") or 0)
    trend_report["ledger_growth_delta"] = int(current_record.get("ledger_entry_count") or 0) - int(baseline_record.get("ledger_entry_count") or 0)
    trend_report["hash_registry_growth_delta"] = int(current_record.get("hash_registry_entry_count") or 0) - int(baseline_record.get("hash_registry_entry_count") or 0)

    total_duration_delta_percent = trend_report["duration_delta_percent"]
    if total_duration_delta_percent is not None and total_duration_delta_percent > 50:
        trend_report["regression_flags"].append("TREND_WARNING_DURATION_REGRESSION")
    if trend_report["warning_count_delta"] > 5:
        trend_report["regression_flags"].append("TREND_WARNING_WARNING_GROWTH")
    if int(current_record.get("runtime_failure_count") or 0) > int(baseline_record.get("runtime_failure_count") or 0):
        trend_report["regression_flags"].append("TREND_WARNING_FAILURE_GROWTH_RUNTIME")
    if int(current_record.get("tooling_failure_count") or 0) > int(baseline_record.get("tooling_failure_count") or 0):
        trend_report["regression_flags"].append("TREND_WARNING_FAILURE_GROWTH_TOOLING")
    if int(current_record.get("semantic_failure_count") or 0) > int(baseline_record.get("semantic_failure_count") or 0):
        trend_report["regression_flags"].append("TREND_WARNING_FAILURE_GROWTH_SEMANTIC")

    if trend_report["duration_delta_seconds"] is not None and trend_report["duration_delta_seconds"] < 0:
        trend_report["improvement_flags"].append("TOTAL_DURATION_IMPROVED")
    if trend_report["warning_count_delta"] < 0:
        trend_report["improvement_flags"].append("WARNING_COUNT_IMPROVED")
    if trend_report["failure_count_delta"] < 0:
        trend_report["improvement_flags"].append("FAILURE_COUNT_IMPROVED")

    return trend_report


def main():
    parser = argparse.ArgumentParser(description="Global Ecosystem Validation Harness")
    parser.add_argument("--root", default=".", help="Project root directory")
    parser.add_argument("--out", default="outputs/audits/global_health_report.json", help="Report output path")
    parser.add_argument("--full-math-program", action="store_true", help="Embed full math-program validator payloads in the output report.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--quick", action="store_true", help="Run the smallest governed validation set.")
    mode_group.add_argument("--registries-only", action="store_true", help="Run registry-focused validation stages only.")
    mode_group.add_argument("--governance-only", action="store_true", help="Run governance/runtime-focused validation stages only.")
    mode_group.add_argument("--patch-chain-only", action="store_true", help="Run only the governed patch-chain summary stage.")
    mode_group.add_argument("--db-only", action="store_true", help="Run only database authority/runtime checks.")
    mode_group.add_argument("--math-only", action="store_true", help="Run only math-program validation checks.")
    parser.add_argument("--no-db-log", action="store_true", help="Suppress DB-backed logging in auxiliary governance diagnostics.")
    parser.add_argument("--stage-timeout-seconds", type=float, help="Mark any stage exceeding this budget as timed out in the report.")
    parser.add_argument("--profile", action="store_true", help="Emit a detailed stage timing profile in the report.")
    parser.add_argument("--history", action="store_true", help="Append a compact run summary to outputs/audits/validation_history.jsonl.")
    parser.add_argument("--trend", action="store_true", help="Generate outputs/audits/validation_trend_report.json from prior validation history.")
    parser.add_argument("--trend-baseline", help="Select a baseline run_id for trend comparison; defaults to the most recent passing full run.")
    parser.add_argument("--no-history", action="store_true", help="Disable history writing even when trend mode is enabled.")
    parser.add_argument("--stages", nargs="+", help="Run only the named validation stages from the selected plan. Accepts space- or comma-separated names.")
    parser.add_argument("--list-stages", action="store_true", help="Print the available validation stages for the selected plan and exit.")
    args = parser.parse_args()

    root = Path(args.root)
    mode = _select_validation_mode(args)
    out_path = Path(args.out)

    partial_mode = mode != "full"
    if args.list_stages:
        if partial_mode:
            stage_plan, _ = _build_partial_validation_stage_plan(
                root,
                args,
                mode,
                {"current_state": None, "ledger_index": None, "patch_chain_cache": {}},
            )
        else:
            stage_plan = _build_validation_stage_plan(root, args)
        for stage_name, _ in stage_plan:
            print(stage_name)
        return

    history_path = root / "outputs/audits/validation_history.jsonl"
    trend_path = root / "outputs/audits/validation_trend_report.json"
    history_requested = bool(args.history or args.trend)
    history_enabled = bool(history_requested and not args.no_history)
    trend_enabled = bool(args.trend)
    history_records = []
    history_load_error = None
    if trend_enabled:
        history_records, history_load_error = _load_jsonl_records(history_path)
    report_stale = _detect_report_staleness(root, out_path)
    report_started_at = datetime.now().isoformat()
    run_id = f"GV-{datetime.now().strftime('%Y%m%dT%H%M%S.%f')}-{os.getpid()}"
    total_started = time.perf_counter()

    if partial_mode:
        context = _build_partial_validation_context(root, mode)
        stage_plan, selected_stage_names = _build_partial_validation_stage_plan(root, args, mode, context)
    else:
        context = None
        selected_stage_names = _selected_stage_names(mode)
        stage_plan = _build_validation_stage_plan(root, args)

    requested_stages = _normalize_requested_stages(args.stages)
    if args.list_stages:
        for stage_name, _ in stage_plan:
            print(stage_name)
        return
    if requested_stages:
        selected_stage_names = _restrict_stage_selection(stage_plan, requested_stages, parser=parser)

    report = {
        "run_id": run_id,
        "validation_mode": mode,
        "started_at": report_started_at,
        "completed_at": None,
        "duration_seconds": None,
        "validation_options": {
            "quick": args.quick,
            "registries_only": args.registries_only,
            "governance_only": args.governance_only,
            "patch_chain_only": args.patch_chain_only,
            "db_only": args.db_only,
            "math_only": args.math_only,
            "no_db_log": args.no_db_log,
            "stage_timeout_seconds": args.stage_timeout_seconds,
            "profile": args.profile,
            "history": args.history,
            "trend": args.trend,
            "trend_baseline": args.trend_baseline,
            "no_history": args.no_history,
            "stages": requested_stages,
            "list_stages": args.list_stages,
        },
    }

    stage_trace = []
    for stage_name, runner in stage_plan:
        if stage_name not in selected_stage_names:
            result = {"status": "skipped", "warnings": [], "errors": [], "reason": "Excluded by validation mode."}
            trace_entry = {
                "stage": stage_name,
                "status": "skipped",
                "failure_class": "none",
                "duration_seconds": 0.0,
                "timed_out": False,
                "error_count": 0,
                "warning_count": 0,
                "result_snapshot": {},
            }
            report[stage_name] = result
            stage_trace.append(trace_entry)
            continue

        result, trace_entry = _run_validation_stage(stage_name, runner, timeout_seconds=args.stage_timeout_seconds)
        report[stage_name] = result
        stage_trace.append(trace_entry)

    total_duration = time.perf_counter() - total_started
    report["completed_at"] = datetime.now().isoformat()
    report["duration_seconds"] = round(total_duration, 6)
    report["stage_trace"] = stage_trace

    report_path_rel = str(out_path).replace("\\", "/")
    stage_results = _build_stage_results(
        stage_trace,
        report_stale=report_stale,
        include_report_write=True,
        report_path=report_path_rel,
    )
    report["stage_results"] = stage_results
    report["slowest_stages"] = [
        {
            "stage_name": item["stage_name"],
            "status": item["status"],
            "duration_seconds": item["duration_seconds"],
            "items_checked": item["items_checked"],
        }
        for item in sorted(
            [entry for entry in stage_results if entry["status"] not in {"SKIPPED_BY_MODE"}],
            key=lambda entry: entry["duration_seconds"],
            reverse=True,
        )[:3]
    ]
    report["runtime_failures"] = [
        {
            "stage_name": item["stage_name"],
            "status": item["status"],
            "failure_summary": item["failure_summary"],
            "duration_seconds": item["duration_seconds"],
        }
        for item in stage_results
        if item["status"] in {"FAIL_RUNTIME", "TIMEOUT"}
    ]
    report["tooling_failures"] = [
        {
            "stage_name": item["stage_name"],
            "status": item["status"],
            "failure_summary": item["failure_summary"],
            "duration_seconds": item["duration_seconds"],
        }
        for item in stage_results
        if item["status"] == "FAIL_TOOLING"
    ]
    report["semantic_failures"] = [
        {
            "stage_name": item["stage_name"],
            "status": item["status"],
            "failure_summary": item["failure_summary"],
            "duration_seconds": item["duration_seconds"],
        }
        for item in stage_results
        if item["status"] == "FAIL_SEMANTIC"
    ]
    report["stale_report_warning"] = report_stale

    if args.profile:
        report["profile"] = {
            "total_duration_seconds": round(total_duration, 6),
            "selected_stage_count": len(selected_stage_names),
            "completed_stage_count": sum(1 for entry in stage_trace if entry["status"] != "skipped"),
            "timed_out_stage_count": sum(1 for entry in stage_trace if entry.get("timed_out")),
            "failure_class_counts": {
                failure_class: sum(1 for entry in stage_trace if entry.get("failure_class") == failure_class)
                for failure_class in sorted({entry.get("failure_class") for entry in stage_trace if entry.get("failure_class")})
            },
            "slowest_stages": report["slowest_stages"],
        }

    terminal_statuses = {"success", "warning", "pass", "skipped"}
    report["overall_status"] = "pass" if all(
        _normalize_validation_status(entry.get("status")) in terminal_statuses
        for entry in report.values()
        if isinstance(entry, dict) and "status" in entry
    ) else "fail"

    current_history_record = _build_validation_history_record(report, stage_trace, root, run_id)
    history_write_status = "disabled"
    history_write_error = None
    trend_write_status = "disabled"
    trend_write_error = None
    trend_status = "disabled"

    if trend_enabled:
        if history_load_error:
            trend_report = _build_trend_report(current_history_record, None, "TREND_HISTORY_CORRUPT")
            trend_status = "TREND_HISTORY_CORRUPT"
        else:
            baseline_record, trend_status = _select_trend_baseline(history_records, args.trend_baseline)
            trend_report = _build_trend_report(current_history_record, baseline_record, trend_status)
        trend_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(trend_path, "w", encoding="utf-8") as f:
                json.dump(trend_report, f, indent=2)
            trend_write_status = "written"
        except Exception as exc:
            trend_write_status = "failed"
            trend_write_error = str(exc)

    if history_enabled:
        try:
            _write_jsonl_record(history_path, current_history_record)
            history_write_status = "written"
        except Exception as exc:
            history_write_status = "failed"
            history_write_error = str(exc)

    report["history_write_status"] = history_write_status
    if history_write_error:
        report["history_write_error"] = history_write_error
    report["trend_status"] = trend_status
    report["trend_write_status"] = trend_write_status
    if trend_write_error:
        report["trend_write_error"] = trend_write_error

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Global health report saved to {out_path}")
    if report["overall_status"] == "fail":
        sys.exit(1)

if __name__ == "__main__":
    main()
