def validate(report, schema):
    missing = [key for key in schema["required_sections"] if key not in report]
    if missing:
        return False, ["missing sections: " + ", ".join(missing)]
    errors = []
    for item in report["object_inventory"]["analyzed"]:
        if item["primary_classification"] not in schema["allowed_classifications"]:
            errors.append("invalid classification: " + item["primary_classification"])
        if item["formal_status"] not in schema["allowed_formal_statuses"]:
            errors.append("invalid formal status: " + item["formal_status"])
    profiles = report["object_inventory"].get("profiles", [])
    profile_ids = {item.get("object_id") for item in profiles}
    analyzed_ids = {item.get("object_id") for item in report["object_inventory"]["analyzed"]}
    if profile_ids != analyzed_ids:
        errors.append("object profile inventory mismatch")
    required_profile_fields = schema.get("object_profile_required_fields", [])
    for profile in profiles:
        for field in required_profile_fields:
            if field not in profile:
                errors.append("missing profile field: " + field)
        if profile.get("confidence") not in schema.get("allowed_confidence_levels", []):
            errors.append("invalid confidence: " + str(profile.get("confidence")))
        if profile.get("proof_state") not in schema.get("allowed_proof_states", []):
            errors.append("invalid proof state: " + str(profile.get("proof_state")))
        if not set(schema.get("impact_fields", [])).issubset(profile.get("impact", {})):
            errors.append("incomplete impact profile: " + str(profile.get("object_id")))
    if report["campaign_metadata"].get("canonical_promotion_allowed"):
        errors.append("promotion cannot be authorized by crawl")
    return not errors, errors
