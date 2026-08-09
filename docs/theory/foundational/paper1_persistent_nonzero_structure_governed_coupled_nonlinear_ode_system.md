PCD-Formal-Stack: v1
Compliance-Charter: v2.3
Claim-Support-Matrix: required
Math-Source-Binding: required

# Persistent Nonzero Structure in a Governed Coupled Nonlinear ODE System: Regime Mapping, Collapse Resistance, and Near-Floor Behavior

## Signature Block

This work presents a mathematical model exploring the conditions under which persistent nonzero structure can arise in coupled nonlinear systems. The formulation is offered as a provisional construction intended for analysis, critique, and refinement within established mathematical and physical frameworks. It forms part of a broader ongoing effort to develop a unified and systematically testable description of physical phenomena.

## Abstract

This work presents a mathematical model exploring the conditions under which persistent nonzero structure can arise in coupled nonlinear systems. The formulation is offered as a provisional construction intended for analysis, critique, and refinement within established mathematical and physical frameworks. It forms part of a broader ongoing effort to develop a unified and systematically testable description of physical phenomena.

We study a coupled nonlinear evolution system with competing reinforcement, suppression, and memory terms, represented for the present analysis in scalar form and examined through a purpose-built simulation program. The investigation focuses on the emergence, loss, and transition of persistent nonzero regimes under variation of interaction, saturation, and memory parameters. Particular attention is given to the role of the memory variable in shifting stability boundaries, modifying transients, and supporting sustained structure.

The paper combines model definition, controlled computational experiments, and regime classification to identify conditions associated with collapse, persistence, oscillatory behavior, transitional states, and low-epsilon near-floor behavior. The central contribution is a structured map of governed ODE behavior together with a clear computational framework for subsequent PDE and relational extensions. The present draft should be read as a technical entry point rather than as a finalized physical theory.

## 1. Introduction

Persistent nonzero structure is not a trivial outcome in nonlinear systems with both reinforcing and suppressive terms. In many familiar settings, sufficiently strong damping, antagonistic coupling, or resource-like saturation can drive a tracked variable toward collapse, extinction, or washout. The present paper begins from a narrower and more disciplined question: within a purpose-built local nonlinear system, do there exist governed parameter regions in which the tracked state remains persistently nonzero, and if so, how does that persistence change as suppression is strengthened and support is withdrawn?

Paper 1 is intentionally limited in scope. It does not attempt to argue for a universal law, a final ontology, or a master interpretive framework. Instead, it studies a specific constructed system under controlled numerical experiments and reports only what is supported by governed outputs stored in this repository. The current evidence base is confined to the ODE layer. No spatial PDE results are integrated into the present draft, and no claim is made here that local ODE behavior automatically transfers to higher-dimensional or diffusive settings.

The immediate motivation for this paper is twofold. First, the project required a fresh simulation program and governed output pipeline rather than reuse of legacy solver outputs. That layer is now in place through the governed driver and batch framework implemented in `sim/src/run_driver.py` and `sim/src/batch_runner.py`, together with manifest, config-snapshot, and per-run summary outputs under `artifacts/runs/`. Second, the governed scan results now show a coherent technical story that is strong enough to support an entry paper: broad persistence and transitional structure appear across the tested ODE region, while collapse-to-pressure is absent in both general boundary scans and deliberately extreme forcing scans.

The first systematic result comes from the persistence-boundary scan in `artifacts/runs/ode_persistence_boundary_scan_v1/classification_summary.csv`. That batch produced mixtures of `oscillatory_persistent`, `persistent_steady`, and `other_transitional` outcomes across the staged parameter sweeps. Importantly, the associated diagnostic note in `artifacts/runs/ode_persistence_boundary_scan_v1/diagnostic_note.md` records that no `collapse_to_pressure` cases were observed in the scanned local region. The second result tightens the negative test: the forced-collapse extreme scan in `artifacts/runs/ode_forced_collapse_extreme_scan_v1/classification_summary.csv` also failed to produce collapse-to-pressure even when residue support was removed, growth was weakened, and suppressive terms were pushed to much stronger values. Its diagnostic note reaches the same conclusion: within the tested ODE region, the system appears collapse-resistant rather than collapse-prone.

That negative result alone would already justify a technical paper, but the current repository contains a more specific and more interesting low-state result. In the floor-extraction scan, governed outputs in `artifacts/runs/ode_epsilon_floor_extraction_scan_v1/top_floor_candidate_runs.csv` show that the tracked variable can be driven into a reproducible low-epsilon regime with floor estimates near `7.84e-3`. This does not amount to a proof of a universal lower bound, but it does show that, under the present operational measurement rules, the local system approaches a stable low-epsilon regime rather than disappearing into collapse. The follow-up refinement scan then sharpens the interpretation. The governed outputs in `artifacts/runs/ode_epsilon_floor_refinement_scan_v1/classification_summary.csv` and `artifacts/runs/ode_epsilon_floor_refinement_scan_v1/top_refined_floor_candidates.csv` indicate that the strongest refined candidates are best classified as `near_floor_convergent`, with best refined floor estimates near `7.05e-3` and no resolved final-window bandwidth at the strongest tested refinement settings.

