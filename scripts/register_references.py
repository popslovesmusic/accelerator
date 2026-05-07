import json
import os
from pathlib import Path

def update_manifest():
    manifest_path = "registry/tool_manifest.json"
    with open(manifest_path, 'r', encoding='utf-8-sig') as f:
        manifest = json.load(f)

    # Map of C++ tools to their reference implementations
    references = {
        "igsoa_gw_core_cpp": "tools/igsoa_gw_core_cpp/reference/sim_reference.py",
        "igsoa_complex_1d_cpp": "tools/igsoa_complex_1d_cpp/reference/sim_reference.py",
        "igsoa_complex_2d_cpp": "tools/igsoa_complex_2d_cpp/reference/sim_reference.py",
        "igsoa_complex_3d_cpp": "tools/igsoa_complex_3d_cpp/reference/sim_reference.py",
        "satp_higgs_1d_cpp": "tools/satp_higgs_1d_cpp/reference/sim_reference.py",
        "tda_module_v2_cpp": "tools/tda_module_v2_cpp/reference/sim_reference.py",
        # Existing ones
        "fsa_rule_engine_sim_v1_cpp": "tools/fsa_rule_engine_sim_v1/sim.py",
        "ca_admissibility_sim_v1_cpp": "tools/ca_admissibility_sim_v1/sim.py",
        "graph_dynamics_sim_v1_cpp": "tools/graph_dynamics_sim_v1/sim.py",
        "stochastic_sim_cpp": "tools/stochastic_sim_v1/sim.py",
        "kuramoto_sim_v1_cpp": "tools/kuramoto_sim_v1/sim.py",
        "symplectic_sim_v1_cpp": "tools/symplectic_sim_v1/sim.py",
        "structural_box_sim_cpp": "tools/structural_box_sim_v2/sim.py",
        "agent_based_sim_v1_cpp": "tools/agent_based_sim_v1/sim.py",
        "lb_fluid_sim_v1_cpp": "tools/lb_fluid_sim_v1/sim.py",
        "accelerator_sim_v1_cpp": "tools/accelerator_sim_v1/sim.py",
        "dase_analog_sim_cpp": "tools/dase_analog_sim_v1/sim.py",
        "satp_higgs_sim_cpp": "tools/satp_higgs_sim_v1/sim.py",
        "satp_higgs_3d_sim_cpp": "tools/satp_higgs_3d_sim_v1/sim.py",
        "circular_accelerator_sim_v1_cpp": "tools/circular_accelerator_sim_v1/ring_sim.py",
        "tda_module_v1_cpp": "tools/tda_module_v1/analyze_topology.py",
        "spectral_analysis_v1_cpp": "tools/spectral_analysis_v1/analyze_spectrum.py",
        "mc_ensemble_sim_v1_cpp": "tools/mc_ensemble_sim_v1/mc_runner.py",
        "parameter_optimizer_v1_cpp": "tools/parameter_optimizer_v1/optimize_runner.py"
    }

    for tool in manifest["tools"]:
        if tool["name"] in references:
            tool["reference_implementation"] = references[tool["name"]]
            tool["has_reference_implementation"] = True
        elif tool["implementation_language"] == "cpp":
            tool["has_reference_implementation"] = False

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    print("Updated tool_manifest.json with reference implementations.")

if __name__ == "__main__":
    update_manifest()
