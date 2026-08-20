import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.repositories.patient import PatientRepository
from app.schemas.common import ApiResponse
from app.schemas.patient import PatientCreate, PatientRead, PatientUpdate, normalize_phone

router = APIRouter(prefix="/patients")
repository = PatientRepository()


def patient_or_404(session: Session, patient_id: uuid.UUID):
    patient = repository.get_active(session, patient_id)
    if patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return patient


@router.get("", response_model=ApiResponse[list[PatientRead]], summary="List active patients")
def list_patients(
    last_name: str | None = Query(default=None, max_length=50),
    date_of_birth: date | None = None,
    phone_number: str | None = None,
    session: Session = Depends(get_db_session),
) -> dict:
    normalized_phone = None
    if phone_number:
        try:
            normalized_phone = normalize_phone(phone_number)
        except ValueError as error:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error

    patients = repository.list_active(
        session, last_name=last_name, date_of_birth=date_of_birth, phone_number=normalized_phone
    )
    return {"data": [PatientRead.model_validate(patient) for patient in patients], "error": None}


@router.get("/{patient_id}", response_model=ApiResponse[PatientRead], summary="Retrieve an active patient")
def get_patient(patient_id: uuid.UUID, session: Session = Depends(get_db_session)) -> dict:
    patient = patient_or_404(session, patient_id)
    return {"data": PatientRead.model_validate(patient), "error": None}


@router.post("", response_model=ApiResponse[PatientRead], status_code=status.HTTP_201_CREATED, summary="Create a patient")
def create_patient(payload: PatientCreate, session: Session = Depends(get_db_session)) -> dict:
    try:
        patient = repository.create(session, payload.model_dump())
    except IntegrityError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient data violates a database constraint") from error
    return {"data": PatientRead.model_validate(patient), "error": None}


@router.put("/{patient_id}", response_model=ApiResponse[PatientRead], summary="Partially update an active patient")
def update_patient(patient_id: uuid.UUID, payload: PatientUpdate, session: Session = Depends(get_db_session)) -> dict:
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="At least one field is required")
    patient = patient_or_404(session, patient_id)
    try:
        patient = repository.update(session, patient, values)
    except IntegrityError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient data violates a database constraint") from error
    return {"data": PatientRead.model_validate(patient), "error": None}


@router.delete("/{patient_id}", response_model=ApiResponse[dict[str, uuid.UUID | datetime]], summary="Soft-delete a patient")
def delete_patient(patient_id: uuid.UUID, session: Session = Depends(get_db_session)) -> dict:
    patient = patient_or_404(session, patient_id)
    repository.soft_delete(session, patient)
    return {"data": {"patient_id": patient.patient_id, "deleted_at": patient.deleted_at}, "error": None}
