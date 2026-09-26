import re
from datetime import datetime

LICENSE_ORDER = {"GC-1": 1, "GC-2": 2, "GC-3": 3, "GC-4": 4, "GC-5": 5}

def license_match(contractor_grade: str | None, required_grade: str | None) -> bool | None:
    if not contractor_grade or not required_grade:
        return None
    c = LICENSE_ORDER.get(contractor_grade.strip().upper())
    r = LICENSE_ORDER.get(required_grade.strip().upper())
    return None if c is None or r is None else c <= r

def _number(value) -> float | None:
    if value is None:
        return None
    text = str(value).replace(",", "").replace(" ", "")
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else None

def _money(text: str) -> float | None:
    if not text:
        return None
    m = re.search(r"(?:ETB|Birr|Br)?\s*([0-9][0-9,]*(?:\.\d+)?)\s*(?:million|m|billion|bn|thousand|k)?", text, re.I)
    if not m:
        return None
    value = float(m.group(1).replace(",", ""))
    suffix = (m.group(0).lower())
    if "billion" in suffix or "bn" in suffix:
        value *= 1_000_000_000
    elif "million" in suffix or re.search(r"\bm\b", suffix):
        value *= 1_000_000
    elif "thousand" in suffix or re.search(r"\bk\b", suffix):
        value *= 1_000
    return value

def _tokens(text: str) -> set[str]:
    return {x for x in re.findall(r"[a-z0-9]+", (text or "").lower()) if len(x) > 2}

def _result(req: dict, status: str, reason: str, evidence: str = "") -> dict:
    return {
        "requirement_id": req.get("id"),
        "type": req.get("requirement_type", "unknown"),
        "description": req.get("description", ""),
        "status": status,
        "reason": reason,
        "evidence": evidence,
    }

