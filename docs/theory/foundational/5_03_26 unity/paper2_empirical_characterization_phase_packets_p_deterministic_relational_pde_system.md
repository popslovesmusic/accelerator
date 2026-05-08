PCD-Formal-Stack: v1
Compliance-Charter: v2.3
Claim-Support-Matrix: required
Math-Source-Binding: required

# Empirical Characterization of Phase Packets (p) in a Deterministic, Relational PDE System

## Signature Block

This work presents an empirical characterization of phase packets `(p)` in a deterministic PDE system using a relational (baseline-relative) detectability protocol rather than noise-variance statistics. The aim is operational: define detectability with explicit tolerance and persistence criteria, report governed scan outcomes, and state clearly when results are measurement-limited upper bounds rather than intrinsic minimal units.

## Abstract

We define a **phase packet** `(p)` as a phase-coherent, bounded region of continuation **relative to a dynamic baseline** in a deterministic PDE system. We introduce an empirical **trajectory-divergence detector** that does not rely on stochastic noise variance: using the baseline PDE trajectory `ε0(x,t)` and an injected trajectory `εδ(x,t)`, we measure `D(t)=max_x |εδ(x,t)−ε0(x,t)|` and declare detection when `D(t) > η` persists for `T_p` consecutive recorded steps. Across high-resolution scans with many trials per amplitude, we find **no mixed detection regime** in the tested range; detection probability remained `1.0` down to the smallest scanned amplitudes under the chosen `η`. Under the present detector and solver settings, this implies **no intrinsic lower detectability bound was observed within tested precision**; operationally, the empirical detectability bound satisfies `Δφ_min,emp < 1e-16` for `η=1e-16` and `T_p=50`. This result is measurement- and protocol-dependent: `(p)` is relational and operational rather than an absolute minimal unit.

## 1. Introduction

The motivating question is not “what is the smallest mismatch that can exist?” but rather:

- **Operational detectability:** for a fixed model, solver, and measurement protocol, what is the smallest injected deviation that becomes reliably distinguishable from the baseline continuation?

This framing replaces “smallest unit” thinking with **protocol-bound** detectability relative to a **dynamic, relational floor** (baseline continuation). The core contribution here is (i) an explicit deterministic detector based on divergence from a baseline trajectory, and (ii) an empirical finding that, within the tested range and settings, no intrinsic detectability cutoff appears.

## 2. Definitions (Operational)

### 2.1 Dynamic baseline (“floor”)

Let `ε0(x,t)` denote the **baseline continuation** under admissible evolution with no injected deviation (under the same solver and parameters used for the injected runs).

This “floor” is **not** defined as stochastic-noise variance. In the deterministic regime used here, baseline variance of certain observables can be exactly zero, making noise-variance detectors ill-posed (see Section 5).

### 2.2 Phase packet `(p)`

We treat `(p)` as an **operational object**: a bounded, phase-coherent continuation structure relative to the baseline. It is not assumed to be a discrete primitive. Discrete-like behavior, if present, is taken to be **emergent** from stability and admissibility constraints.

### 2.3 Deviation / mismatch

We consider injected deviations by amplitude `δ > 0` applied to the PDE state (here: an injected perturbation in `epsilon` using the same injection family as the executed scans).

### 2.4 Detectability (trajectory divergence)

Define the instantaneous divergence observable:

`D(t) = max_x |εδ(x,t) − ε0(x,t)|`.

Let `η` be an explicit numerical tolerance and `T_p` a persistence window in **consecutive recorded steps**. We define detection as:

- detected iff `D(t) > η` for at least `T_p` consecutive recorded steps.

We run multiple trials per amplitude (varying injection location) and define:

- `P_detect(δ) = detected_trials / total_trials`.

Operational value:

- `Δφ_min,emp` is the smallest `δ` with `P_detect(δ) ≥ 0.95`.

Important: if `P_detect(δ)=1.0` for all tested `δ`, the result is an **upper bound**: `Δφ_min,emp < δ_min_scanned`.

## 3. Model and environment (executed configuration)

All primary PDE empirical results cited below use the same core PDE engine and a deterministic setup:

- Engine: `level2_pde_cpp`
- Deterministic regime: `noise_std = 0`
- Grid/time (from the executed reports):
  - `Nx = 256`
  - `dt = 1e-3`
  - warmup: `warmup_steps = 50`
  - measurement: `measurement_steps = 1500`
  - recording: `record_every = 1`

