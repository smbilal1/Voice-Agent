PATIENT_PROPERTIES = {
    "first_name": {"type": "string", "description": "First name, letters plus hyphens/apostrophes only."},
    "last_name": {"type": "string", "description": "Last name, letters plus hyphens/apostrophes only."},
    "date_of_birth": {"type": "string", "description": "Date of birth in YYYY-MM-DD format."},
    "sex": {"type": "string", "enum": ["Male", "Female", "Other", "Decline to Answer"]},
    "phone_number": {"type": "string", "description": "U.S. phone number; formatting is allowed."},
    "email": {"type": "string"},
    "address_line_1": {"type": "string"},
    "address_line_2": {"type": "string"},
    "city": {"type": "string"},
    "state": {"type": "string", "description": "Two-letter U.S. state abbreviation."},
    "zip_code": {"type": "string", "description": "Five-digit ZIP or ZIP+4."},
    "insurance_provider": {"type": "string"},
    "insurance_member_id": {"type": "string"},
    "preferred_language": {"type": "string"},
    "emergency_contact_name": {"type": "string"},
    "emergency_contact_phone": {"type": "string"},
}

CREATE_PATIENT_TOOL = {
    "name": "create_patient",
    "description": (
        "Creates a brand-new patient record in the database. Call this ONLY after: "
        "(1) all required fields have been collected, and (2) the caller has explicitly "
        "confirmed the full read-back is correct (a clear 'yes' or equivalent). "
        "Do not call this for a caller who already has an existing record — use "
        "find_patient_by_phone first to check, and use update_patient instead if a match is found. "
        "Do not call this speculatively or before confirmation, even if you believe you have all the data."
    ),
    "parameters": {
        "type": "object",
        "properties": PATIENT_PROPERTIES,
        "required": [
            "first_name", "last_name", "date_of_birth", "sex", "phone_number", "address_line_1", "city", "state", "zip_code"
        ],
    },
}

FIND_PATIENT_BY_PHONE_TOOL = {
    "name": "find_patient_by_phone",
    "description": (
        "Looks up whether an active (non-deleted) patient record already exists for the given "
        "phone number. Call this as soon as you have collected or received the caller's phone "
        "number, BEFORE collecting the rest of their information, so you can offer to update an "
        "existing record instead of creating a duplicate. If no match is returned, proceed with "
        "a normal new-patient registration. Do not call create_patient or update_patient before "
        "calling this tool at least once during the call."
    ),
    "parameters": {
        "type": "object",
        "properties": {"phone_number": {"type": "string", "description": "U.S. phone number."}},
        "required": ["phone_number"],
    },
}

UPDATE_PATIENT_TOOL = {
    "name": "update_patient",
    "description": (
        "Updates one or more fields on an existing patient record, identified by patient_id "
        "(obtained from a prior find_patient_by_phone call). Only include the fields the caller "
        "actually wants to change — omit any field that is staying the same. Call this ONLY after "
        "the caller has explicitly confirmed the specific changes being made. Never call this "
        "without first having a valid patient_id from find_patient_by_phone."
    ),
    "parameters": {
        "type": "object",
        "properties": {"patient_id": {"type": "string", "description": "Existing patient UUID."}} | PATIENT_PROPERTIES,
        "required": ["patient_id"],
    },
}

VAPI_FUNCTION_TOOLS = [CREATE_PATIENT_TOOL, FIND_PATIENT_BY_PHONE_TOOL, UPDATE_PATIENT_TOOL]