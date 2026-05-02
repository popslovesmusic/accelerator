import json
import os
from typing import Dict, Any, Optional

class GovernanceLoader:
    def __init__(self, charter_path: str = "registry/compliance_charter_v2_3.json"):
        self.charter_path = charter_path
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if os.path.exists(self.charter_path):
            with open(self.charter_path, "r", encoding="utf-8") as f:
                return json.load(f).get("governance_enforcement_v2", {})
        return {}

    def get_mandate(self, level: str) -> Dict[str, Any]:
        return self.data.get("claim_level_mandates", {}).get(level, {})

    def get_template_mandates(self) -> Dict[str, Any]:
        return self.data.get("template_mandates", {})

    def get_intent_limits(self) -> Dict[str, str]:
        return self.data.get("intent_limits", {})
