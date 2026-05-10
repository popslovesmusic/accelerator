import os
import json
import shutil
from pathlib import Path
import time

def create_zenodo_bundle(bundle_id, paper_path, run_dirs, metadata):
    """
    Generate a Zenodo-compliant archival bundle.
    """
    bundle_root = Path(f"zenodo/bundles/{bundle_id}")
    os.makedirs(bundle_root / "configs", exist_ok=True)
    os.makedirs(bundle_root / "data", exist_ok=True)
    
    print(f"Creating Zenodo bundle: {bundle_id}")
    
    # 1. Metadata
    with open(bundle_root / "zenodo_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
        
    # 2. Paper
    shutil.copy(paper_path, bundle_root / "paper.md")
    
    # 3. Collect Simulation Evidence
    all_metrics = []
    for run_dir in run_dirs:
        run_path = Path(run_dir)
        run_name = run_path.name
        
        # Copy config
        config_src = run_path / "data" / "config.json"
        if config_src.exists():
            shutil.copy(config_src, bundle_root / "configs" / f"{run_name}_config.json")
            
        # Copy provenance
        prov_src = run_path / "data" / "provenance_manifest.json"
        if prov_src.exists():
            shutil.copy(prov_src, bundle_root / f"{run_name}_provenance.json")
            
        # Copy falsification
        fals_src = run_path / "data" / "falsification_report.json"
        if fals_src.exists():
            shutil.copy(fals_src, bundle_root / f"{run_name}_falsification.json")
            
        # Collect metrics
        metrics_src = run_path / "data" / "metrics.json"
        if metrics_src.exists():
            with open(metrics_src, 'r') as f:
                run_metrics = json.load(f)
                run_metrics["run_id"] = run_name
                all_metrics.append(run_metrics)
                
    with open(bundle_root / "aggregate_metrics.json", 'w') as f:
        json.dump(all_metrics, f, indent=2)
        
    # 4. Manifest
    manifest = {
        "bundle_id": bundle_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pcd_stack": "v1",
        "contents": [str(p.relative_to(bundle_root)) for p in bundle_root.glob("**/*") if p.is_file()]
    }
    with open(bundle_root / "bundle_manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Bundle created successfully at {bundle_root}")
    return str(bundle_root)

if __name__ == "__main__":
    # Example usage for Orientation Emergence (Paper 4)
    metadata = {
        "title": "Orientation Emergence: Deriving Local Reference -(i) from Admissible Mismatch-Minimizing Selection",
        "authors": ["PCD Framework Governance Layer"],
        "description": "Formal derivation of local reference -(i) and simulation validation of stable minimizer switching.",
        "license": "CC-BY-4.0",
        "keywords": ["PCD", "-(i)", "orientation", "admissibility", "simulation"],
        "doi_or_placeholder": "10.5281/zenodo.placeholder"
    }
    
    paper_path = "docs/theory/foundational/5_03_26 unity/math/paper4_deriving_local_reference_minus_i_from_admissible_mismatch_minimizing_selection.md"
    run_dirs = [
        "results/msv_001/full_execution_v1/2026-05-10_run01_MSV-001-GRAPH-REF-V1",
        "results/msv_001/full_execution_v1/2026-05-10_run01_MSV-001-CA-REF-V1"
    ]
    
    create_zenodo_bundle("orientation_emergence_v1", paper_path, run_dirs, metadata)
