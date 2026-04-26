# Tool Scientific Precision Report (2026-04-25)

This report evaluates the *scientific precision* of the repo’s simulation tools as implemented in code. “Precision” here means: numerical integration quality, reproducibility, validation coverage, metric definitional clarity, and (where applicable) physical/unit fidelity. It does **not** imply external scientific correctness.

Charter note: `theory/lexicon/compliance_charter_v2_3.json` requires strict provenance for **empirical claims in documents**. This report is a code-method review, not an empirical results claim.

## 1. Evaluation Criteria

Each tool is scored qualitatively across:

- **Numerics:** integrator order, stability considerations, convergence checks, discretization clarity.
- **Stochastic rigor:** seed control, RNG isolation, ensemble support, statistical reporting.
- **Validation:** existence of limiting-case checks, invariants, regression/falsification hooks.
- **Observables:** metrics are defined, interpretable, and logged in recoverable artifacts (`summary.json`, `metrics.csv`, etc.).
- **Physical fidelity (when applicable):** SI units, governing equations aligned with domain, boundary conditions explicit.

## 2. High-Precision / Best-Validated Tooling

### `linac_sim` (physical units + validation suite)

- **Strengths**
  - SI units and relativistic constraints (e.g., explicit speed-limit check).
  - Multiple explicit validation checks in `linac_sim/validation.py` including: zero-field energy conservation, nonrelativistic limit under constant field, RF phase check, timestep convergence, aperture loss, and emittance calculation.
  - Seeded beam initialization via `SimulationConfig.seed`.
- **Precision limits**
  - Still a reduced model (no space charge, field maps, etc.); precision is “internal consistency” more than “accelerator-grade code”.
- **Scientific precision rating (relative, repo-internal)**
  - Numerics: **medium** (explicit time stepping; convergence check exists)
  - Reproducibility: **high**
  - Validation: **high**

## 3. Medium-Precision Dynamical Systems (Clear Integrators, Limited Validation)

### `kuramoto_sim_v1`

- **Method:** fixed-step RK4 integration for phase ODE (`kuramoto_sim_v1/kuramoto_engine.py`).
- **Strengths:** integrator is explicit and standard; coherence observables are clear (`order_parameter`, `local_coherence_mean`).
- **Limits:** no timestep convergence testing; units are abstract; ring-neighbor coupling only.
- **Rating:** Numerics **medium-high**, reproducibility **high**, validation **medium**.

### `graph_dynamics_sim_v1`

- **Method:** RK4 for phase dynamics + stochastic rewiring rule (`graph_dynamics_sim_v1/network_engine.py`).
- **Strengths:** separates phase update vs topology update; logs both topology and phase metrics.
- **Limits:** rewiring uses heuristic stress thresholds; no convergence/robustness checks; RNG is global (`np.random.*`) but seeded in driver.
- **Rating:** Numerics **medium**, reproducibility **medium-high**, validation **low-medium**.

### `symplectic_sim_v1`

- **Method:** 2nd-order symplectic leapfrog / Verlet (`symplectic_sim_v1/symplectic_engine.py`).
- **Strengths:** symplectic structure appropriate for Hamiltonian systems; logs energy drift proxy.
- **Limits:** no formal error control; no convergence checks; physics is a stylized nonlinear pendulum, not a calibrated physical system.
- **Rating:** Numerics **medium-high**, reproducibility **high**, validation **medium** (energy drift metric helps).

### `stochastic_sim_v1`

- **Method:** Euler–Maruyama for SDE (`stochastic_sim_v1/sde_engine.py`).
- **Strengths:** correct baseline method for SDE; clear threshold-crossing observable (`crossing_fraction`) and onset-time tracking.
- **Limits:** fixed dt, no strong/weak convergence study; global RNG use; limited statistical diagnostics (means/stdevs, not confidence intervals).
- **Rating:** Numerics **medium**, stochastic rigor **medium**, validation **medium** (falsification exists in harness).

### `structural_box_sim_v2` (PDE scaffold)

