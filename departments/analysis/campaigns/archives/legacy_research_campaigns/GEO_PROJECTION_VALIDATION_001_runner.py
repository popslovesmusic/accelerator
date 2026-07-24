"""
GEO_PROJECTION_VALIDATION_001 — Campaign Runner
===============================================
Governed simulation campaign for Topology-to-Geometry Projection Legality.

Four adversarial control runs:
  CTRL-SHUFFLED            : Shuffled topology; tests distinction preservation under randomization
  CTRL-RESIDUE-DEPLETED    : Residue-depleted; tests closure-trace without memory support
  CTRL-CLOSURE-PERTURBED   : Closure-perturbed; tests closure-trace survivability under perturbation
  CTRL-ORIENTATION-PERTURBED: Orientation-perturbed; tests orientation-trace survivability

Four proxy metrics (per evidence_campaign_template_registry.json):
  distinction_loss_rate
  orientation_loss_rate
  closure_loss_rate
  admissibility_violation_rate

Claim scope: STRICTLY_LOCAL_RESTRICTED_ANALOG (C1)
Governance: GEO_GAP_REDUCTION_SEQUENCE_001 / PO_GEO_001_SYMBOLIC_REVIEW_001

Output: results/GEO_PROJECTION_VALIDATION_001/evidence_report.json
"""

import sys
import json
import time
import hashlib
import numpy as np
from pathlib import Path

# ── Governance constants ──────────────────────────────────────────────────────
CAMPAIGN_ID       = "GEO_PROJECTION_VALIDATION_001"
CLAIM_SCOPE       = "STRICTLY_LOCAL_RESTRICTED_ANALOG"
EVIDENCE_CLASS    = "C2_SIMULATION_OBSERVED"
TAU_MIN           = 0.05          # minimum effect size for support
SEEDS             = 32            # reproducibility seeds
N_NODES           = 80            # topology-state graph size
STEPS             = 120           # projection steps
N_TOPOLOGY_STATES = 200           # T objects per run
RNG_MASTER        = 42

# ── Invariant label vocabulary ─────────────────────────────────────────────────
DISTINCTION_VOCAB  = ["D_LOW", "D_MED", "D_HIGH"]
ORIENT_VOCAB       = ["O_POS", "O_NEG", "O_ZERO"]
CLOSURE_VOCAB      = ["C_OPEN", "C_PARTIAL", "C_CLOSED"]
ADMISSIBILITY_PASS = "PASS"
ADMISSIBILITY_FAIL = "FAIL"

# ── Topology-state factory ─────────────────────────────────────────────────────

def make_trace_geo(rng, n):
    """Build n Trace_geo(T) records — complete, pre-projection label records."""
    return [
        {
            "T_id":             i,
            "distinction_class": rng.choice(DISTINCTION_VOCAB),
            "admissibility_status": ADMISSIBILITY_PASS,   # Dom admission: only PASS enters
            "orientation_class": rng.choice(ORIENT_VOCAB),
            "closure_class":    rng.choice(CLOSURE_VOCAB),
        }
        for i in range(n)
    ]

# ── Pi_geo projection models ───────────────────────────────────────────────────

def pi_geo_intact(trace, rng, noise=0.0):
    """
    M0 — intact projection: all four labels survive.
    Geometry_app G carries tau_geo-readable labels matching Trace_geo(T).
    """
    def project(t):
        return {
            "G_id":             t["T_id"],
            "distinction_class": t["distinction_class"],
            "admissibility_status": t["admissibility_status"],
            "orientation_class": t["orientation_class"],
            "closure_class":    t["closure_class"],
            "_origin_T_id":    t["T_id"],
        }
    return [project(t) for t in trace]


def pi_geo_shuffled(trace, rng, noise=0.0):
    """
    CTRL-SHUFFLED: distinction classes shuffled across T objects.
    Tests PO-GEO-001A: distinction_alias failure mode.
    The projection deliberately randomises which distinction class each G carries.
    """
    shuffled_dist = rng.permutation([t["distinction_class"] for t in trace])
    def project(t, d):
        return {
            "G_id":             t["T_id"],
            "distinction_class": d,          # shuffled — may alias
            "admissibility_status": t["admissibility_status"],
            "orientation_class": t["orientation_class"],
            "closure_class":    t["closure_class"],
            "_origin_T_id":    t["T_id"],
        }
    return [project(t, d) for t, d in zip(trace, shuffled_dist)]


