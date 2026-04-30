import json
import os

c1_tools = [
    "agent_based_sim_v1_cpp",
    "bifurcation_analyzer_v1_cpp",
    "ca_admissibility_sim_v1_cpp",
    "circular_accelerator_sim_v1_cpp",
    "falsification_suite_v1_cpp",
    "fsa_rule_engine_sim_v1_cpp",
    "graph_dynamics_sim_v1_cpp",
    "info_metrics_module_v1_cpp",
    "kuramoto_sim_v1_cpp",
    "lb_fluid_sim_v1_cpp"
]

for tool in c1_tools:
    path = os.path.join(tool, "validation", "certification_manifest.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            if not content.strip():
                print(f"Skipping empty file: {path}")
                continue
            data = json.loads(content)
        
        data["certification_level"] = "C1"
        data["latest_validation_outputs"] = [f"outputs/full_cpp_validation/{tool}.log"]
        data["scientific_validity"]["implementation_verified"] = True
        data["scientific_validity"]["reproducibility_verified"] = True
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Updated {path}")

# Update tool_manifest.json
manifest_path = "tool_manifest.json"
with open(manifest_path, 'r', encoding='utf-8-sig') as f:
    manifest = json.load(f)

# Update all C++ tools in manifest based on their individual certification_manifest.json
for tool_entry in manifest["tools"]:
    if tool_entry["name"].endswith("_cpp"):
        tool_name = tool_entry["name"]
        cert_path = os.path.join(tool_name, "validation", "certification_manifest.json")
        if os.path.exists(cert_path):
            with open(cert_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                if not content.strip():
                    continue
                cert_data = json.loads(content)
            
            tool_entry["certification_level"] = cert_data["certification_level"]
            tool_entry["last_validation_date"] = "2026-04-29"
            tool_entry["has_falsification"] = cert_data["scientific_validity"]["falsification_verified"]
            tool_entry["numerical_stability_verified"] = cert_data["scientific_validity"]["numerical_stability_verified"]
            tool_entry["uncertainty_quantified"] = cert_data["scientific_validity"]["uncertainty_quantified"]
            tool_entry["provenance_verified"] = cert_data["scientific_validity"]["provenance_verified"]
            print(f"Updated {tool_name} in manifest to {cert_data['certification_level']}")

with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=4)
print("Updated tool_manifest.json")
