def validate(report, schema):
    missing = [key for key in schema["required_sections"] if key not in report]
    if missing:
        return False, ["missing sections: " + ", ".join(missing)]
    errors = []
    for item in report["mathematical_inventory"]:
        if item["primary_classification"] not in schema["allowed_classifications"]:
            errors.append("invalid classification: " + item["primary_classification"])
        if item["formal_status"] not in schema["allowed_formal_statuses"]:
            errors.append("invalid formal status: " + item["formal_status"])
    if report["campaign_metadata"].get("canonical_promotion_allowed"):
        errors.append("promotion cannot be authorized by crawl")
    return not errors, errors
