# Tool Scientific Rigor Report (2026-04-29)

## 0. Metadata

```json
{
  "report_id": "tool_scientific_rigor_2026_04_29",
  "scope": "Acellorator root tool ecosystem and extracted UHD 770 C++ engine package",
  "classification": "code-method review",
  "empirical_claim_policy": "Only commands with recoverable output files are cited as verification evidence.",
  "overreach_check": "passed"
}
```

## 1. Executive Summary

This report evaluates the current tool ecosystem for scientific rigor: reproducibility,
recoverable output, numerical controls, falsification support, and suitability for
cross-model claims. It does not claim external scientific truth. Tool support means
the implementation is suitable for model-scoped experiments when used under the
repo governance rules.

Current status:

- `tool_manifest.json` lists 35 tools.
- Root contains 23 C++ engine/tool directories.
- Python and C++ versions coexist for several tools; Python can be archived only
  after representative C++ regression comparisons are recorded.
- New C++ ports for `symplectic`, `spectral`, `tda`, `mc_ensemble`, and
  `parameter_optimizer` have recoverable smoke evidence in
  `outputs/cpp_smoke/summary.json`.
- UHD 770 support is implemented in the extracted C++ package with CPU/GPU drift
  reporting for the D-ASE analog mission path.

## 2. Rigor Scale

| Level | Meaning for tools |
| --- | --- |
| R0 | Tool exists but has no current recoverable verification evidence. |
| R1 | Builds or runs in at least one local smoke path. |
| R2 | Emits recoverable reports with defined observables and deterministic controls. |
| R3 | Multi-seed or regression evidence exists and falsification/negative controls are available. |
| R4 | Cross-model, multi-seed, falsification-ready evidence schema is complete enough for L3 research claims. |

Rigor levels are tool-readiness levels, not claim-validation levels. A research
claim still requires the AGENTS protocol: at least two model classes, at least
three seeds, defined observables, normalized comparison, and falsification before
using "Supported".

## 3. Tool Inventory

