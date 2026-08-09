import os
import argparse
import json

def classify_path(path):
    path = path.replace('\\', '/')
    
    status = 'unverified_residue'
    scope = 'unknown'
    confidence = 'not_checked'
    
    # Classification Logic
    if path.startswith('registry/') and (
        'lexicon_canonical' in path or 
        'lexicon_alias_map' in path or 
        'compliance_charter' in path or 
        'claim_registry' in path or
        'math_registry' in path
    ):
        status = 'canonical_active'
        scope = 'lexicon' if 'lexicon' in path else 'registry'
        confidence = 'verified'
    
    elif path.startswith('scripts/') or path.startswith('oneproc/') or path.endswith('.py') or path.endswith('.ps1') or path.endswith('.bat'):
        status = 'active_runtime'
        scope = 'command_audit' if 'audit' in path else 'unknown'
        confidence = 'verified'
    
    elif path.startswith('results/') or path.startswith('outputs/'):
        if '2026-04' in path or '2026-03' in path or 'legacy' in path:
            status = 'historical_residue'
            scope = 'historical_report'
            confidence = 'verified_as_residue_only'
        else:
            status = 'active_runtime'
            scope = 'tool_validation' if 'validation' in path else 'command_audit'
            confidence = 'verified'
            
        if 'current_evidence' in path:
            status = 'current_command_evidence'
            
    elif 'backup' in path or 'archive' in path or 'old' in path or 'copy' in path or path.endswith('.bak'):
        status = 'archived'
        scope = 'historical_report'
        confidence = 'verified_as_residue_only'
        
    elif 'deprecated' in path:
        status = 'deprecated'
        scope = 'unknown'
        confidence = 'not_checked'
        
    elif 'superseded' in path:
        status = 'superseded'
        scope = 'unknown'
        confidence = 'not_checked'
        
    elif path.startswith('configs/'):
        status = 'canonical_active' if 'canonical' in path else 'active_runtime'
        scope = 'config'
        confidence = 'verified'
        
    elif path.startswith('docs/'):
        status = 'canonical_active' if 'foundational' in path else 'active_runtime'
        scope = 'doc'
        confidence = 'verified'

    return status, scope, confidence

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check orientation status of a path.")
    parser.add_argument("path", help="Path to classify.")
    args = parser.parse_args()
    
    status, scope, confidence = classify_path(args.path)
    print(json.dumps({
        "path": args.path, 
        "orientation_status": status,
        "authority_scope": scope,
        "evidence_confidence": confidence
    }))
