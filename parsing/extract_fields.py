from get_data import *

def extract_patients(records):
    rows = []
    for patient in records:
        patient_id = patient.get("id")
        ethnicity = None

        for extension in patient.get("extension", []):
            if not isinstance(extension, dict):
                continue

            sub_extensions = extension.get("extension", [])
            for sub_ext in sub_extensions:
                if not isinstance(sub_ext, dict):
                    continue
                value_coding = sub_ext.get("valueCoding")
                if isinstance(value_coding, dict):
                    display = value_coding.get("display")
                    if display:
                        ethnicity = display
                        break
            if ethnicity:
                break

        rows.append({
            "patient_id": patient_id,
            "patient_resource_type": patient.get("resourceType"),
            "gender": patient.get("gender"),
            "ethnicity": ethnicity,
            "birthdate": patient.get("birthDate")
        })
    return rows

def extract_medications(records):
    rows = []
    for med in records:
        med_reference = med.get("medicationReference") or {}
        encounter = med.get("encounter") or {}

        rows.append({
            "patient_id": get_subject_id(med),
            "medication_id": med.get("id"),
            "medication_status": med.get("status"),
            "medication_authoredOn": med.get("authoredOn"),
            "medication_display": med_reference.get("display"),
            "medication_reference": med_reference.get("reference"),
            "medication_encounter": get_reference_id(encounter.get("reference"))
        })

    return rows

def extract_conditions(records):
    rows = []
    for cond in records:
        evidence = cond.get("evidence") or []
        first_evidence = evidence[0] if evidence else {}
        details = first_evidence.get("detail") or []
        first_detail = details[0] if details else {}

        rows.append({
            "patient_id": get_subject_id(cond),
            "condition_id": cond.get("id"),
            "condition_display": first_detail.get("display"),
            "condition_onsetDateTime": cond.get("onsetDateTime"),
            "condition_encounter": get_reference_id((cond.get("encounter") or {}).get("reference"))
        })

    return rows

def extract_codings(value):
    """
    Extracts coding list from FHIR CodeableConcept or list of CodeableConcepts
    """
    if value is None:
        return []
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return []

    codings = []
    for concept in value:
        if not isinstance(concept, dict):
            continue
        concept_codings = concept.get("coding", [])
        if isinstance(concept_codings, dict):
            concept_codings = [concept_codings]

        for coding in concept_codings:
            if isinstance(coding, dict):
                codings.append({
                    "system": coding.get("system"),
                    "code": coding.get("code"),
                    "display": coding.get("display")
                })
    return codings

def extract_first_coding_display(doc):
    """
    Returns the first non-empty coding.display found in doc['type'] or doc['category'].
    """
    for field in ("type", "category"):
        field_value = doc.get(field)
        if not field_value:
            continue
            
        # Normalize CodeableConcept to list
        concepts = field_value if isinstance(field_value, list) else [field_value]
        
        for concept in concepts:
            if not isinstance(concept, dict):
                continue
                
            codings = concept.get("coding", [])
            if isinstance(codings, dict):
                codings = [codings]
                
            for coding in codings:
                if isinstance(coding, dict) and coding.get("display"):
                    return coding["display"]
                    
    return None

def extract_encounters(records):
    rows = []
    for encounter in records:
        locations = encounter.get("location") or []
        first_location = locations[0] if locations else {}
        location_ref = first_location.get("location") or {}

        rows.append({
            "patient_id": get_subject_id(encounter),
            "encounter_id": encounter.get("id"),
            "encounter_location": location_ref.get("display"),
            "encounter_display": encounter.get("class", {}).get("display") if isinstance(encounter.get("class"), dict) else None,
            "encounter_date": (encounter.get("period") or {}).get("start")
        })
        
    return rows