| Tool | Class | Current role | Rigor | Main strengths | Main limits |
| --- | --- | --- | --- | --- | --- |
| `agent_based_sim_v1` | agent / Python | swarm emergence | R2 | clear order/residue metrics | Python archival pending C++ regression |
| `agent_based_sim_v1_cpp` | agent / C++ | high-performance swarm | R2 | AVX2/SYCL-oriented, manifest registered | needs current root-output audit and CPU/GPU drift schema |
| `ca_admissibility_sim_v1` | discrete CA / Python | admissibility gating | R2 | explicit discrete rule, useful negative controls | conceptual precision more than numerical precision |
| `ca_admissibility_sim_v1_cpp` | discrete CA / C++ | high-performance gating | R2 | C++ port exists, clear observables | needs representative Python/C++ equivalence report |
| `fsa_rule_engine_sim_v1` | finite state / Python | Boolean admissibility | R2 | clear continuation/halt logic | random graph sensitivity needs ensemble reporting |
| `fsa_rule_engine_sim_v1_cpp` | finite state / C++ | high-performance FSA | R2 | C++ implementation and runtime metrics | needs current root-output convention audit |
| `graph_dynamics_sim_v1` | network / Python | topology and corridors | R2 | topology + phase observables | heuristic rewiring thresholds |
| `graph_dynamics_sim_v1_cpp` | network / C++ | high-performance graph dynamics | R2 | C++ network engine exists | needs regression against Python metrics |
| `stochastic_sim_v1` | stochastic SDE / Python | threshold/noise onset | R2 | standard SDE observable set | fixed step, limited uncertainty intervals |
| `stochastic_sim_cpp` | stochastic / C++ | UHD/SYCL threshold port | R2 | zero-noise falsification and root report path | needs multi-seed CI reporting |
| `kuramoto_sim_v1` | oscillator ODE / Python | phase locking | R2 | RK4 and clear order parameter | no timestep convergence report |
| `kuramoto_sim_v1_cpp` | oscillator ODE / C++ | high-performance oscillator model | R2 | C++/SYCL-oriented port | needs current scientific schema audit |
| `rd_moving_boundary_sim_v1` | PDE / Python | moving boundary topology | R2 | clear active area and signal metrics | explicit stability constraints not enforced |
| `rd_sim_cpp` | PDE / C++ | reaction-diffusion port | R2 | root report path and precision-drift field | needs dx/dt convergence tests |
| `lb_fluid_sim_v1` | lattice Boltzmann / Python | fluid erosion | R1 | defined fluid observables | reduced model, validation sparse |
| `lb_fluid_sim_v1_cpp` | lattice Boltzmann / C++ | UHD-oriented fluid engine | R2 | C++/SYCL port exists | needs physical benchmark controls |
| `symplectic_sim_v1` | Hamiltonian / Python | conservation behavior | R2 | appropriate symplectic method | limited convergence checks |
| `symplectic_sim_v1_cpp` | Hamiltonian / C++ | conservation/precision port | R3 | FP32/FP64 drift and zero-step control | needs multi-seed or parameter-scan regression |
| `structural_box_sim_v2` | PDE / Python | identity/stability | R2 | persistence and violation metadata | explicit Euler stability risk |
| `structural_box_sim_cpp` | PDE / C++ | structural box port | R2 | root output, precision-drift metric | needs direct Python/C++ equivalence case |
| `mc_ensemble_sim_v1` | orchestrator / Python | parameter sweeps | R2 | batch-run evidence and aggregation | Python dependency remains |
| `mc_ensemble_sim_v1_cpp` | orchestrator / C++ | executable-template sweeps | R3 | recoverable trial manifests and smoke evidence | metric aggregation is schema-dependent |
| `info_metrics_module_v1` | post-processing / Python | entropy/complexity | R1 | useful derived metrics | requires input provenance discipline |
| `info_metrics_module_v1_cpp` | post-processing / C++ | accelerated metrics | R2 | C++/GPU-oriented postprocessor | needs canonical test vectors |
| `bifurcation_analyzer_v1` | analyzer / Python | regime mapping | R2 | parameter ramp abstraction | needs model-specific convergence controls |
| `bifurcation_analyzer_v1_cpp` | analyzer / C++ | high-speed regime mapping | R2 | Lyapunov/runtime metrics | needs regression against known bifurcation cases |
| `tda_module_v1` | topology / Python | Betti-0 analysis | R2 | interpretable topology metrics | limited to simple topology primitives |
| `tda_module_v1_cpp` | topology / C++ | Betti-0 connected components | R3 | empty/single/two-component controls and smoke evidence | no higher-dimensional persistent homology |
| `spectral_analysis_v1_cpp` | spectral analysis / C++ | temporal/spatial spectra | R3 | known-mode controls and recoverable reports | direct DFT is not scalable for large data |
| `parameter_optimizer_v1_cpp` | optimizer / C++ | deterministic random search | R3 | trace, best config, metric-path extraction | does not reproduce Python Nelder-Mead path |
| `linac_sim_cpp` | accelerator / C++ | linear accelerator port | R2 | FP32/FP64 precision reporting | needs benchmark against Python `linac_sim` |
| `circular_accelerator_sim_v1_cpp` | accelerator / C++ | ring accelerator port | R2 | high-performance 6D ring model | needs external/analytic validation cases |
| `accelerator_sim_v1_cpp` | accelerator / C++ | reduced 6D/PIC-style port | R2 | survival/RMS/emittance proxy metrics | not accelerator-grade beam physics validation |
| `falsification_suite_v1` | harness / Python | negative controls | R2 | required for Supported claims | Python dependency remains |
| `falsification_suite_v1_cpp` | harness / C++ | C++ falsification runner | R2 | high-performance harness exists | needs standardized suite schema coverage |

## 4. Verified Evidence Available Now

Recoverable smoke evidence exists for the five newly added C++ ports:

```json
{
  "evidence_file": "outputs/cpp_smoke/summary.json",
  "date": "2026-04-29",
  "engines": {
    "symplectic_sim_v1_cpp": 0,
    "spectral_analysis_v1_cpp": 0,
    "tda_module_v1_cpp": 0,
    "mc_ensemble_sim_v1_cpp": 0,
    "parameter_optimizer_v1_cpp": 0
  }
}
```

Additional implementation evidence is documented in:

- `CPLUSPLUS_PORTING_STATUS_2026-04-29.md`
- `ROOT_DIRECTORY_LAYOUT.md`
- `Simulation_engines_extracted_2026-04-25/UHD770_UPDATE_STATUS_2026-04-29.md`

