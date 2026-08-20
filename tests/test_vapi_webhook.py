import json


def vapi_payload(name: str, arguments: dict, call_id: str = "tool-call-1") -> dict:
    """Create Vapi payload matching actual Vapi toolCallList structure with function.arguments"""
    return {
        "message": {
            "type": "tool-calls",
            "toolCallList": [
                {
                    "id": call_id,
                    "function": {
                        "name": name,
                        "arguments": arguments if isinstance(arguments, str) else json.dumps(arguments)
                    }
                }
            ]
        }
    }


def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-vapi-secret"}


def test_vapi_creates_patient_only_through_protected_webhook(client, valid_patient_payload):
    response = client.post("/vapi/tools", headers=auth_headers(), json=vapi_payload("create_patient", valid_patient_payload))

    assert response.status_code == 200, response.text
    result = response.json()["results"][0]
    assert result["toolCallId"] == "tool-call-1"
    tool_result = json.loads(result["result"])
    assert tool_result["status"] == "created"

    patient = client.get(f"/patients/{tool_result['patient_id']}")
    assert patient.status_code == 200
    assert patient.json()["data"]["first_name"] == "Jane"


def test_vapi_lookup_and_validation_errors_follow_tool_contract(client, valid_patient_payload):
    client.post("/vapi/tools", headers=auth_headers(), json=vapi_payload("create_patient", valid_patient_payload))

    lookup = client.post(
        "/vapi/tools", headers=auth_headers(), json=vapi_payload("find_patient_by_phone", {"phone_number": "415-555-2671"}, "lookup-1")
    )
    found = json.loads(lookup.json()["results"][0]["result"])
    assert found["found"] is True
    assert found["first_name"] == "Jane"

    invalid = client.post("/vapi/tools", headers=auth_headers(), json=vapi_payload("create_patient", {"first_name": "Jane"}, "invalid-1"))
    assert invalid.status_code == 200
    assert invalid.json()["results"][0]["toolCallId"] == "invalid-1"
    result = json.loads(invalid.json()["results"][0]["result"])
    assert result["status"] == "validation_error"
    assert "last_name" in result["fields"]


def test_vapi_webhook_rejects_requests_without_the_shared_secret(client, valid_patient_payload):
    response = client.post("/vapi/tools", json=vapi_payload("create_patient", valid_patient_payload))
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "HTTP_401"
