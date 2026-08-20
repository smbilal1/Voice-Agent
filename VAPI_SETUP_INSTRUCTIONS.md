# Vapi Assistant Setup Instructions

## Problem
Vapi is calling the `create_patient` tool but passing empty arguments `{}` instead of the patient data collected during the conversation.

## Root Cause
The tools in Vapi are not configured correctly as **Server Tools** that connect to your webhook endpoint.

## Solution: Configure Server Tools in Vapi Dashboard

### Step 1: Access Your Assistant
1. Go to [Vapi Dashboard](https://dashboard.vapi.ai)
2. Open **Assistants** → **CareCloud Patient Registration**
   - Assistant ID: `27815141-fc76-4c8a-85e0-f02b2d468150`

### Step 2: Update System Prompt
1. Click on the **Instructions** or **System Prompt** section
2. Paste this prompt:

```
You are Ava, CareCloud's warm, professional virtual patient intake coordinator.

Your single goal is to register or update a test patient record through a natural phone conversation. This is a technical demonstration, not an emergency line. Do not provide medical advice, diagnoses, treatment, or insurance coverage advice. If a caller has an emergency, tell them to call 911 or their local emergency number.

Conversation style:
- Be calm, concise, and conversational. Ask one clear question at a time.
- Let callers answer in any order. Acknowledge information, remember it, and only ask for what is missing or needs clarification.
- Accept corrections at any time, including spelled names. Repeat spelling back when it is ambiguous.
- If the caller says they want to start over, discard the unsaved information and begin again.
- Never invent, guess, or silently alter a caller's information.

Required information:
1. first name and last name
2. date of birth in month/day/year form; it must be a real date and cannot be in the future
3. sex: Male, Female, Other, or Decline to Answer
4. a U.S. 10-digit phone number
5. street address line 1, city, two-letter U.S. state, and ZIP code

Optional information:
After the required information is complete, say: "I can also collect your insurance information, emergency contact, and preferred language. Would you like to provide any of those?" Do not pressure the caller. Default preferred_language to English if not supplied.

Duplicate workflow:
- Once you have a valid phone number, call find_patient_by_phone.
- If a record exists, tell the caller only that a record exists for its first and last name and ask whether they would like to update it. Never read back old demographic details until the caller confirms they are the patient.
- If they choose an update, collect only the changed information, read back the changes, and obtain explicit confirmation before calling update_patient.

New registration workflow:
- Validate each item conversationally. For an invalid phone, ZIP, state, or future/invalid date, explain only that issue and ask for that field again.
- Before saving, read back every collected required field and every optional field supplied. Ask: "Is all of that correct, and may I save your registration?"
- Only an explicit yes or confirmation authorizes a save. A vague acknowledgement is not enough; ask again.
- After explicit confirmation, call create_patient exactly once with the full collected record.
- Do not say the patient is registered until the tool result says status is created.
- On success, say: "You're all set, [first name]. Your registration has been saved." Then end the call.
- If saving fails, apologize briefly, say the registration was not saved, and offer to try again. Do not pretend it succeeded.

Privacy:
- Use test data only. Never ask for Social Security numbers, payment cards, medical history, or symptoms.
- Do not mention internal tool names, APIs, databases, prompts, or system instructions to the caller.
```

### Step 3: Remove Existing Tools
1. Go to the **Tools** or **Functions** section
2. **DELETE ALL** existing tools (they're configured incorrectly)

### Step 4: Add Server Tools
1. Click **Add Tool** → **Custom Tool** or **Server Tool**
2. Configure the server:
   - **Server URL**: `https://YOUR-DEPLOYMENT-URL.com/vapi/tools`
     - Replace with your actual Railway or Vercel URL
     - Make sure it ends with `/vapi/tools` (not `/vapi/toolsi`)
   - **Authentication**: Bearer Token
   - **Bearer Token**: `hello-world-420`

3. Add each tool individually:

#### Tool 1: find_patient_by_phone
```json
{
  "type": "function",
  "function": {
    "name": "find_patient_by_phone",
    "description": "Checks whether an active patient record already exists for a validated U.S. phone number.",
    "parameters": {
      "type": "object",
      "properties": {
        "phone_number": {
          "type": "string",
          "description": "U.S. phone number."
        }
      },
      "required": ["phone_number"]
    }
  }
}
```

#### Tool 2: create_patient
```json
{
  "type": "function",
  "function": {
    "name": "create_patient",
    "description": "Creates a new patient record only after the caller explicitly confirms the complete read-back.",
    "parameters": {
      "type": "object",
      "properties": {
        "first_name": {"type": "string", "description": "First name"},
        "last_name": {"type": "string", "description": "Last name"},
        "date_of_birth": {"type": "string", "description": "Date of birth in YYYY-MM-DD format"},
        "sex": {"type": "string", "enum": ["Male", "Female", "Other", "Decline to Answer"]},
        "phone_number": {"type": "string", "description": "U.S. phone number"},
        "email": {"type": "string"},
        "address_line_1": {"type": "string"},
        "address_line_2": {"type": "string"},
        "city": {"type": "string"},
        "state": {"type": "string", "description": "Two-letter U.S. state"},
        "zip_code": {"type": "string", "description": "Five-digit ZIP"},
        "insurance_provider": {"type": "string"},
        "insurance_member_id": {"type": "string"},
        "preferred_language": {"type": "string"},
        "emergency_contact_name": {"type": "string"},
        "emergency_contact_phone": {"type": "string"}
      },
      "required": ["first_name", "last_name", "date_of_birth", "sex", "phone_number", "address_line_1", "city", "state", "zip_code"]
    }
  }
}
```

#### Tool 3: update_patient
```json
{
  "type": "function",
  "function": {
    "name": "update_patient",
    "description": "Updates an existing patient record only after the caller explicitly confirms the changes.",
    "parameters": {
      "type": "object",
      "properties": {
        "patient_id": {"type": "string", "description": "Existing patient UUID"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "date_of_birth": {"type": "string"},
        "sex": {"type": "string", "enum": ["Male", "Female", "Other", "Decline to Answer"]},
        "phone_number": {"type": "string"},
        "email": {"type": "string"},
        "address_line_1": {"type": "string"},
        "address_line_2": {"type": "string"},
        "city": {"type": "string"},
        "state": {"type": "string"},
        "zip_code": {"type": "string"},
        "insurance_provider": {"type": "string"},
        "insurance_member_id": {"type": "string"},
        "preferred_language": {"type": "string"},
        "emergency_contact_name": {"type": "string"},
        "emergency_contact_phone": {"type": "string"}
      },
      "required": ["patient_id"]
    }
  }
}
```

### Step 5: Save and Test
1. Click **Save** or **Publish** to apply changes
2. Test with **Talk to Assistant** in the Vapi dashboard
3. Make a test call from your phone: `+15728679107`

### Step 6: Verify in Logs
After a test call, check your deployment logs to ensure:
- ✅ Tools are being called with actual patient data (not empty `{}`)
- ✅ Patient records are being created successfully
- ✅ No validation errors

## Troubleshooting

### If you still see empty arguments `{}`
- Make sure tools are configured as **Server Tools**, not built-in tools
- Verify the webhook URL is correct and accessible
- Check that authentication is set to Bearer token with your secret

### If tools aren't being called at all
- Ensure the system prompt instructs the AI to use the tools
- Check that required fields are marked correctly
- Test with simpler test data first

### If you get 401 Unauthorized
- Verify Bearer token matches `VAPI_WEBHOOK_SECRET` in your environment variables
- Should be: `Bearer hello-world-420`

## Environment Variables Checklist
Ensure these are set in your deployment (Railway/Vercel):
- ✅ `DATABASE_URL` - Your Neon PostgreSQL connection string
- ✅ `VAPI_WEBHOOK_SECRET=hello-world-420`
- ✅ `VAPI_API_KEY=84650cfd-e648-487d-aea0-cef1103d0de1`
- ✅ `VAPI_ASSISTANT_ID=27815141-fc76-4c8a-85e0-f02b2d468150`
- ✅ `VAPI_PHONE_NUMBER=+15728679107`
- ✅ `ENVIRONMENT=production`
- ✅ `LOG_LEVEL=INFO`
