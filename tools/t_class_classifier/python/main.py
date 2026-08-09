import sys
import argparse
import json
import ingest
import sanitize
import t_signature
import classify
import audit
import distribution

def run_classifier(input_path: str, output_path: str, action: str = "reject") -> int:
    try:
        # Ingest
        raw_data = ingest.read_trace_file(input_path)
        
        # Sanitize / negative fixture policy
        sanitize.validate_schema_integrity(raw_data)
        sanitized_data = sanitize.strip_forbidden_fields(raw_data, action=action)
        
        # Ingest parsed dataclass
        trace = ingest.parse_trace(sanitized_data)
        
        # Signature & Classification
        t_sig = t_signature.build_t_sig(trace)
        res = classify.assign_t_class(t_sig)
        
        # Audit
        audit.write_decision_audit(res, output_path)
        print(f"Classification successful: Assigned class {res.t_class} to {input_path}")
        return 0
    except Exception as e:
        sys.stderr.write(f"Error during classification: {str(e)}\n")
        return 1

def main():
    parser = argparse.ArgumentParser(description="T_class Topological Organization Classifier")
    parser.add_argument("--input", required=True, help="Path to realized closure trace JSON file")
    parser.add_argument("--output", required=True, help="Path to write classification result JSON file")
    parser.add_argument("--action", default="reject", choices=["reject", "strip"], help="Action on forbidden fields")
    args = parser.parse_args()

    sys.exit(run_classifier(args.input, args.output, action=args.action))
