from datetime import date, timedelta


def create_patient(client, payload: dict) -> dict:
    response = client.post("/patients", json=payload)
    assert response.status_code == 201, response.text
    return response.json()["data"]


def test_create_and_retrieve_patient(client, valid_patient_payload):
    created = create_patient(client, valid_patient_payload)

    assert created["phone_number"] == "4155552671"
    assert created["state"] == "CA"
    assert created["preferred_language"] == "English"

    response = client.get(f"/patients/{created['patient_id']}")
    assert response.status_code == 200
    assert response.json() == {"data": created, "error": None}


def test_list_filters_by_last_name_dob_and_phone(client, valid_patient_payload):
    jane = create_patient(client, valid_patient_payload)
    create_patient(client, valid_patient_payload | {"first_name": "John", "last_name": "Smith", "phone_number": "2125550199"})

    by_name = client.get("/patients", params={"last_name": "dav"})
    assert by_name.status_code == 200
    assert [item["patient_id"] for item in by_name.json()["data"]] == [jane["patient_id"]]

    by_dob = client.get("/patients", params={"date_of_birth": "1990-04-15"})
    assert len(by_dob.json()["data"]) == 2

    by_phone = client.get("/patients", params={"phone_number": "(415) 555-2671"})
    assert [item["patient_id"] for item in by_phone.json()["data"]] == [jane["patient_id"]]


def test_partial_update_then_soft_delete(client, valid_patient_payload):
    created = create_patient(client, valid_patient_payload)
    patient_id = created["patient_id"]

    update = client.put(f"/patients/{patient_id}", json={"city": "Austin", "state": "TX"})
    assert update.status_code == 200
    assert update.json()["data"]["city"] == "Austin"
    assert update.json()["data"]["state"] == "TX"

    deletion = client.delete(f"/patients/{patient_id}")
    assert deletion.status_code == 200
    assert deletion.json()["data"]["patient_id"] == patient_id
    assert deletion.json()["data"]["deleted_at"] is not None

    assert client.get(f"/patients/{patient_id}").status_code == 404
    assert client.get("/patients").json()["data"] == []


def test_invalid_data_returns_consistent_422_envelope(client, valid_patient_payload):
    invalid_cases = [
        {"phone_number": "123"},
        {"date_of_birth": (date.today() + timedelta(days=1)).isoformat()},
        {"state": "ZZ"},
        {"zip_code": "12"},
        {"first_name": "Jane3"},
    ]

    for invalid in invalid_cases:
        response = client.post("/patients", json=valid_patient_payload | invalid)
        assert response.status_code == 422
        body = response.json()
        assert body["data"] is None
        assert body["error"]["code"] == "VALIDATION_ERROR"


def test_missing_patient_and_empty_update_are_handled(client):
    missing = client.get("/patients/00000000-0000-0000-0000-000000000000")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "HTTP_404"

    empty_update = client.put("/patients/00000000-0000-0000-0000-000000000000", json={})
    assert empty_update.status_code == 422
    assert empty_update.json()["error"]["code"] == "HTTP_422"
