# Residue State vs Memoryless and Finite-History Controls

## 1. Scope
This report answers the bounded program question: does maintaining an explicit residue state that accumulates past experience produce behavior that cannot be explained equally well by memoryless decisions or finite-history memory alone?

Scope is limited to on-disk Acellorator artifacts inspected on 2026-07-21. No new simulation was run. Local governance was found and applied from `GEMINI.md`; `AGENTS.md` was also applied. DB governance runtime was queried before documentation changes. The DB allowed textbook routing but deferred the new report path and warned that the DB snapshot is stale, so canonical files and recoverable result paths remain authoritative for this report.

## 2. Directly Observed/Defined
**Finding:** The current program does not contain validated evidence sufficient to support the strong hypothesis that explicit accumulated residue produces behavior that cannot be explained equally well by memoryless or finite-history alternatives.

Evidence:
- `configs/non_markov_organization_campaign.json` defines the right comparison design: `last_state_only_control`, `history_shuffle_control`, `history_truncation_control`, and `full_history_accumulative_run`. It is scoped as `C2_TESTABLE_CANDIDATE`, not validated evidence.
- `results/non_markov_organization_validation/non_markov_summary.md` states the campaign is `SCAFFOLD_READY` with `NO_EVIDENCE_YET`.
- `results/non_markov_organization_validation/non_markov_results.json` contains `"runs": []`.
- `tools/strict_memoryless_control_v1_cpp/validation/certification_manifest.json` classifies the strict memoryless control tool as `C1` and records falsification, numerical stability, uncertainty, and provenance verification as false.
- `results/2026-06-10_run01_LFCR_002_TRIAD_KILL/paper.md` reports a 2,100-run falsification attack across CA, PDE, and graph mechanisms and classifies the broad residue/triad/orientation necessity claim as `FALSIFIED`.
- `results/2026-06-10_run01_LFCR_002_TRIAD_KILL/artifacts/ablation_comparison.csv` records `M1_NO_RESIDUE` as ineffective in CA, graph, and PDE; CA no-residue closure is higher than baseline (`0.9576` vs `0.9250`), graph is near baseline (`0.0894` vs `0.0935`), and PDE is equal (`1.0` vs `1.0`).
- `docs/math/law015_channel_memory_reinforcement_history_law.md` defines memory and residue as projections of reinforcement history, not as primitive stored objects.

## 3. Inferred Inside Framework
The strongest supported internal inference is weaker than the proposed hypothesis:

Within the framework, residue and reinforcement history are defined as admissibility-conditioning trace structures. Some artifacts define tests where accumulated history should be compared against memoryless, shuffled-history, and truncated-history controls. However, the available completed evidence does not yet show that explicit accumulated residue is uniquely necessary or non-reducible to simpler controls.

Claim class: **C1-C2 bounded candidate only** for the non-Markov/residue-accumulation hypothesis. The direct comparative test is designed but not populated with runs.

## 4. External Resemblance (Analogy Only)
The program vocabulary resembles memory, hysteresis, non-Markov dynamics, and path dependence. This is analogy only. The inspected evidence does not establish a claim about biological memory, physical memory storage, cognition, or universal non-Markov physical law.

## 5. What It Does NOT Prove
This report does not prove that residue is unnecessary in all Acellorator models. It also does not prove that memoryless or finite-history models are always sufficient.

It does show that the current program evidence does not justify the stronger exclusionary claim: “explicit accumulated residue produces behavior that cannot be explained equally well by memoryless or finite-history memory alone.”

## 6. Failure Modes / Uncertainty
- The direct non-Markov campaign has no runs, so it cannot adjudicate full-history versus last-state, shuffled-history, or truncated-history explanations.
- The strict memoryless control tool is only C1 and lacks falsification and provenance verification.
- LFCR-002 falsifies a broad closure-necessity claim, but it is not a complete finite-history-memory equivalence search.
- Some textbook and narrative passages retain stronger historical wording; current governance notes restrict provisional array-graph and whole-expression campaigns from theorem promotion or evidence endorsement.
- A decisive future test would need matched full-residue, memoryless, last-state-only, shuffled-history, and finite-window controls, with enough seeds, independent measurement, and model-class replication.

## 7. Report Verdict
**Answer:** Not yet. The program contains definitions and proposed tests for the hypothesis, but the available on-disk evidence does not currently demonstrate residue-specific behavior that cannot be explained equally well by memoryless or finite-history alternatives. The most relevant completed falsification evidence pushes in the opposite direction for the broad necessity claim.

