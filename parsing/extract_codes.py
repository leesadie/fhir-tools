import pandas as pd

SYSTEM_PATTERNS = {
    "icd10": ["icd-10", "icd10", "http://hl7.org/fhir/sid/icd-10"],
    "snomed": ["snomed", "http://snomed.info/sct"],
    "rxnorm": ["rxnorm", "http://www.nlm.nih.gov/research/umls/rxnorm"]
}

def extract_coding_systems(resource_list, system_key="icd10"):
    """
    Extracts coding systems and metadata from FHIR resource lists

    Args
    ----
    resource_list: list of dicts for conditions, medications, etc
    system_key: 'icd10', 'snomed', 'rxnorm' or custom search string

    Returns
    ------
    List of dicts with code, display, onset date, and system
    """
    if not isinstance(resource_list, list):
        return []

    # Retrieve match patterns
    patterns = SYSTEM_PATTERNS.get(system_key.lower(), [system_key.lower()])
    matches = []

    for item in resource_list:
        if not isinstance(item, dict):
            continue

        system_val = str(
            item.get("condition_system") or
            item.get("system") or
            item.get("coding_system", "")
        ).lower()

        if any(pattern in system_val for pattern in patterns):
            matches.append({
                "code": item.get("condition_code") or item.get("code"),
                "display": item.get("condition_display") or item.get("display"),
                "system": item.get("condition_system") or item.get("system"),
                "onset_date": (
                    item.get("condition_onsetDateTime") or 
                    item.get("onsetDateTime") or 
                    item.get("authoredOn") or 
                    item.get("effectiveDateTime")
                )
            })

    return matches