The central contribution of Paper 1 is therefore not a broad metaphysical thesis but a bounded technical result. The paper presents a fresh governed simulation framework for the local epsilon-rho-residue system, maps its persistent and transitional ODE regimes, documents the absence of collapse-to-pressure in the tested scan region, and identifies a reproducible near-floor regime whose present best-supported interpretation is convergent rather than oscillatory. Those findings are sufficient to motivate the next stage of work, but they remain local, numerical, and deliberately provisional.

The remainder of the paper is organized as follows. Section 2 defines the model and its representation assumptions. Section 3 describes the experiment design and run governance. Section 4 summarizes the numerical implementation. Section 5 presents the current ODE results, with emphasis on persistence, non-collapse under extreme forcing, and near-floor refinement. Section 6 discusses what these results do and do not justify. Section 7 states the present limitations and the next technical steps.

## 2. Model Definition

The draft model definition should be written from `docs/model/governing_equations.md` and the still-incomplete `docs/model/variable_table.md`. For this first-pass manuscript draft, this section remains a placeholder pending completion of the variable table and final wording cleanup.

## 3. Experiment Design

The experiment design section should summarize the governed scan families now present in the repository:

- persistence-boundary scans
- forced-collapse extreme scans
- epsilon-floor extraction scans
- epsilon-floor refinement scans

This section remains a placeholder in the current first pass because the outline and results narrative are already usable, but the section should still be expanded before treating this file as a submission-ready manuscript draft.

## 4. Numerical Implementation

The numerical implementation section should describe the current governed ODE stack:

- ODE right-hand side in `sim/src/model.py`
- integrators in `sim/src/integrators.py`
- classification logic in `sim/src/classifier.py`
- metric construction in `sim/src/metrics.py`
- governed run writing in `sim/src/io_schema.py`
- single-run execution in `sim/src/run_driver.py`
- governed batch execution in `sim/src/batch_runner.py`

This section also remains a placeholder for now. The paper should eventually give a concise technical summary of RK4 use, timestep policies, horizon choices, manifest capture, and classification rules.

## 5. Results

### 5.1 Persistence across the scanned local ODE region

The governed ODE scans presently support a clear first conclusion: across the tested local parameter region, the system persistently avoids collapse-to-pressure. The persistence-boundary batch in `artifacts/runs/ode_persistence_boundary_scan_v1/classification_summary.csv` shows that the ODE layer organizes into `oscillatory_persistent`, `persistent_steady`, and `other_transitional` outcomes depending on scan family and initial condition choice. Stage `A1_support_weakening_scan` remains strongly oscillatory for `moderate_balanced` and `small_epsilon` starts, while `epsilon_biased` initial conditions open a larger transitional subset. Stages `A2` and `A3` broaden the mix of steady, oscillatory, and transitional behavior, indicating that the local system does undergo structured regime change even where it does not collapse.

This matters because it shows that the system is not merely frozen into one numerical behavior. The governed scans already reveal structured dependence on support, suppression, and growth terms, which means Paper 1 can justifiably frame its main result as a regime-mapping exercise rather than a single-regime report.

### 5.2 Failure to induce collapse under extreme forcing

The second result is stronger because it addresses the obvious objection directly: perhaps the initial parameter scans were simply too mild to expose collapse. The forced-collapse extreme batch was constructed precisely to test that possibility by removing residue support, starving growth, and applying stronger suppressive terms. Yet the governed outputs in `artifacts/runs/ode_forced_collapse_extreme_scan_v1/classification_summary.csv` still show no `collapse_to_pressure` cases. Instead, the batch is dominated by `persistent_steady` outcomes, with only a small `other_transitional` subset in the earlier stages. The most aggressive stage, `E4_combined_extreme_break_test`, is entirely `persistent_steady` across all three tested initial-condition families.

This is an important result because it narrows the interpretation space. It does not prove that collapse is impossible in every parameter region. It does show, however, that collapse is not easily obtained in the currently governed local ODE region, even when the scan is explicitly designed to break persistence.

### 5.3 Identification of a low-epsilon near-floor regime

