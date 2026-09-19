from decode_base64 import *
from utils import get_subject_id, get_reference_id

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

def extract_notes(records):
    rows = []
    for doc in records:
        subject_id = get_subject_id(doc)
        context = doc.get("context") or {}

        encounter_refs = context.get("encounter") or []
        if isinstance(encounter_refs, dict):
            encounter_refs = [encounter_refs]
        encounter_ref = encounter_refs[0] if encounter_refs else {}

        coding_display = extract_first_coding_display(doc)

        decoded_payloads = list(find_base64(doc))
        if not decoded_payloads:
            decoded_payloads = [None]

        for text in decoded_payloads:
            rows.append({
                "patient_id": subject_id,
                "document_id": doc.get("id"),
                "encounter_id": get_reference_id(encounter_ref.get("reference")),
                "encounter_display": encounter_ref.get("display"),
                "coding_display": coding_display,
                "date": doc.get("date"),
                "text": text,
            })

    return rows
