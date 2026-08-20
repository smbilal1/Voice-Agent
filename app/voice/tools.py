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
    "description": "Creates a new patient record only after the caller explicitly confirms the complete read-back.",
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
    "description": "Checks whether an active patient record already exists for a validated U.S. phone number.",
    "parameters": {
        "type": "object",
        "properties": {"phone_number": {"type": "string", "description": "U.S. phone number."}},
        "required": ["phone_number"],
    },
}

UPDATE_PATIENT_TOOL = {
    "name": "update_patient",
    "description": "Updates an existing patient record only after the caller explicitly confirms the changes.",
    "parameters": {
        "type": "object",
        "properties": {"patient_id": {"type": "string", "description": "Existing patient UUID."}} | PATIENT_PROPERTIES,
        "required": ["patient_id"],
    },
}

VAPI_FUNCTION_TOOLS = [CREATE_PATIENT_TOOL, FIND_PATIENT_BY_PHONE_TOOL, UPDATE_PATIENT_TOOL]
