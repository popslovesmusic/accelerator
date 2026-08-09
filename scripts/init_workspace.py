import os
import json

def init_workspace():
    required_dirs = ["outputs/runs", "patches", "registry"]
    for d in required_dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"Created directory: {d}")

    registry_files = [
        "claim_registry.json",
        "evidence_registry.json",
        "language_policy_registry.json",
        "lexicon_canonical.json",
        "tool_manifest.json"
    ]

    for f in registry_files:
        path = os.path.join("registry", f)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as rf:
                json.dump({}, rf)
            print(f"Created empty registry file: {path}")

if __name__ == "__main__":
    init_workspace()
    print("Initialization complete.")
