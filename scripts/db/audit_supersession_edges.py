import argparse
import json
import os
import sqlite3
from collections import Counter, defaultdict
import datetime


def _utc_now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _fetch_edges(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
          se.id,
          se.from_artifact_id,
          se.to_artifact_id,
          se.relation,
          COALESCE(se.confidence, 'weak') AS confidence,
          se.evidence_path,
          se.reason,
          se.timestamp,
          se.indexed_at,
          a_from.path AS from_path,
          a_to.path AS to_path
        FROM supersession_edges se
        LEFT JOIN artifacts a_from ON a_from.id = se.from_artifact_id
        LEFT JOIN artifacts a_to ON a_to.id = se.to_artifact_id
        """
    )
    return [dict(r) for r in cur.fetchall()]


def _duplicate_edges(edges):
    seen = {}
    dups = []
    for e in edges:
        key = (e.get("from_artifact_id"), e.get("to_artifact_id"), e.get("relation"))
        if key in seen:
            dups.append(
                {
                    "edge_id": e.get("id"),
                    "duplicate_of_edge_id": seen[key],
                    "from_artifact_id": e.get("from_artifact_id"),
                    "to_artifact_id": e.get("to_artifact_id"),
                    "relation": e.get("relation"),
                }
            )
        else:
            seen[key] = e.get("id")
    return dups


def _find_two_cycles(edges, limit=200):
    # Identify A->B and B->A as cycle candidates (regardless of relation/confidence)
    forward = defaultdict(set)
    for e in edges:
        a = e.get("from_artifact_id")
        b = e.get("to_artifact_id")
        if a is None or b is None:
            continue
        forward[a].add(b)

    cycles = []
    visited_pairs = set()
    for a, outs in forward.items():
        for b in outs:
            if a == b:
                continue
            if a in forward.get(b, set()):
                pair = tuple(sorted((a, b)))
                if pair in visited_pairs:
                    continue
                visited_pairs.add(pair)
                cycles.append({"type": "2-cycle", "nodes": [a, b]})
                if len(cycles) >= limit:
                    return cycles
    return cycles


def audit_supersession_edges(db_path, sample=50):
    report = {
        "timestamp": _utc_now_iso(),
        "db_path": db_path,
        "supersession_edge_audit": {
            "status": "pass",
            "total_edges": 0,
            "by_relation": {},
            "by_confidence": {},
            "reference_integrity": {
                "missing_from_artifact": 0,
                "missing_to_artifact": 0,
                "self_edges": 0,
            },
            "cycle_candidates": [],
            "duplicate_edges": [],
            "risk_summary": [],
            "samples": [],
            "recommendations": [],
        },
    }

    if not os.path.exists(db_path):
        report["supersession_edge_audit"]["status"] = "fail"
        report["supersession_edge_audit"]["risk_summary"].append(
            {"rule": "db_missing", "severity": "fail", "detail": f"Database file missing: {db_path}"}
        )
        return report

    conn = _connect(db_path)
    try:
        edges = _fetch_edges(conn)
    finally:
        conn.close()

    total = len(edges)
    report["supersession_edge_audit"]["total_edges"] = total

    by_relation = Counter(e.get("relation") or "unknown" for e in edges)
    by_conf = Counter((e.get("confidence") or "weak").lower() for e in edges)
    report["supersession_edge_audit"]["by_relation"] = dict(by_relation)
    report["supersession_edge_audit"]["by_confidence"] = dict(by_conf)

    missing_from = sum(1 for e in edges if not e.get("from_path"))
    missing_to = sum(1 for e in edges if not e.get("to_path"))
    self_edges = sum(1 for e in edges if e.get("from_artifact_id") == e.get("to_artifact_id") and e.get("from_artifact_id") is not None)
    report["supersession_edge_audit"]["reference_integrity"]["missing_from_artifact"] = missing_from
    report["supersession_edge_audit"]["reference_integrity"]["missing_to_artifact"] = missing_to
    report["supersession_edge_audit"]["reference_integrity"]["self_edges"] = self_edges

    dups = _duplicate_edges(edges)
    report["supersession_edge_audit"]["duplicate_edges"] = dups[: min(len(dups), 200)]

    cycles = _find_two_cycles(edges, limit=200)
    report["supersession_edge_audit"]["cycle_candidates"] = cycles

    # Risk rules
    risk = []
    status = "pass"

    def add_risk(rule, severity, detail, count=None):
        nonlocal status
        entry = {"rule": rule, "severity": severity, "detail": detail}
        if count is not None:
            entry["count"] = int(count)
        risk.append(entry)
        if severity == "fail":
            status = "fail"
        elif severity == "warning" and status == "pass":
            status = "warning"

    if self_edges > 0:
        add_risk("self_edges", "fail", "Self-referential edges detected.", self_edges)
    if missing_from > 0 or missing_to > 0:
        add_risk(
            "missing_artifact_refs",
            "fail",
            "Edges reference artifact IDs that do not resolve to artifacts rows (LEFT JOIN missing).",
            missing_from + missing_to,
        )
    if len(dups) > 0:
        add_risk("duplicate_edges", "warning", "Duplicate (from,to,relation) edges detected.", len(dups))
    if len(cycles) > 0:
        add_risk("cycle_candidates", "warning", "2-cycle candidates detected (A->B and B->A).", len(cycles))

    weak = by_conf.get("weak", 0)
    probable = by_conf.get("probable", 0)
    verified = by_conf.get("verified", 0)
    if total > 0:
        weak_ratio = weak / total
        verified_ratio = verified / total
        probable_ratio = probable / total

        if weak_ratio > 0.75:
            add_risk("weak_confidence_ratio_over_0_75", "warning", "Weak-confidence edges dominate; treat lineage as highly advisory.", weak)
        if verified_ratio < 0.05:
            add_risk("verified_confidence_ratio_under_0_05", "warning", "Very few edges are verified; do not over-trust lineage.", verified)

        report["supersession_edge_audit"]["reference_integrity"]["weak_confidence_ratio"] = weak_ratio
        report["supersession_edge_audit"]["reference_integrity"]["probable_confidence_ratio"] = probable_ratio
        report["supersession_edge_audit"]["reference_integrity"]["verified_confidence_ratio"] = verified_ratio

    # High-risk patterns: pattern-only edges (no evidence_path + no reason)
    pattern_only = [
        e
        for e in edges
        if not (e.get("evidence_path") or "").strip()
        and not (e.get("reason") or "").strip()
        and (e.get("confidence") or "weak").lower() in {"weak", "probable"}
    ]
    if pattern_only and total:
        add_risk(
            "pattern_only_edges",
            "advisory",
            "Edges appear pattern-detected (no evidence_path/reason). Keep advisory in retrieval explanations.",
            len(pattern_only),
        )

    # Retrieval impact warning: a conservative note if weak+probable dominate.
    if total and (weak + probable) / total > 0.8:
        add_risk(
            "retrieval_impact_warning",
            "warning",
            "Lineage edges are mostly non-verified; orientation-aware retrieval must avoid treating lineage as authoritative.",
        )

    report["supersession_edge_audit"]["risk_summary"] = risk
    report["supersession_edge_audit"]["status"] = status

    # Samples: deterministic-ish (by id)
    edges_sorted = sorted(edges, key=lambda e: (e.get("relation") or "", (e.get("confidence") or ""), e.get("id") or 0))
    sample_n = max(0, int(sample))
    if sample_n:
        step = max(1, len(edges_sorted) // sample_n) if edges_sorted else 1
        sampled = edges_sorted[::step][:sample_n]
        report["supersession_edge_audit"]["samples"] = [
            {
                "id": e.get("id"),
                "from": e.get("from_path") or {"missing_artifact_id": e.get("from_artifact_id")},
                "to": e.get("to_path") or {"missing_artifact_id": e.get("to_artifact_id")},
                "relation": e.get("relation"),
                "confidence": (e.get("confidence") or "weak").lower(),
                "evidence_path": e.get("evidence_path"),
                "reason": e.get("reason"),
            }
            for e in sampled
        ]

    # Recommendations (non-mutating)
    recs = []
    if status in {"warning", "fail"}:
        recs.append("Treat `supersession_edges` as advisory lineage metadata; do not use as SSOT for deletion/migration decisions.")
    if total and verified == 0:
        recs.append("Consider adding a mechanism to record explicit verified supersession declarations (evidence_path + confidence=verified).")
    if missing_from or missing_to:
        recs.append("Enable foreign key enforcement (`PRAGMA foreign_keys=ON`) in ingestion tools or add periodic cleanup reports.")
    if len(dups) > 0:
        recs.append("Consider adding a UNIQUE constraint on (from_artifact_id,to_artifact_id,relation) or dedupe in ingestion.")
    report["supersession_edge_audit"]["recommendations"] = recs

    return report


def main():
    parser = argparse.ArgumentParser(description="Audit supersession_edges quality and risks (advisory lineage metadata).")
    parser.add_argument("--db", default="registry/db/acellorator_index.sqlite", help="Path to SQLite database.")
    parser.add_argument("--sample", type=int, default=50, help="Number of sample edges to include in report output.")
    parser.add_argument("--out", default="", help="Optional output path for JSON report.")
    args = parser.parse_args()

    report = audit_supersession_edges(args.db, sample=args.sample)
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"

    if args.out:
        out_path = args.out
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "x", encoding="utf-8") as f:
            f.write(text)
        print(f"Wrote supersession edge audit report to {out_path}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
