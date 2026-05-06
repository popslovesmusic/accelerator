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

        gap_queue, err = self.validate_json_load(self.gap_queue_path)
        if err: results["errors"].append(f"Gap Queue Load Error: {err}")

        if results["errors"]:
            results["status"] = "failed"
            return results

        # 2. Integrity Checks: All tools in lexicon registry must exist in tool manifest
        manifest_tools = {t["name"] for t in manifest.get("tools", [])}
        for term, data in lexicon.get("terms", {}).items():
            for role, role_data in data.get("roles", {}).items():
                for model in role_data.get("models_used", []):
                    if model not in manifest_tools and "_v1" not in model: # v1 often python counterparts
                        results["errors"].append(f"Integrity Error: Term '{term}' role '{role}' uses unregistered tool '{model}'")

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
            cmd = [sys.executable, str(wrapper), "--config", str(config_path), "--out", str(out_dir)]
        else:
            cmd = [str(wrapper), "--config", str(config_path), "--out", str(out_dir)]
            
        try:
            # Run in the tool's directory if it's an executable that might need local DLLs
            cwd = wrapper.parent
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
        self.math_registry_path = self.root / "registry/math_registry.json"
        self.math_hashes_path = self.root / "registry/math_hashes.json"

    def calculate_hash(self, path):
        import hashlib
        try:
            content = path.read_bytes()
            return hashlib.sha256(content).hexdigest()
        except:
            return None

    def run(self):
        results = {"status": "success", "errors": []}
        
        if not self.math_registry_path.exists():
            return results

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

            if item_id in hashes:
                if hashes[item_id] != current_hash:
                    # Check if it's a template
                    if "TEMPLATE" in path.name: continue
                    results["errors"].append(f"Governance Violation: Math file '{item['path']}' was modified (Additive-Only Rule Violation).")

        # Update hashes (only if no errors, to prevent locking in broken states)
        if not results["errors"]:
            with open(self.math_hashes_path, 'w', encoding='utf-8') as f:
                json.dump(new_hashes, f, indent=2)

        if results["errors"]:
            results["status"] = "failed"
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
        "math_validation": MathValidator(root).run()
    }

    report["overall_status"] = "pass" if all(v["status"] == "success" for k, v in report.items() if isinstance(v, dict)) else "fail"

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Global health report saved to {out_path}")
    if report["overall_status"] == "fail":
        sys.exit(1)

if __name__ == "__main__":
    main()