def _evaluate_requirement(req: dict, contractor: dict, experience: list[dict], equipment: list[dict]) -> dict:
    rtype = (req.get("requirement_type") or "").lower()
    description = req.get("description") or ""
    text = description.lower()

    if rtype == "eligibility" and ("license" in text or "grade" in text):
        required = req.get("required_value")
        if not required:
            found = re.search(r"GC[- ]?[1-5]", description, re.I)
            required = found.group(0).replace(" ", "-").upper() if found else None
        actual = contractor.get("license_grade")
        if not actual or not required:
            return _result(req, "needs_verification", "License grade is not sufficiently specified in the tender or contractor profile.")
        matched = license_match(str(actual), str(required))
        return _result(req, "satisfied" if matched else "not_satisfied",
                       f"Contractor {actual} vs tender requirement {required}.",
                       f"contractor.license_grade={actual}")

    if rtype == "financial":
        required = _number(req.get("required_value")) or _money(description)
        actual = contractor.get("financial_capacity")
        if required is None or actual is None:
            return _result(req, "needs_verification", "A comparable financial threshold or contractor capacity is missing.")
        matched = float(actual) >= required
        return _result(req, "satisfied" if matched else "not_satisfied",
                       f"Capacity {float(actual):,.0f} ETB compared with extracted threshold {required:,.0f} ETB.",
                       f"contractor.financial_capacity={actual}")

    if rtype == "equipment":
        if not equipment:
            return _result(req, "not_satisfied", "No contractor equipment is recorded.")
        req_tokens = _tokens(description)
        best = []
        for item in equipment:
            name = str(item.get("equipment_type") or "")
            overlap = req_tokens & _tokens(name)
            if overlap:
                best.append((item, overlap))
        if not best:
            return _result(req, "not_satisfied", "No recorded equipment matches the tender description.")
        required_qty = _number(req.get("required_value"))
        if required_qty is None:
            qty_match = True
        else:
            qty_match = sum(int(x[0].get("quantity") or 0) for x in best) >= required_qty
        if qty_match:
            return _result(req, "satisfied", "Recorded equipment matches the requirement and quantity where a quantity was available.",
                           ", ".join(str(x[0].get("equipment_type")) for x in best))
        return _result(req, "not_satisfied", "Matching equipment exists, but the recorded quantity is below the tender requirement.")

    if rtype == "experience":
        if not experience:
            return _result(req, "not_satisfied", "No contractor project experience is recorded.")
        years_required = _number(req.get("required_value"))
        years_text = re.search(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)", description, re.I)
        if years_required is None and years_text:
            years_required = float(years_text.group(1))
        project_value_required = None
        money_text = re.search(r"(?:ETB|Birr|Br)\s*([0-9][0-9,]*(?:\.\d+)?)\s*(million|m|billion|bn|thousand|k)?", description, re.I)
        if money_text:
            project_value_required = _money(money_text.group(0))
        type_tokens = _tokens(description)
        candidates = []
        for item in experience:
            project_type = str(item.get("project_type") or "")
            value = float(item.get("contract_value") or 0)
            overlap = type_tokens & _tokens(project_type)
            candidates.append((item, overlap, value))
        if project_value_required is not None:
            candidates = [x for x in candidates if x[2] >= project_value_required]
        if type_tokens:
            typed = [x for x in candidates if x[1]]
            if typed:
                candidates = typed
        if not candidates:
            return _result(req, "not_satisfied", "No recorded project experience meets the extracted experience criteria.")
        evidence = ", ".join(str(x[0].get("project_name")) for x in candidates[:5])
        reason_parts = ["Recorded project experience supports the requirement."]
        if project_value_required is not None:
            reason_parts.append(f"project value threshold {project_value_required:,.0f} ETB")
        if years_required is not None:
            contractor_years = contractor.get("years_experience")
            if contractor_years is None:
                return _result(req, "needs_verification", f"Tender indicates at least {years_required:g} years of experience, but contractor years are not recorded.")
            if float(contractor_years) < years_required:
                return _result(req, "not_satisfied", f"Contractor reports {contractor_years:g} years versus required {years_required:g} years.")
            reason_parts.append(f"{contractor_years:g} years recorded")
        return _result(req, "satisfied", " ".join(reason_parts), evidence)

    if rtype in {"technical", "personnel", "document"}:
        return _result(req, "needs_verification", "The platform needs explicit contractor evidence for this requirement; it does not assume compliance.")

    if rtype == "eligibility":
        return _result(req, "needs_verification", "Eligibility requirement requires structured verification.")

    return _result(req, "unknown", "Requirement type is not yet supported by the matching rules.")

def build_match(tender: dict, requirements: list[dict], contractor: dict, experience: list[dict], equipment: list[dict]) -> dict:
    mandatory = [x for x in requirements if x.get("mandatory", True)]
    details = [_evaluate_requirement(x, contractor, experience, equipment) for x in mandatory]

    by_type = {}
    for item in details:
        current = by_type.get(item["type"], [])
        current.append(item["status"])
        by_type[item["type"]] = current

    def aggregate(kind: str) -> bool | None:
        values = by_type.get(kind, [])
        if not values:
            return None
        if "not_satisfied" in values:
            return False
        if "needs_verification" in values or "unknown" in values:
            return None
        return True

    closing = tender.get("closing_date")
    deadline_status = "open" if closing else "unknown"
    if closing:
        try:
            deadline_status = "closed" if datetime.fromisoformat(str(closing).replace("Z", "+00:00")) < datetime.now().astimezone() else "open"
        except ValueError:
            deadline_status = "unknown"

    unresolved = [x["description"] for x in details if x["status"] != "satisfied"]
    return {
        "license_match": aggregate("eligibility"),
        "experience_match": aggregate("experience"),
        "equipment_match": aggregate("equipment"),
        "financial_match": aggregate("financial"),
        "deadline_status": deadline_status,
        "missing_requirements": unresolved,
        "match_details": details,
        "notes": "Requirement-by-requirement comparison. Satisfied means the recorded contractor evidence supports the requirement; unresolved items require verification."
    }
