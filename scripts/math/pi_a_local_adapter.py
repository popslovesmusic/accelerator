"""Governed provisional Pi_A local adapter.

This is a bounded implementation surface for local fixture evaluation. It is
not a theorem prover, physical model, or authorization for lexicon promotion.
The contract remains conditional and strictly local.
"""


class PiALocalAdapter:
    contract_id = "PI_A_LOCAL_ADAPTER_CONTRACT_20260726_001"
    scope = "STRICTLY_LOCAL_RESTRICTED_DOMAIN"
    claim_boundary = "C1_DEFINED_PROVISIONAL"
    governed_status = "PROVISIONAL_NONPHYSICAL_ADAPTER"

    def project(self, values):
        required = ("already_in_Im_Pi_A", "local_domain_declared", "admissibility_budget_non_exhausted")
        if not all(key in values for key in required):
            return "INVALID_INPUT_CONTRACT"
        if not values["local_domain_declared"]:
            return "COMPOSITION_BLOCKED"
        if not values["admissibility_budget_non_exhausted"]:
            return "MEMBERSHIP_NOT_ESTABLISHED"
        return "MEMBERSHIP_CONDITION_SATISFIED" if values["already_in_Im_Pi_A"] else "MEMBERSHIP_NOT_ESTABLISHED"

    def compose(self, values):
        required = ("MT_001_dependency_active", "Pi_A_signature_typed", "composition_scope_local_only")
        if not all(key in values for key in required):
            return "INVALID_INPUT_CONTRACT"
        return "LOCAL_COMPOSITION_CONDITION_SATISFIED" if all(values[key] for key in required) else "COMPOSITION_BLOCKED"

    def check_failure_boundary(self, values):
        required = ("failure_geometry_links_present", "excluded_domains_declared", "counterexamples_not_discharged")
        if not all(key in values for key in required):
            return "INVALID_INPUT_CONTRACT"
        return "FAILURE_BOUNDARY_RETAINED" if all(values[key] for key in required) else "EXCLUSION_BLOCKED"

    def evaluate(self, fixture):
        handlers = {
            "PO-010-001": self.project,
            "PO-010-002": self.compose,
            "PO-010-003": self.check_failure_boundary,
        }
        try:
            handler = handlers[fixture["obligation"]]
        except KeyError as exc:
            raise ValueError(f"Unsupported obligation: {fixture.get('obligation')}") from exc
        return handler(fixture["input"])
