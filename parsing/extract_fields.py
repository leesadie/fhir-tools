from fhir_utils import get_path

def extract_resources(records: list, schema: dict):
    """
    Generic extractor for any FHIR resource array

    Args
    ----
    records: list of FHIR resource dicts
    schema: dict mapping column output names to dot-paths, tuples or callables
    """
    rows = []
    for record in records:
        row = {}
        for col, extractor in schema.items():
            if callable(extractor):
                # Custom function
                row[col] = extractor(record)
            elif isinstance(extractor, tuple):
                # (Path, Transformer)
                path, transform = extractor
                raw_val = get_path(record, path) if path else record
                row[col] = transform(raw_val) if raw_val is not None else None
            elif isinstance(extractor, str):
                # Plain path lookup
                row[col] = get_path(record, extractor)
            else:
                row[col] = None
        rows.append(row)
    return rows

def extract_epic_mrn(patient):
    for i in patient.get("identifier", []):
        if not isinstance(i, dict):
            continue
        type_text = get_path(i, "type.text", "")
        if "EPIC" in str(type_text).upper():
            val = i.get("value")
            if isinstance(val, str) and not val.startswith("E"):
                return val
    return None

def extract_ethnicity(patient):
    for ext in patient.get("extension", []):
        if not isinstance(ext, dict):
            continue
        for sub_ext in ext.get("extension", []):
            if isinstance(sub_ext, dict):
                display = get_path(sub_ext, "valueCoding.display")
                if display:
                    return display
    return None

def extract_patient_name(patient):
    names = patient.get("name", [])
    if names and isinstance(names[0], dict):
        first = names[0]
        if first.get("text"):
            return first.get("text")
        given = " ".join(first.get("given", []))
        family = first.get("family", "")
        return f"{given} {family}".strip() or None
    return None
