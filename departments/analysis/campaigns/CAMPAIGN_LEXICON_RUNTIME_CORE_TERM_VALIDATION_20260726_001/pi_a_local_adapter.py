"""Noncanonical, bounded Pi_A adapter for approved fixture execution.

This adapter is a campaign test double bound to the declared registry contract.
It is not an engine implementation and does not establish theorem validity.
"""


class PiALocalAdapter:
    contract_id = "PI_A_LOCAL_ADAPTER_CONTRACT_20260726_001"
    scope = "STRICTLY_LOCAL_RESTRICTED_DOMAIN"
    claim_boundary = "C1_DEFINED_PROVISIONAL"

    def project(self, values):
        if not values.get("local_domain_declared", True):
            return "COMPOSITION_BLOCKED"
        if not values.get("admissibility_budget_non_exhausted", True):
            return "MEMBERSHIP_NOT_ESTABLISHED"
        if values.get("already_in_Im_Pi_A", False):
            return "MEMBERSHIP_CONDITION_SATISFIED"
        return "MEMBERSHIP_NOT_ESTABLISHED"

    def compose(self, values):
        required = ("MT_001_dependency_active", "Pi_A_signature_typed", "composition_scope_local_only")
        return "LOCAL_COMPOSITION_CONDITION_SATISFIED" if all(values.get(key, False) for key in required) else "COMPOSITION_BLOCKED"

    def check_failure_boundary(self, values):
        required = ("failure_geometry_links_present", "excluded_domains_declared", "counterexamples_not_discharged")
        return "FAILURE_BOUNDARY_RETAINED" if all(values.get(key, False) for key in required) else "EXCLUSION_BLOCKED"

    def evaluate(self, fixture):
        obligation = fixture["obligation"]
        if obligation == "PO-010-001":
            return self.project(fixture["input"])
        if obligation == "PO-010-002":
            return self.compose(fixture["input"])
        if obligation == "PO-010-003":
            return self.check_failure_boundary(fixture["input"])
        raise ValueError(f"Unsupported obligation: {obligation}")