The UHD 770 evidence is scoped to the extracted D-ASE package. It supports the
claim that one UHD 770 backend path exists and reports CPU/GPU drift for that
path. It does not prove all engines are GPU-equivalent.

## 5. Scientific Rigor Strengths

The ecosystem now has useful model diversity:

- Discrete models: CA and FSA.
- Agent models: swarm simulation.
- Network models: graph dynamics.
- Continuous PDE models: RD and structural box.
- Stochastic models: SDE threshold simulator.
- Hamiltonian model: symplectic simulator.
- Analysis layers: spectral, TDA, information metrics, bifurcation.
- Orchestration layers: Monte Carlo ensemble and optimizer.
- Falsification layer: Python and C++ harnesses.

The C++ direction improves rigor where it adds:

- deterministic seeds and explicit parameters,
- FP32/FP64 drift checks,
- zero or known-control falsification cases,
- recoverable JSON/CSV reports,
- root `outputs/<tool>/...` homes,
- CPU reference paths for GPU work.

## 6. Scientific Rigor Gaps

These gaps block strong claim promotion:

1. Python/C++ equivalence is not yet fully documented for every port.
2. Several older C++ ports still need output schema auditing against the root
   output convention and charter provenance needs.
3. Most continuous models still lack formal timestep/grid convergence tests.
4. Stochastic models need confidence intervals or bootstrap/ensemble uncertainty
   reports, not only point estimates.
5. GPU acceleration must remain paired with CPU reference drift checks before a
   result is treated as scientifically comparable.
6. Analysis tools need canonical input test vectors so future changes can be
   regression-tested without relying on ad hoc generated data.
7. Tool outputs are recoverable, but not all contain a uniform metadata block
   with seed, config hash, executable identity, backend, precision mode, and
   run timestamp.

## 7. Required Standard Before Archiving Python

For each Python tool being retired, create a directory under:

```text
outputs/port_regression_<tool>_<date>/
```

Each directory should contain:

- original Python config,
- matched C++ config,
- Python output summary,
- C++ output summary,
- comparison JSON with tolerances,
- note on expected numerical differences,
- pass/fail decision.

Minimum pass criteria:

```json
{
  "same_observables": true,
  "same_seed_or_seed_mapping": true,
  "metric_tolerance_defined": true,
  "control_case_passed": true,
  "recoverable_outputs": true
}
```

## 8. Recommended Next Rigor Upgrades

Priority order:

1. Add a common report footer to every C++ tool: `tool_name`, `version`,
   `seed`, `backend`, `precision`, `config_hash`, `timestamp`, and
   `source_commit`.
2. Add Python/C++ equivalence batches for each port before archiving Python.
3. Extend `scripts/run_cpp_smoke.ps1` to cover all 23 C++ directories in phases.
4. Add grid/timestep convergence controls for `rd_sim_cpp`,
   `structural_box_sim_cpp`, `stochastic_sim_cpp`, and accelerator tools.
5. Add canonical test vectors for `spectral_analysis_v1_cpp`,
   `tda_module_v1_cpp`, and `info_metrics_module_v1_cpp`.
6. Require CPU/GPU drift reporting for every UHD 770 path.
7. Update `tool_manifest.json` with a `model_class`, `evidence_level`, and
   `output_schema` field for each tool.

## 9. Claim Governance

Within these models, the tool ecosystem is now suitable for governed exploratory
research and model-scoped comparison. It is not yet uniformly suitable for L3
"Supported" claims without per-claim multi-model, multi-seed, falsification
evidence. The most rigorous current C++ additions are
`symplectic_sim_v1_cpp`, `spectral_analysis_v1_cpp`, `tda_module_v1_cpp`,
`mc_ensemble_sim_v1_cpp`, and `parameter_optimizer_v1_cpp`, because they have
fresh smoke evidence and explicit recoverable artifacts.

## 10. Immediate Action Items

```json
{
  "seed_sensitivity": "Add multi-seed batches for stochastic, agent, graph, CA, and optimizer tools.",
  "parameter_sensitivity": "Add bounded parameter scans with recorded config hashes.",
  "artifact_risk": "High if generated outputs lack backend, precision, seed, and commit metadata."
}
```