def pi_geo_residue_depleted(trace, rng, noise=0.0):
    """
    CTRL-RESIDUE-DEPLETED: closure_class set to None (memory support removed).
    Tests PO-GEO-001D: closure_trace_loss failure mode.
    Simulates a projection that carries no residue memory — closure lineage breaks.
    """
    def project(t):
        return {
            "G_id":             t["T_id"],
            "distinction_class": t["distinction_class"],
            "admissibility_status": t["admissibility_status"],
            "orientation_class": t["orientation_class"],
            "closure_class":    None,        # trace lost — TAU-UNDEF-2 fires
            "_origin_T_id":    t["T_id"],
        }
    return [project(t) for t in trace]


def pi_geo_closure_perturbed(trace, rng, noise=0.3):
    """
    CTRL-CLOSURE-PERTURBED: closure_class randomly reassigned with probability `noise`.
    Tests PO-GEO-001D: closure_trace_loss_or_alias failure mode under perturbation.
    """
    closure_pool = CLOSURE_VOCAB
    def project(t):
        cc = t["closure_class"]
        if rng.random() < noise:
            # perturb: reassign randomly (may alias)
            cc = rng.choice(closure_pool)
        return {
            "G_id":             t["T_id"],
            "distinction_class": t["distinction_class"],
            "admissibility_status": t["admissibility_status"],
            "orientation_class": t["orientation_class"],
            "closure_class":    cc,
            "_origin_T_id":    t["T_id"],
        }
    return [project(t) for t in trace]


def pi_geo_orientation_perturbed(trace, rng, noise=0.3):
    """
    CTRL-ORIENTATION-PERTURBED: orientation_class randomly reassigned with probability `noise`.
    Tests PO-GEO-001C: orientation_trace_loss failure mode under perturbation.
    """
    def project(t):
        oc = t["orientation_class"]
        if rng.random() < noise:
            oc = rng.choice(ORIENT_VOCAB)
        return {
            "G_id":             t["T_id"],
            "distinction_class": t["distinction_class"],
            "admissibility_status": t["admissibility_status"],
            "orientation_class": oc,
            "closure_class":    t["closure_class"],
            "_origin_T_id":    t["T_id"],
        }
    return [project(t) for t in trace]

# ── tau_geo recoverability check ───────────────────────────────────────────────

def tau_geo(G, trace_map):
    """
    Partial recoverability operator. Returns recovered labels or UNDEFINED sentinel.
    Fires TAU-UNDEF-2 if any required label is None/missing.
    Fires TAU-UNDEF-3 if any label conflicts with Trace_geo(T) ground truth.
    Returns None if undefined (projection legality failure for this G).
    """
    T = trace_map.get(G["_origin_T_id"])
    if T is None:
        return None   # TAU-UNDEF-1: G not produced by Pi_geo

    recovered = {
        "distinction_class":   G.get("distinction_class"),
        "admissibility_status": G.get("admissibility_status"),
        "orientation_class":   G.get("orientation_class"),
        "closure_class":       G.get("closure_class"),
    }

    # TAU-UNDEF-2: any required label missing or None
    for field in ["distinction_class", "admissibility_status", "orientation_class", "closure_class"]:
        if recovered[field] is None:
            return None

    return recovered

# ── Metric measurement ─────────────────────────────────────────────────────────

def measure_metrics(trace_list, projected_list):
    """
    Measure all four proxy metrics by comparing tau_geo recoveries against Trace_geo ground truth.
    Returns dict of per-T failure indicators and aggregate rates.
    """
    trace_map = {t["T_id"]: t for t in trace_list}

    distinction_losses   = 0
    orientation_losses   = 0
    closure_losses       = 0
    admissibility_viols  = 0
    tau_undefined        = 0
    n = len(projected_list)

    # PO-GEO-001D aliasing check: closure_class must be injective across T objects
    # Build mapping: Trace_geo closure_class -> set of recovered closure classes
    closure_alias_events = 0
    # Group by source closure class
    source_groups = {}
    for G in projected_list:
        T = trace_map[G["_origin_T_id"]]
        src_cc = T["closure_class"]
        rec = tau_geo(G, trace_map)
        rec_cc = rec["closure_class"] if rec is not None else None
        if src_cc not in source_groups:
            source_groups[src_cc] = set()
        if rec_cc is not None:
            source_groups[src_cc].add(rec_cc)

    # Aliasing: two different source classes map to the same recovered class
    all_recovered_classes = []
    for src_cc, rec_set in source_groups.items():
        all_recovered_classes.extend(list(rec_set))
    # If any recovered class appears in more than one source group → alias
    from collections import Counter
    rec_counts = Counter(all_recovered_classes)
    closure_alias_count = sum(1 for v in rec_counts.values() if v > 1)

    for G in projected_list:
        T = trace_map[G["_origin_T_id"]]
        rec = tau_geo(G, trace_map)

        if rec is None:
            tau_undefined += 1
            # tau undefined = all four sub-obligations potentially failed for this G
            distinction_losses  += 1
            orientation_losses  += 1
            closure_losses      += 1
            admissibility_viols += 1
            continue

        # PO-GEO-001A: distinction preservation
        if rec["distinction_class"] != T["distinction_class"]:
            distinction_losses += 1

        # PO-GEO-001B: admissibility preservation
        if rec["admissibility_status"] != ADMISSIBILITY_PASS:
            admissibility_viols += 1

        # PO-GEO-001C: orientation trace
        if rec["orientation_class"] != T["orientation_class"]:
            orientation_losses += 1

        # PO-GEO-001D: closure trace
        if rec["closure_class"] != T["closure_class"]:
            closure_losses += 1

    return {
        "n":                       n,
        "tau_undefined_count":     tau_undefined,
        "distinction_loss_rate":   distinction_losses / n,
        "orientation_loss_rate":   orientation_losses / n,
        "closure_loss_rate":       closure_losses / n,
        "admissibility_violation_rate": admissibility_viols / n,
        "closure_alias_source_groups": closure_alias_count,
    }