These settings are recorded in:

- `experiments/pde/output/delta_phi_min_empirical_lower_scan_report.md`
- `experiments/pde/output/sim7_transition_curve_report.md`

## 4. Measurement protocol

### 4.1 Baseline

We compute a single baseline trajectory `ε0(x,t)` under the same solver and parameters and record the full baseline evolution for use in divergence comparisons.

### 4.2 Injection

We inject deviations of prescribed amplitudes into the baseline initial condition (after warmup). Trials vary **injection location** (and keep other conditions fixed) to obtain a detection probability per amplitude.

### 4.3 Primary observable

`D(t)=max_x |εδ(x,t)−ε0(x,t)|`.

### 4.4 Detection rule

Detected iff `D(t) > η` for `T_p` consecutive recorded steps.

### 4.5 Reliability criterion

We report `P_detect(δ)` and use the operational threshold `P_detect(δ) ≥ 0.95` for “reliable detection”.

## 5. Method progression (What failed and why)

### 5.1 Noise-variance z-score detector (invalid in deterministic baseline)

A z-score detector based on baseline variance fails when `sigma_floor = 0` in a deterministic baseline. In that case, z-score detectability is undefined.

Executed evidence:

- `experiments/pde/output/delta_phi_min_detectability_report.md`

### 5.2 Survival/collapse refinement (context only)

Survival/collapse detectors can be useful for regime description, but they answer a different question than “minimal detectable deviation relative to a baseline trajectory”.

Executed evidence:

- `experiments/pde/output/delta_phi_min_refinement_report.md`

### 5.3 Trajectory divergence (primary detector)

We adopt trajectory divergence from baseline as the primary operational detector because it is well-defined in deterministic regimes and explicitly logs `η` and `T_p`.

## 6. Experiments

### 6.1 Coarse scan

Evidence:

- `experiments/pde/output/delta_phi_min_empirical_report.md`

### 6.2 Lower scan

Evidence:

- `experiments/pde/output/delta_phi_min_empirical_lower_scan_report.md`

### 6.3 High-resolution scan

Evidence:

- `experiments/pde/output/sim7_transition_curve_report.md`

## 7. Results

### 7.1 Primary empirical statement

Within the tested PDE regime and under the trajectory-divergence detector:

- No mixed detection regime was observed in the scanned ranges.
- Detection probability remained `1.0` for all tested amplitudes down to the smallest scanned amplitudes.
- Therefore, the result is an **upper bound** under the specified protocol:
  - `Δφ_min,emp < 1e-16` for `η=1e-16`, `T_p=50` (current solver + model settings).

### 7.2 What is (and is not) claimed

Claimed:

- An operational detectability bound under a clearly stated detector and numerical tolerance.

Not claimed:

- A universal minimal mismatch scale.
- A proof of an ontological “smallest existing mismatch”.

## 8. Interpretation

The detected bound depends on:

- tolerance `η`,
- persistence window `T_p`,
- observable choice (`D(t)`),
- solver/time discretization and recorded cadence.

Accordingly, the proper statement is: **no intrinsic detectability cutoff was observed within the tested numerical resolution**.

## 9. Statistical framing without stochastic noise

Repeated trials here are used as a stability/reliability check for the detector (varying injection location), not as a claim that the system is fundamentally stochastic.

## 10. Limitations

- Measurement-limited: `Δφ_min,emp` is bounded only down to the smallest scanned amplitude under the chosen `η`.
- Detector-specific: other observables/detectors could yield different operational bounds.
- Regime-limited: no claim that this bound transfers across parameter regimes or models.

## 11. Implications

- The evidence supports a relational plank concept: operational detectability relative to dynamic baseline continuation.
- Within tested precision, there is no evidence for a smallest detectable unit; detectability persists below `1e-16` under the present protocol.

## 12. Conclusion

Using a deterministic PDE trajectory-divergence detector with explicit tolerance `η` and persistence window `T_p`, all tested amplitudes down to `1e-16` produced reliable divergence from baseline continuation under the current settings. The strongest writing-safe empirical statement is therefore:

- `Δφ_min,emp < 1e-16` (for `η=1e-16`, `T_p=50`), i.e. no intrinsic lower detectability bound was observed within tested numerical precision.
