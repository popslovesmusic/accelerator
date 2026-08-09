# Orientation Scoring Logic

ORIENTATION_STATUS_WEIGHTS = {
    "current_command_evidence": 1.0,
    "canonical_active": 0.95,
    "active_runtime": 0.9,
    "unverified_residue": 0.45,
    "historical_residue": 0.35,
    "archived": 0.25,
    "deprecated": 0.15,
    "superseded": 0.1,
    "invalidated": 0.0
}

AUTHORITY_SCOPE_WEIGHTS = {
    "lexicon": 1.0,
    "registry": 0.95,
    "command_audit": 0.9,
    "tool_validation": 0.8,
    "config": 0.65,
    "doc": 0.45,
    "historical_report": 0.25,
    "unknown": 0.2
}

EVIDENCE_CONFIDENCE_WEIGHTS = {
    "verified": 1.0,
    "conflicting": 0.55,
    "unverified_residue": 0.35,
    "verified_as_residue_only": 0.3,
    "not_checked": 0.2,
    "missing": 0.0
}

def calculate_orientation_score(orientation_status, authority_scope, evidence_confidence, freshness_score=0.5, text_match_score=0.0):
    """
    Default score formula: 
    score = 0.35*orientation_status + 0.25*authority_scope + 0.20*evidence_confidence + 0.10*freshness + 0.10*text_match
    """
    w_os = ORIENTATION_STATUS_WEIGHTS.get(orientation_status, 0.2)
    w_as = AUTHORITY_SCOPE_WEIGHTS.get(authority_scope, 0.2)
    w_ec = EVIDENCE_CONFIDENCE_WEIGHTS.get(evidence_confidence, 0.2)
    
    score = (0.35 * w_os) + (0.25 * w_as) + (0.20 * w_ec) + (0.10 * freshness_score) + (0.10 * text_match_score)
    
    return {
        "score": round(score, 4),
        "breakdown": {
            "orientation_status": round(0.35 * w_os, 4),
            "authority_scope": round(0.25 * w_as, 4),
            "evidence_confidence": round(0.20 * w_ec, 4),
            "freshness": round(0.10 * freshness_score, 4),
            "text_match": round(0.10 * text_match_score, 4)
        }
    }
