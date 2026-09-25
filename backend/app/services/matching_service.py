LICENSE_ORDER = {"GC-1": 1, "GC-2": 2, "GC-3": 3, "GC-4": 4, "GC-5": 5}

def license_match(contractor_grade: str | None, required_grade: str | None) -> bool | None:
    if not contractor_grade or not required_grade:
        return None
    c, r = LICENSE_ORDER.get(contractor_grade.upper()), LICENSE_ORDER.get(required_grade.upper())
    return None if c is None or r is None else c <= r

def build_match(tender: dict, requirements: list[dict], contractor: dict, experience: list[dict], equipment: list[dict]) -> dict:
    mandatory = [x for x in requirements if x.get("mandatory", True)]
    license_reqs = [x for x in mandatory if x.get("requirement_type") == "eligibility"]
    required_grade = next((x.get("required_value") for x in license_reqs if "license" in x.get("description", "").lower() or "grade" in x.get("description", "").lower()), None)
    lm = license_match(contractor.get("license_grade"), required_grade)
    financial_reqs = [x for x in mandatory if x.get("requirement_type") == "financial"]
    fm = None
    if financial_reqs and contractor.get("financial_capacity") is not None:
        fm = all(float(contractor["financial_capacity"]) >= float(x["required_value"]) for x in financial_reqs if str(x.get("required_value", "")).replace(".", "", 1).isdigit())
    equipment_reqs = [x for x in mandatory if x.get("requirement_type") == "equipment"]
    equipment_text = " ".join(x.get("equipment_type", "") for x in equipment).lower()
    em = None if not equipment_reqs else all(any(part.strip().lower() in equipment_text for part in x.get("description", "").split()) for x in equipment_reqs)
    return {
        "license_match": lm, "experience_match": None if not experience else True,
        "equipment_match": em, "financial_match": fm,
        "deadline_status": "open" if tender.get("closing_date") else "unknown",
        "missing_requirements": [x.get("description", "") for x in mandatory if x.get("verified") is not True],
        "notes": "Requirement-by-requirement comparison; unknown fields remain unresolved rather than being scored."
    }