The absence of collapse does not mean the system stays far from zero. The floor-extraction scan was designed to press the system toward the smallest operationally reachable epsilon regime without prematurely naming that scale. The governed outputs in `artifacts/runs/ode_epsilon_floor_extraction_scan_v1/classification_summary.csv` classify all scan families as `near_floor_persistent`. The strongest candidates in `artifacts/runs/ode_epsilon_floor_extraction_scan_v1/top_floor_candidate_runs.csv` cluster around `epsilon_floor_estimate ≈ 0.007840429190601898`, with zero resolved final-window bandwidth under the current measurement rules for the top rows.

At the level of Paper 1, the correct statement is modest but meaningful: the local ODE system can be driven into a reproducible low-epsilon regime that remains nonzero and bounded in the current governed scans. That is stronger than merely saying that collapse failed; it identifies a specific low-state regime that can be measured and revisited under refinement.

### 5.4 Refinement of the near-floor interpretation

The most important update relative to earlier project expectations is that the current refinement results do not support the oscillatory-band hypothesis as the leading interpretation. The refinement batch in `artifacts/runs/ode_epsilon_floor_refinement_scan_v1/classification_summary.csv` classifies all refined candidate families as `near_floor_convergent`. This includes the local box refinement (`R1`), time-horizon refinement (`R2`), timestep convergence probes (`R3`), and micro-initial-condition resolution probes (`R4`).

The strongest refined candidates are listed in `artifacts/runs/ode_epsilon_floor_refinement_scan_v1/top_refined_floor_candidates.csv`. The top rows converge on `epsilon_floor_estimate ≈ 0.00705393487903215`, with `near_floor_bandwidth = 0.0` and `near_floor_oscillation_amplitude = 0.0` at the strongest tested refinement settings. These top candidates occur under smaller timesteps and longer horizons, which weakens the case that the previously observed low-epsilon behavior was a coarse numerical artifact or a broad stable oscillatory band.

The refinement data therefore support a more precise current statement: within the tested local ODE region, the strongest low-epsilon candidates converge toward a narrow nonzero floor estimate rather than maintaining a resolved oscillatory band in the final window.

### 5.5 Resolution and sensitivity

The refinement batch also begins to address whether the near-floor structure is stable under tighter numerical and initial-condition scrutiny. The relevant files are:

- `artifacts/runs/ode_epsilon_floor_refinement_scan_v1/near_floor_band_stability_table.csv`
- `artifacts/runs/ode_epsilon_floor_refinement_scan_v1/dt_convergence_table.csv`
- `artifacts/runs/ode_epsilon_floor_refinement_scan_v1/ic_resolution_table.csv`

These outputs are sufficient to support a cautious sensitivity claim: the low-epsilon regime persists under the tested horizon extensions, timestep reductions, and micro-perturbation probes. What they do not yet justify is a final claim that the smallest resolvable epsilon increment has been exhaustively characterized. The `delta_epsilon_min_resolved` quantity is now produced operationally, but it still belongs to an ongoing refinement program rather than a fully closed numerical-analysis result.

## 6. Discussion

The present governed ODE results support three disciplined interpretations. First, the tested local system is persistence-favoring rather than collapse-favoring over the parameter region examined so far. Second, low-epsilon behavior should not be conflated with collapse, because the scans repeatedly identify bounded nonzero near-floor states rather than extinction. Third, the best current evidence supports a convergent near-floor interpretation more strongly than a stable oscillatory-band interpretation.

What these results do **not** justify is equally important. They do not establish a universal lower bound across all parameter space. They do not show that zero is impossible in every related system. They do not transfer automatically to PDE dynamics. And they do not complete the numerical-analysis story for all possible tolerances, horizons, and resolution settings. Paper 1 should therefore frame the current outcome as a governed local result: a reproducible near-floor ODE regime has been identified and refined, but broader claims remain open.

## 7. Limitations

- The manuscript currently reports only ODE evidence.
- The variable table in `docs/model/variable_table.md` remains incomplete.
- Paper-ready figures are not yet generated.
- The numerical refinement evidence is strong enough for a first paper draft, but not yet exhaustive enough for maximal convergence claims.
- The repository diagnostics should still be tightened so that convergent near-floor interpretation is stated as explicitly in the batch notes as it is in the manuscript draft.

## 8. Conclusion

Paper 1 can now support a technically disciplined first conclusion. The governed local ODE system exhibits broad persistent and transitional structure across the tested parameter region. Collapse-to-pressure was not observed in either the persistence-boundary scans or the forced-collapse extreme scans. A reproducible low-epsilon near-floor regime was then identified and measured operationally. Under subsequent refinement, the strongest candidates support a convergent near-floor interpretation with best refined estimates near `7.05e-3`.

This is enough to justify the paper as a technical entry point: it documents a fresh governed simulation framework, a persistence-dominated local ODE regime map, and a refined low-epsilon result that is nontrivial and reproducible. It is not yet enough to justify universal claims, PDE-level conclusions, or final interpretive closure. Those remain the next stage of work.
