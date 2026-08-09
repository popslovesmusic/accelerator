#!/usr/bin/env python3
"""
check_lean_pilot.py

Audits the Lean 4 MPF Closure Pilot setup in proofs/lean/.
Executes `lake build` via the Lean 4 compiler, parses compiler stdout/stderr,
and outputs real verification status using strict governance schema rules.
"""

import sys
import os
import json
import subprocess
import re
from pathlib import Path

def run_lake_build(lean_dir):
    lake_bin = "lake"
    elan_bin = Path(os.environ.get("USERPROFILE", "")) / ".elan" / "bin" / "lake.exe"
    if elan_bin.exists():
        lake_bin = str(elan_bin)

    try:
        res = subprocess.run(
            [lake_bin, "build"],
            cwd=str(lean_dir),
            capture_output=True,
            text=True,
            shell=(os.name == "nt")
        )
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        return 1, "", f"Failed to execute lake build: {str(e)}"

def check_lean_pilot():
    base_dir = Path(__file__).parent.parent
    lean_dir = base_dir / "proofs" / "lean"
    
    declared_theorems = [
        "L116_syntax_closure",
        "L117_boundary_condition",
        "orientation_failure_boundary",
        "core_expression_satisfiability",
        "countermodel_boundary_failure",
        "step_admissibility_preservation",
        "step_residue_accumulation",
        "step_valuation_soundness",
        "step_orientation_alignment_preservation",
        "P110_projection_signature",
        "P111_affect_effect_inheritance",
        "P112_projection_intersection_specialization",
        "L118_operator_algebra"
    ]
    
    # Classify substance: 'structural' (true by type construction / pattern match) vs 'substantive'
    theorem_substance = {
        "L116_syntax_closure": "structural",
        "L117_boundary_condition": "substantive",
        "orientation_failure_boundary": "substantive",
        "core_expression_satisfiability": "substantive",
        "countermodel_boundary_failure": "substantive",
        "step_admissibility_preservation": "substantive",
        "step_residue_accumulation": "substantive",
        "step_valuation_soundness": "substantive",
        "step_orientation_alignment_preservation": "substantive",
        "P110_projection_signature": "substantive",
        "P111_affect_effect_inheritance": "structural",
        "P112_projection_intersection_specialization": "substantive",
        "L118_operator_algebra": "substantive"
    }
    
    if not lean_dir.exists() or not (lean_dir / "MpfClosurePilot.lean").exists():
        results = {
            "build_exit_code": 1,
            "compiled": False,
            "theorems_declared": declared_theorems,
            "theorems_proved": [],
            "theorems_with_open_sorry": declared_theorems,
            "theorem_substance": theorem_substance,
            "unexpected_errors": ["File proofs/lean/MpfClosurePilot.lean not found"],
            "status_label": "compile_failure"
        }
        print(json.dumps(results, indent=2))
        return 1

    exit_code, stdout, stderr = run_lake_build(lean_dir)
    combined_output = stdout + "\n" + stderr
    
    compiled = (exit_code == 0)
    
    # Parse lines with 'declaration uses 'sorry'' and extract line numbers
    sorry_lines = []
    for line in combined_output.splitlines():
        if "declaration uses 'sorry'" in line:
            m = re.search(r":(\d+):\d+:", line)
            if m:
                sorry_lines.append(int(m.group(1)))
    
    # Read source file to map line numbers to theorems
    lean_file = lean_dir / "MpfClosurePilot.lean"
    source_lines = lean_file.read_text(encoding="utf-8").splitlines()
    
    theorems_with_open_sorry = []
    for line_num in sorry_lines:
        start = max(0, line_num - 5)
        end = min(len(source_lines), line_num + 5)
        context_text = "\n".join(source_lines[start:end])
        for thm in declared_theorems:
            if thm in context_text and thm not in theorems_with_open_sorry:
                theorems_with_open_sorry.append(thm)
    
    theorems_proved = [t for t in declared_theorems if t not in theorems_with_open_sorry]
    
    # Check compiler errors (lines containing 'error:' not attached to a sorry)
    unexpected_errors = []
    for line in combined_output.splitlines():
        if "error:" in line.lower() and "sorry" not in line.lower():
            unexpected_errors.append(line.strip())

    # Status label calculation
    if not compiled or unexpected_errors:
        status_label = "compile_failure"
    elif len(theorems_with_open_sorry) > 0:
        status_label = "compiles_with_open_gaps"
    else:
        status_label = "fully_verified"

    results = {
        "build_exit_code": exit_code,
        "compiled": compiled,
        "theorems_declared": declared_theorems,
        "theorems_proved": theorems_proved,
        "theorems_with_open_sorry": theorems_with_open_sorry,
        "theorem_substance": theorem_substance,
        "unexpected_errors": unexpected_errors,
        "status_label": status_label,
        "raw_build_output": combined_output.strip()
    }
    
    # Format human readable output
    print("=== Lean 4 MPF Closure Pilot Real Verification ===")
    print(f"Build Exit Code: {exit_code}")
    print(f"Compiled Successfully: {compiled}")
    print(f"Declared Theorems: {', '.join(declared_theorems)}")
    print(f"Theorems Proved (No Sorry / No Open Gap): {', '.join(theorems_proved) if theorems_proved else 'None'}")
    print(f"  - Note on L116_syntax_closure: {theorem_substance['L116_syntax_closure']} (true by pattern match / totality construction)")
    print(f"  - Note on P111_affect_effect_inheritance: {theorem_substance['P111_affect_effect_inheritance']} (true by model mapping definition)")
    print(f"Theorems with Open Sorries/Gaps: {', '.join(theorems_with_open_sorry)}")
    print(f"Theorem Substance Breakdown: {json.dumps(theorem_substance)}")
    print(f"Unexpected Compiler Errors: {len(unexpected_errors)}")
    print(f"Status Label: {status_label}")
    print("\n--- Raw Compiler Output ---")
    print(combined_output.strip())
    
    return 0 if compiled else 1

if __name__ == "__main__":
    sys.exit(check_lean_pilot())
