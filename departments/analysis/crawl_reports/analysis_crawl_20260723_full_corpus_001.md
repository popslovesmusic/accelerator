# Analysis Crawl Report: Full Corpus State

## Scope

This bounded crawl inspected the Analysis Department SSOT and local rules, the live master work index, research-debt registry, D-semantics obligation registry, program-state and recommendation reports, Colab archive registry, induction and claim registries, lexicon gap queue, and the current analysis campaign artifacts. Historical and bounded result states were preserved as reported.

The crawl used current repository files as source evidence. It did not execute campaigns, close obligations, promote claims, or modify canonical registries.

## Directly Observed / Defined

- The master work index contains 91 item records, while its summary reports `total_items: 82` and its execution summary reports 90 completed non-archived items.
- The program-state report independently reports 91 total work-index items, 90 completed, one archived, zero blocked, and zero needing mapping.
- The live research-debt registry contains seven records: six resolved runtime debts and one open moderate D-semantics debt, `DEBT_D_SEMANTICS_PROOF_001`.
- The D-semantics registry contains five open obligations: domain/codomain, context threshold, typed transition preservation, representable distinction preservation, and non-collapse boundary.
- The nine registered Colab archives remain bounded C2 outputs. Notebook 15 is C2 theorem-candidate evidence; Notebooks 17–20 include explicit counterexamples or definition and replication limits.
- The lexicon gap queue contains 223 records: 133 provisional C1 definitions and 90 resolved-to-canonical records. No unresolved status was found in the inspected queue.
- The DB freshness gate is `fresh / allow`, and the working tree was clean before this report was written.

## What Was Learned

The repository has two distinct state layers. The work index is operationally closed for unclassified work, while source registries retain active, bounded, and open research scopes. This is consistent with the department SSOT projection rule, but the work-index summary counters are stale or internally inconsistent and require a metadata repair review.

The empirical program has produced a coherent bounded pattern: topology, articulation, organizational projection, residue, exclusion, and conservation claims are all constrained by finite model classes, operational definitions, missing replication, or counterexamples. These results support continued formalization and adversarial testing, not unrestricted theorem promotion.

## What Was Not Learned

- No universal theorem about continuation geometry, projection monotonicity, residue determination, or distinction conservation was established.
- The open D obligations were not discharged by the crawl or by the notebook archives.
- The work-index counter discrepancy cannot be classified as harmless generated metadata without reconciling the source scan and summary-generation rule.
- Lexicon C1 status does not establish L2 validation or canonical semantic equivalence.

## Findings by Discovery Class

### `GOVERNANCE_DEFECT`

`master_work_index.json` has contradictory aggregate metadata: 91 item records versus `summary.total_items = 82`. Its summary by execution state also does not match the item-level statuses. This is a reproducibility and routing defect.

Epistemic status: `OBSERVED`  
Proof status: `NOT_ATTEMPTED`  
Required action: regenerate or reconcile the summary from item records under the authoritative projection rule, then validate that no source item was dropped.

### `PROOF_OBLIGATION`

The five D-semantics obligations remain open and block theorem promotion for the D evaluation/projection semantics.

Epistemic status: `SOURCE_REPORTED`  
Proof status: `OBLIGATIONS_IDENTIFIED`  
Required action: execute the existing AOW v2 work packages in dependency order, beginning with domain/codomain and context-threshold formalization.

### `EMPIRICAL_ANOMALY`

Notebook result archives repeatedly report C2 evidence with counterexamples, finite-domain limits, operational definitions, absent immutable pre-execution specifications, and pending approved-tool replication. These are not defects in the results by themselves; they define the current claim ceiling.

Epistemic status: `EMPIRICALLY_SUPPORTED`  
Proof status: `INDEPENDENT_REVIEW_REQUIRED`

### `GENERALIZATION_CANDIDATE`

Across the notebook sequence, stronger claims become less stable when the tested object is projected into a broader domain: generic topology retains bounded signal, but projection monotonicity and strong residue-determination formulations encounter counterexamples. A candidate general principle is that projection enriches representational organization only under an explicitly typed preservation relation; without that relation, apparent emergence may be representational, operational, or genuinely structural.

Epistemic status: `CONJECTURED`  
Proof status: `OBLIGATIONS_IDENTIFIED`

## Open Debt and Blocking Effects

| Item | State | Blocking effect | Recommended discharge |
|---|---|---|---|
| `DEBT_D_SEMANTICS_PROOF_001` | Open, moderate | Blocks D-semantics theorem promotion | Execute `OBL-D-001A` through `OBL-D-001E` work packages |
| Master-index aggregate mismatch | Unresolved metadata defect | Weakens reproducibility of work-count and priority reports | Recompute item-level summary and run global validation |
| Notebook replication and specification gaps | C2 archive blockers | Prevent elevation above bounded evidence | Add immutable experiment specifications and approved-tool replication |
| Notebook counterexamples and definition dependence | Active evidence limitations | Prevents universal or causal interpretation | Preserve counterexamples and formalize exact claim boundaries |

## Synthesis and Hypothesis

### Mapping

The current evidence maps:

`fixed primitive claim` -> `typed projection or operational model` -> `observable organization or residue` -> `bounded topology/statistics` -> `counterexample or preservation test`.

### Preserved Structure

Across the campaigns, the preserved object is not a universal interpretation. It is the requirement that each projection retain explicit domain, admissibility, type, and evidence boundaries.

### Uncertainty and Competing Explanations

Observed organization may arise from actual higher-degree freedom, from the operational encoding of the projection, from finite model selection, or from proxy features. These explanations remain distinguishable only through typed preservation tests, matched controls, independent replication, and countermodel search.

### Falsification Condition

The candidate projection principle is weakened or rejected if a lower-degree representation preserves all relevant continuation, closure, distinction, and symmetry information for every tested higher-degree organization, or if the apparent higher-degree classes disappear under independently specified encodings and grouped evaluation.

## Recommended Next Action

`FORMALIZE`: reconcile the master-index aggregate metadata first, then execute `OBL-D-001A` and `OBL-D-001B` sequentially. The metadata repair is a prerequisite for trustworthy progress accounting; the D domain and threshold definitions are the highest-leverage mathematical prerequisites.

## What This Report Does Not Authorize

This report does not discharge research debt, close work items, promote any theorem or lexicon term, alter canonical registries, or treat C2 notebook results as formal proof or external truth.

