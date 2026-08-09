import json
import os
import argparse

def generate_support_statement(verdict, math_family):
    registry_path = "registry/bounded_support_statement_registry.json"
    
    if not os.path.exists(registry_path):
        print(f"Error: {registry_path} missing.")
        return

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    # Find template
    template = next((t["template"] for t in registry["statement_templates"] if t["verdict"] == verdict), None)
    if not template:
        print(f"Error: No template found for verdict {verdict}")
        return

    statement = template.format(math_family=math_family)
    print(f"Generated Statement:\n\n{statement}")
    return statement

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate governed bounded-support statements.")
    parser.add_argument("--verdict", required=True, help="Support verdict (e.g., STRONG_SUPPORT).")
    parser.add_argument("--family", required=True, help="Math family ID.")
    args = parser.parse_args()

    generate_support_statement(args.verdict, args.family)
