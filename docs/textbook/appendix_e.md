# Appendix E: Simulation Evidence Index

This index points to the primary evidence pools supporting the claims made in this textbook. All paths refer to the `results/` directory of the project repository.

### Key Evidence Packages
| Target Claim | Supporting Run(s) | Mechanism Classes | Status |
| :--- | :--- | :--- | :--- |
| **Pi-A Stability** | `results/mpf_sim_001_pi_a_stability/` | Agent, CA | Supported (C4) |
| **Metastability Basins** | `results/mpf_sim_003_metastability_oscillatory/` | ODE, PDE | Partially Supported (C2) |
| **Braid Formation** | `results/mpf_sim_005_braid_triadic_closure/` | Graph, Agent | Provisional (C1) |
| **Orientation Bias** | `results/mpf_sim_008_orientation_selection/` | CA, Graph | Supported (C4) |
| **Gravity-like Gradient** | `results/mpf_sim_012_alignment_refraction/` | PDE | Structural Comparison (C3) |

### Evidence Requirements
To be listed in this index, a run must provide:
1. **Raw Metrics:** Saved in `data/` subdirectory.
2. **Analysis Artifacts:** Plots, spectral data, or TDA results in `artifacts/`.
3. **Reproducibility Metadata:** Exact config hash, seed, and tool version.
4. **Falsification Report:** Documenting at least one adversarial test result.

### Accessing Evidence
Raw data and simulation artifacts for the above runs are archived in the `results/` folder. For access to the specific codebase versions used for these runs, refer to the `source_commit` field in the run metadata JSON.
