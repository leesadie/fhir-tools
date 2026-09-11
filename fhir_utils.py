import pandas as pd

def get_path(data, path, default=None):
    """Safely fetch nested keys/indexes using dot notation"""
    curr = data
    for key in path.split("."):
        if isinstance(curr, dict):
            curr = curr.get(key)
        elif isinstance(curr, list) and key.isdigit():
            idx = int(key)
            curr = curr[idx] if idx < len(curr) else None
        else:
            return default
        if curr is None:
            return default
    return curr

def get_reference_id(value):
    """
    Strips prefix of FHIR reference 
    Example: 'Patient/123' -> '123'
    """
    if isinstance(value, dict):
        value = value.get("reference")
    if not isinstance(value, str):
        return None
    return value.rsplit("/", 1)[-1]

def get_subject_id(resource):
    return get_reference_id(resource.get("subject"))

def get_coding_display(value):
    """
    Returns the first coding.display from a CodeableConcept
    or list of CodeableConcepts
    """
    concepts = value if isinstance(value, list) else [value]
    for concept in concepts:
        if not isinstance(concept, dict):
            continue
        codings = concept.get("coding", [])
        codings = codings if isinstance(codings, list) else [codings]
        for coding in codings:
            if isinstance(coding, dict) and coding.get("display"):
                return coding["display"]
    return None

def get_first_display(value):
    """
    Returns the first display value from a Reference or list of References
    """
    if isinstance(value, dict):
        return value.get("display")
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and item.get("display"):
                return item["display"]
    return None

def join_unique(values, sep=" | "):
    result = []
    for value in values:
        if value is None or pd.isna(value):
            continue
        if isinstance(value, list):
            for item in value:
                if item not in result:
                    result.append(item)
        elif value not in result:
            result.append(value)
    return sep.join(map(str, result)) if result else None