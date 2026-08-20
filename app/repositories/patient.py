import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.patient import Patient


class PatientRepository:
    """Database access for active patient records."""

    def get_active(self, session: Session, patient_id: uuid.UUID) -> Patient | None:
        statement = select(Patient).where(Patient.patient_id == patient_id, Patient.deleted_at.is_(None))
        return session.scalar(statement)

    def list_active(
        self, session: Session, *, last_name: str | None, date_of_birth: date | None, phone_number: str | None
    ) -> list[Patient]:
        statement: Select[tuple[Patient]] = select(Patient).where(Patient.deleted_at.is_(None))
        if last_name:
            statement = statement.where(Patient.last_name.ilike(f"%{last_name.strip()}%"))
        if date_of_birth:
            statement = statement.where(Patient.date_of_birth == date_of_birth)
        if phone_number:
            statement = statement.where(Patient.phone_number == phone_number)
        return list(session.scalars(statement.order_by(Patient.created_at.desc())))

    def create(self, session: Session, values: dict) -> Patient:
        patient = Patient(**values)
        session.add(patient)
        session.flush()
        session.refresh(patient)
        return patient

    def update(self, session: Session, patient: Patient, values: dict) -> Patient:
        for field, value in values.items():
            setattr(patient, field, value)
        session.flush()
        session.refresh(patient)
        return patient

    def soft_delete(self, session: Session, patient: Patient) -> None:
        patient.deleted_at = datetime.now(timezone.utc)
        session.flush()