- **Method:** explicit Euler time stepping for coupled reaction–diffusion fields (`structural_box_sim_v2/sim.py`).
- **Strengths:** clear governing RHS structure; boundary handling explicit (Neumann via padding); logs “within box” margins and first-violation metadata.
- **Limits:** explicit Euler stability constraints are not enforced/diagnosed; no dt/dx convergence checks; clamp-to-nonnegative can mask numerical instabilities.
- **Rating:** Numerics **medium**, reproducibility **high**, validation **medium-low**.

### `rd_moving_boundary_sim_v1`

- **Method:** explicit Euler for reaction–diffusion with finite differences (`rd_moving_boundary_sim_v1/rd_engine.py`).
- **Strengths:** explicit equations; snapshots + aggregate metrics.
- **Limits:** CFL/stability not checked; clipping (`D` in [0,1]) can hide instability; stochasticity absent but sensitivity likely high.
- **Rating:** Numerics **medium-low**, reproducibility **high**, validation **low**.

## 4. Low-Precision / Primarily Conceptual Engines (Algorithmic, Not Numerical-Scientific)

### `ca_admissibility_sim_v1`

- **Method:** deterministic update rule with admissibility mask (`gradient > R`) and residue evolution (`R = R*(1-γ) + δ*active`), plus optional seeded initialization noise (`epsilon_noise_std`, `residue_noise_std`) in `ca_admissibility_sim_v1/ca_engine.py`.
- **Strengths:** rule is explicit; metrics are simple and recoverable; good for “filter/gating” role tests.
- **Limits:** not a physical CA; boundary conditions are periodic via `np.roll`; “precision” is mostly definitional (does the rule implement the intended concept) rather than numerical accuracy.
- **Rating:** Numerics **low** (discrete rule), reproducibility **high**, validation **medium** (via falsification suites).

### `fsa_rule_engine_sim_v1`

- **Method:** finite-state graph with admissibility gating by residue (`fsa_rule_engine_sim_v1/fsa_engine.py`).
- **Strengths:** explicit admissibility logic; yields clear “continuation vs halt” observable.
- **Limits:** seed sensitivity is dominated by random graph realization; does not approximate a physical process; “precision” is conceptual/algorithmic.
- **Rating:** Numerics **n/a**, reproducibility **medium-high**, validation **low-medium**.

## 5. Accelerator Prototypes (Research-Focused, Not High-Fidelity Beam Physics)

### `accelerator_sim_v1`

- **Method:** vectorized map updates for a reduced 6D state (`accelerator_sim_v1/sim.py`), with simplified drift/quadrupole/rf/aperture elements.
- **Strengths:** fast, reproducible parameter studies; logs survival + RMS + emittance proxies; snapshots to `.npz`.
- **Limits:** not symplectic tracking; “delta” update is stylized; no SI-unit grounding; limited validation.
- **Rating:** Numerics **medium-low**, reproducibility **high**, validation **low**.

## 6. Cross-Cutting Precision Gaps

These are repo-wide opportunities to improve scientific precision:

1) **Convergence tests:** only `linac_sim` includes an explicit dt refinement check; other continuous-time tools would benefit from at least one convergence diagnostic.
2) **RNG isolation:** several tools use `np.random.seed` + global RNG; prefer `np.random.default_rng(seed)` passed explicitly to engines to avoid accidental cross-coupling between modules.
3) **Uncertainty reporting:** stochastic tools generally report point estimates; add confidence intervals or bootstrap summaries for key observables.
4) **Schema/provenance alignment:** most tools do not emit the charter annex_B v2.3 metric schema fields (e.g., sim_id, batch_id, run_date, seed_unanimity). This limits charter-level “verified” claims even when files are recoverable.
5) **Clipping/clamping:** several PDE/field tools clip or clamp fields; useful for stability but can hide numerical issues unless coupled with diagnostics (e.g., fraction clipped per step).

## 7. Summary (Practical Guidance)

- If you need **physics-grade internal consistency + validation**, start with `linac_sim`.
- If you need **clean dynamical systems observables**, `kuramoto_sim_v1` and `symplectic_sim_v1` are the most method-explicit.
- If you need **concept validation of admissibility/filtering**, use `ca_admissibility_sim_v1` + `fsa_rule_engine_sim_v1` (but treat results as role-specific, model-scoped).
- For **charter-compliant writing**, treat non-rerun-tool outputs as recoverable evidence but be conservative about “verified” unless the charter schema requirements are explicitly met.

