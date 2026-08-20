import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.routes import patients as patient_routes
from app.api.routes import vapi as vapi_routes
from app.core.config import settings
from app.db.session import get_db_session
from app.main import app
from app.models.patient import Patient


class InMemoryPatientRepository:
    """Test double that exercises HTTP behavior without external database credentials."""

    def __init__(self) -> None:
        self.patients: dict[uuid.UUID, Patient] = {}

    def get_active(self, _session, patient_id: uuid.UUID) -> Patient | None:
        patient = self.patients.get(patient_id)
        return patient if patient and patient.deleted_at is None else None

    def list_active(self, _session, *, last_name, date_of_birth, phone_number) -> list[Patient]:
        patients = [patient for patient in self.patients.values() if patient.deleted_at is None]
        if last_name:
            patients = [patient for patient in patients if last_name.lower() in patient.last_name.lower()]
        if date_of_birth:
            patients = [patient for patient in patients if patient.date_of_birth == date_of_birth]
        if phone_number:
            patients = [patient for patient in patients if patient.phone_number == phone_number]
        return sorted(patients, key=lambda patient: patient.created_at, reverse=True)

    def create(self, _session, values: dict) -> Patient:
        now = datetime.now(timezone.utc)
        patient = Patient(patient_id=uuid.uuid4(), **values)
        patient.created_at = now
        patient.updated_at = now
        self.patients[patient.patient_id] = patient
        return patient

    def update(self, _session, patient: Patient, values: dict) -> Patient:
        for field, value in values.items():
            setattr(patient, field, value)
        patient.updated_at = datetime.now(timezone.utc)
        return patient

    def soft_delete(self, _session, patient: Patient) -> None:
        patient.deleted_at = datetime.now(timezone.utc)


class FakeSession:
    def commit(self) -> None:
        pass

    def flush(self) -> None:
        pass

    def refresh(self, _patient) -> None:
        pass

    def rollback(self) -> None:
        pass


def empty_session():
    yield FakeSession()


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    repository = InMemoryPatientRepository()
    monkeypatch.setattr(patient_routes, "repository", repository)
    monkeypatch.setattr(vapi_routes, "repository", repository)
    monkeypatch.setattr(settings, "vapi_webhook_secret", "test-vapi-secret")
    app.dependency_overrides[get_db_session] = empty_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def valid_patient_payload() -> dict:
    return {
        "first_name": "Jane",
        "last_name": "Davis",
        "date_of_birth": "1990-04-15",
        "sex": "Female",
        "phone_number": "+1 (415) 555-2671",
        "email": "jane.davis@example.com",
        "address_line_1": "1 Market Street",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94105",
    }