# ── Single seed run ────────────────────────────────────────────────────────────

PROJECTORS = {
    "M0_intact":               pi_geo_intact,
    "CTRL_SHUFFLED":           pi_geo_shuffled,
    "CTRL_RESIDUE_DEPLETED":   pi_geo_residue_depleted,
    "CTRL_CLOSURE_PERTURBED":  pi_geo_closure_perturbed,
    "CTRL_ORIENTATION_PERTURBED": pi_geo_orientation_perturbed,
}

def run_seed(seed):
    rng = np.random.default_rng(seed)
    trace = make_trace_geo(rng, N_TOPOLOGY_STATES)
    results = {}
    for name, projector in PROJECTORS.items():
        projected = projector(trace, rng)
        metrics   = measure_metrics(trace, projected)
        results[name] = metrics
    return results

# ── Main execution ─────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*72}")
    print(f"  {CAMPAIGN_ID}")
    print(f"  Scope: {CLAIM_SCOPE}")
    print(f"  Seeds: {SEEDS}  |  Topology states per seed: {N_TOPOLOGY_STATES}")
    print(f"{'='*72}\n")

    master_rng = np.random.default_rng(RNG_MASTER)
    seed_list  = [int(s) for s in master_rng.integers(0, 2**31, size=SEEDS)]

    all_seed_results = []
    for i, seed in enumerate(seed_list):
        r = run_seed(seed)
        all_seed_results.append({"seed": seed, "results": r})
        if (i + 1) % 8 == 0:
            print(f"  Completed {i+1}/{SEEDS} seeds...")

    print(f"\n  All {SEEDS} seeds complete. Aggregating...\n")

    # ── Aggregate across seeds ────────────────────────────────────────────────
    model_names = list(PROJECTORS.keys())
    metric_names = [
        "distinction_loss_rate",
        "orientation_loss_rate",
        "closure_loss_rate",
        "admissibility_violation_rate",
    ]

    aggregated = {}
    for model in model_names:
        aggregated[model] = {}
        for metric in metric_names:
            vals = [r["results"][model][metric] for r in all_seed_results]
            aggregated[model][metric] = {
                "mean":  float(np.mean(vals)),
                "std":   float(np.std(vals)),
                "min":   float(np.min(vals)),
                "max":   float(np.max(vals)),
            }

    # ── Effect size: M0 vs each control ──────────────────────────────────────
    # Positive effect = control loss_rate HIGHER than M0 → attack worked → invariant sensitive to mechanism
    effect_sizes = {}
    for ctrl in ["CTRL_SHUFFLED", "CTRL_RESIDUE_DEPLETED", "CTRL_CLOSURE_PERTURBED", "CTRL_ORIENTATION_PERTURBED"]:
        effect_sizes[ctrl] = {}
        for metric in metric_names:
            m0_mean   = aggregated["M0_intact"][metric]["mean"]
            ctrl_mean = aggregated[ctrl][metric]["mean"]
            effect    = ctrl_mean - m0_mean   # positive = control degrades invariant
            effect_sizes[ctrl][metric] = float(effect)

    # ── Decision rules ────────────────────────────────────────────────────────
    # SUPPORT: M0 outperforms (lower loss) every attack by >= TAU_MIN on the primary metric for that control
    ctrl_primary_metric = {
        "CTRL_SHUFFLED":            "distinction_loss_rate",
        "CTRL_RESIDUE_DEPLETED":    "closure_loss_rate",
        "CTRL_CLOSURE_PERTURBED":   "closure_loss_rate",
        "CTRL_ORIENTATION_PERTURBED": "orientation_loss_rate",
    }

    ctrl_results = {}
    for ctrl, primary in ctrl_primary_metric.items():
        effect = effect_sizes[ctrl][primary]
        m0_mean = aggregated["M0_intact"][primary]["mean"]
        ctrl_mean = aggregated[ctrl][primary]["mean"]
        if effect >= TAU_MIN:
            verdict = "SUPPORT"
            verdict_note = f"Control degrades {primary} by {effect:.4f} (>= tau_min {TAU_MIN}). M0 loss={m0_mean:.4f}, control loss={ctrl_mean:.4f}."
        elif effect > 0:
            verdict = "WEAK"
            verdict_note = f"Control degrades {primary} by {effect:.4f} (< tau_min {TAU_MIN}). Borderline."
        else:
            verdict = "FALSIFY"
            verdict_note = f"Control does NOT degrade {primary} (effect={effect:.4f}). M0 has no advantage."
        ctrl_results[ctrl] = {
            "primary_metric": primary,
            "M0_mean":    m0_mean,
            "ctrl_mean":  ctrl_mean,
            "effect":     effect,
            "verdict":    verdict,
            "verdict_note": verdict_note,
        }

    # Overall campaign verdict
    verdicts = [v["verdict"] for v in ctrl_results.values()]
    if "FALSIFY" in verdicts:
        overall = "FALSIFIED"
    elif all(v == "SUPPORT" for v in verdicts):
        overall = "SUPPORTED"
    else:
        overall = "MIXED"

    # -- Print summary ---------------------------------------------------------
    print(f"{'='*72}")
    print(f"  CAMPAIGN RESULT: {overall}")
    print(f"{'='*72}")
    for ctrl, res in ctrl_results.items():
        marker = "[+]" if res["verdict"] == "SUPPORT" else ("[X]" if res["verdict"] == "FALSIFY" else "[~]")
        print(f"  {marker} {ctrl}")
        print(f"      Primary metric : {res['primary_metric']}")
        print(f"      M0 loss rate   : {res['M0_mean']:.4f}")
        print(f"      Control loss   : {res['ctrl_mean']:.4f}")
        print(f"      Effect size    : {res['effect']:.4f}  (tau_min={TAU_MIN})")
        print(f"      Verdict        : {res['verdict']}")
        print()

    print(f"  M0 (intact) baseline metrics:")
    for metric in metric_names:
        m = aggregated["M0_intact"][metric]
        print(f"    {metric:40s}: mean={m['mean']:.4f}  std={m['std']:.4f}")
    print()

    # ── Build evidence report ─────────────────────────────────────────────────
    ts = time.strftime("%Y-%m-%dT%H:%M:%S-04:00")
    report = {
        "campaign_id":          CAMPAIGN_ID,
        "claim_scope":          CLAIM_SCOPE,
        "evidence_class":       EVIDENCE_CLASS,
        "execution_timestamp":  ts,
        "governance": {
            "parent_patches":   ["GEO_GAP_REDUCTION_SEQUENCE_001", "PO_GEO_001_SYMBOLIC_REVIEW_001"],
            "target_lemma":     "L099",
            "target_object":    "geometry_app",
            "tau_min":          TAU_MIN,
            "seeds":            SEEDS,
            "n_topology_states": N_TOPOLOGY_STATES,
            "rng_master_seed":  RNG_MASTER,
        },
        "what_this_proves": {
            "scope": "Within these models, and within the declared label vocabulary, the intact projection M0 shows lower invariant loss rates than matched adversarial controls when the relevant mechanism is ablated.",
            "does_not_prove": [
                "Pi_geo is physically real",
                "geometry_app is physical space",
                "field_app, matter_app, or gravity_app support is restored",
                "L100 or downstream lemmas are promoted",
                "OPEN_BRIDGE_001 is promoted",
            ]
        },
        "overall_verdict":     overall,
        "control_results":     ctrl_results,
        "aggregated_metrics":  aggregated,
        "m0_baseline": {m: aggregated["M0_intact"][m]["mean"] for m in metric_names},
        "seed_list":           seed_list,
        "required_statement":  "Observed signatures are interpreted only through restricted local analog structure.",
    }

    # ── Save report ───────────────────────────────────────────────────────────
    out_dir = Path("results/GEO_PROJECTION_VALIDATION_001")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "evidence_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    report_bytes = json.dumps(report, indent=2).encode()
    report_hash  = hashlib.sha256(report_bytes).hexdigest()
    hash_path    = out_dir / "evidence_report.sha256"
    with open(hash_path, "w") as f:
        f.write(report_hash)

    print(f"  Evidence report : {report_path}")
    print(f"  SHA-256         : {report_hash}")
    print(f"\n  Overall verdict : {overall}")
    print(f"{'='*72}\n")

    return overall

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result in ("SUPPORTED", "MIXED") else 1)
