import uuid
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.repositories.patient import PatientRepository
from app.schemas.patient import normalize_phone

router = APIRouter(include_in_schema=False)
repository = PatientRepository()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[2] / "templates"))


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    last_name: str | None = Query(default=None, max_length=50),
    date_of_birth: date | None = None,
    phone_number: str | None = None,
    session: Session = Depends(get_db_session),
) -> HTMLResponse:
    phone_error = None
    normalized_phone = None
    if phone_number:
        try:
            normalized_phone = normalize_phone(phone_number)
        except ValueError:
            phone_error = "Enter a valid 10-digit U.S. phone number to filter by phone."

    patients = repository.list_active(
        session,
        last_name=last_name,
        date_of_birth=date_of_birth,
        phone_number=normalized_phone if not phone_error else "__no_match__",
    )
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "patients": patients,
            "patient_count": len(patients),
            "phone_error": phone_error,
            "filters": {"last_name": last_name or "", "date_of_birth": date_of_birth.isoformat() if date_of_birth else "", "phone_number": phone_number or ""},
        },
    )


@router.get("/dashboard/patients/{patient_id}", response_class=HTMLResponse)
def patient_detail(request: Request, patient_id: uuid.UUID, session: Session = Depends(get_db_session)) -> HTMLResponse:
    patient = repository.get_active(session, patient_id)
    return templates.TemplateResponse(
        request=request,
        name="patient_detail.html",
        context={"patient": patient},
        status_code=200 if patient else 404,
    )
