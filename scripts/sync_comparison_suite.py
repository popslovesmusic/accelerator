import json
import os

manifest_path = "tool_manifest.json"
with open(manifest_path, 'r', encoding='utf-8-sig') as f:
    manifest = json.load(f)

# Tools to update/add
comparison_tools = [
    {
        "name": "dase_analog_sim_v1",
        "description": "NumPy-based mission simulator for analog feedback loops (comparison prototype).",
        "entry_point": "dase_analog_sim_v1/sim.py",
        "cli_command": "python dase_analog_sim_v1/sim.py --config {config} --out {out_dir}",
        "config_params": ["n_nodes", "steps", "iterations", "dt"],
        "metrics": ["mean_output", "max_output", "mean_integrator"],
        "model_class": "analog_simulation",
        "certification_level": "C1"
    },
    {
        "name": "satp_higgs_sim_v1",
        "description": "NumPy-based 2D finite-difference scalar field simulator with Higgs potential (comparison prototype).",
        "entry_point": "satp_higgs_sim_v1/sim.py",
        "cli_command": "python satp_higgs_sim_v1/sim.py --config {config} --out {out_dir}",
        "config_params": ["size", "steps", "dt", "dx", "h_vev", "lambda_h", "g"],
        "metrics": ["phi_rms", "higgs_rms"],
        "model_class": "field_simulation",
        "certification_level": "C1"
    },
    {
        "name": "satp_higgs_3d_sim_v1",
        "description": "NumPy-based 3D finite-difference scalar field simulator with Higgs potential (comparison prototype).",
        "entry_point": "satp_higgs_3d_sim_v1/sim.py",
        "cli_command": "python satp_higgs_3d_sim_v1/sim.py --config {config} --out {out_dir}",
        "config_params": ["size", "steps", "dt", "dx", "h_vev", "lambda_h", "g"],
        "metrics": ["phi_rms", "higgs_rms"],
        "model_class": "field_simulation",
        "certification_level": "C1"
    },
    {
        "name": "symplectic_sim_v1",
        "description": "Python Hamiltonian integration prototype (restored for comparison).",
        "entry_point": "symplectic_sim_v1/sim.py",
        "cli_command": "python symplectic_sim_v1/sim.py --config {config} --out {out_dir}",
        "config_params": ["kappa", "dt", "initial_q_spread", "n_particles", "steps"],
        "metrics": ["mean_H", "std_H", "q_rms"],
        "model_class": "hamiltonian",
        "certification_level": "C1"
    },
    {
        "name": "spectral_analysis_v1",
        "description": "Python spectral analysis layer (restored for comparison).",
        "entry_point": "spectral_analysis_v1/analyze_spectrum.py",
        "cli_command": "python spectral_analysis_v1/analyze_spectrum.py --dir {data_path} --threshold {threshold}",
        "config_params": ["threshold"],
        "metrics": ["dominant_modes", "total_power"],
        "model_class": "spectral_analyzer",
        "certification_level": "C1"
    },
    {
        "name": "tda_module_v1",
        "description": "Python Topological Data Analysis prototype (restored for comparison).",
        "entry_point": "tda_module_v1/analyze_topology.py",
        "cli_command": "python tda_module_v1/analyze_topology.py --dir {data_path} --threshold {threshold}",
        "config_params": ["threshold", "mode"],
        "metrics": ["count", "max_size", "active_fraction"],
        "model_class": "topology_analyzer",
        "certification_level": "C1"
    },
    {
        "name": "mc_ensemble_sim_v1",
        "description": "Python parameter sweep orchestrator (restored for comparison).",
        "entry_point": "mc_ensemble_sim_v1/mc_runner.py",
        "cli_command": "python mc_ensemble_sim_v1/mc_runner.py --config {config} --out {out_dir}",
        "config_params": ["trials", "scan_params"],
        "metrics": ["ensemble_results.csv"],
        "model_class": "orchestrator",
        "certification_level": "C1"
    },
    {
        "name": "parameter_optimizer_v1",
        "description": "Python parameter optimizer prototype (restored for comparison).",
        "entry_point": "parameter_optimizer_v1/optimize_runner.py",
        "cli_command": "python parameter_optimizer_v1/optimize_runner.py --config {config} --out {out_dir}",
        "config_params": ["max_evals", "search_params"],
        "metrics": ["optimization_trace.csv", "best_config.json"],
        "model_class": "optimizer",
        "certification_level": "C1"
    },
    {
        "name": "linac_sim_v1",
        "description": "Pure Python linear accelerator prototype (sync with manifest).",
        "entry_point": "linac_sim/__main__.py",
        "cli_command": "python linac_sim --config {config} --out {out_dir}",
        "config_params": ["particles", "steps", "rf_gradient"],
        "metrics": ["survival_fraction", "energy_gain"],
        "model_class": "accelerator",
        "certification_level": "C1"
    },
    {
        "name": "circular_accelerator_sim_v1",
        "description": "Pure Python ring simulation prototype.",
        "entry_point": "circular_accelerator_sim_v1/ring_sim.py",
        "cli_command": "python circular_accelerator_sim_v1/ring_sim.py --config {config} --out {out_dir}",
        "config_params": ["particles", "turns", "circumference"],
        "metrics": ["x_rms", "z_rms", "survival_fraction"],
        "model_class": "accelerator",
        "certification_level": "C1"
    }
]

manifest_tools = {t["name"]: t for t in manifest["tools"]}

for info in comparison_tools:
    if info["name"] in manifest_tools:
        # Update existing
        manifest_tools[info["name"]].update(info)
        manifest_tools[info["name"]]["last_validation_date"] = "2026-04-29"
        print(f"Updated {info['name']} in manifest")
    else:
        # Add new
        info["last_validation_date"] = "2026-04-29"
        info["has_falsification"] = False
        info["numerical_stability_verified"] = False
        info["uncertainty_quantified"] = False
        info["provenance_verified"] = False
        manifest["tools"].append(info)
        print(f"Added {info['name']} to manifest")

with open(manifest_path, 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=4)
print("Updated tool_manifest.json with full comparison suite")
