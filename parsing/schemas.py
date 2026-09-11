# Common resource extraction schemas
from extract_fields import extract_resources, extract_epic_mrn, extract_patient_name, extract_ethnicity
from fhir_utils import get_subject_id, get_reference_id, get_coding_display

PATIENT_SCHEMA = {
    "patient_id": "id",
    "mrn": extract_epic_mrn,
    "patient_name": extract_patient_name,
    "patient_resource_type": "resourceType",
    "gender": "gender",
    "ethnicity": extract_ethnicity,
    "birthdate": "birthDate"
}

MEDICATION_SCHEMA = {
    "patient_id": get_subject_id,
    "medication_id": "id",
    "medication_status": "status",
    "medication_authoredOn": "authoredOn",
    "medication_display": "medicationReference.display",
    "medication_reference": "medicationReference.reference",
    "medication_encounter": ("encounter.reference", get_reference_id)
}

CONDITION_SCHEMA = {
    "patient_id": get_subject_id,
    "condition_id": "id",
    "condition_display": ("evidence.0.detail.0.display"),
    "condition_onsetDateTime": "onsetDateTime",
    "condition_encounter": ("encounter.reference", get_reference_id)
}

OBSERVATION_SCHEMA = {
    "patient_id": get_subject_id,
    "observation_id": "id",
    "status": "status",
    "code_display": ("code", get_coding_display),
    "value_quantity": "valueQuantity.value",
    "value_unit": "valueQuantity.unit",
    "effective_date": "effectiveDateTime"
}

# Example usage
# patient_rows = extract_resources(patient_records, PATIENT_SCHEMA)
# medication_rows = extract_resources(medication_records, MEDICATION_SCHEMA)
# observation_rows = extract_resources(observation_records, OBSERVATION_SCHEMA)