import json
import logging
import secrets
import uuid
from typing import Any

from fastapi import APIRouter, Body, Depends, Header, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db_session
from app.repositories.patient import PatientRepository
from app.schemas.patient import PatientCreate, PatientUpdate, normalize_phone

router = APIRouter(prefix="/vapi", tags=["vapi"])
repository = PatientRepository()
logger = logging.getLogger(__name__)


def compact_result(value: dict[str, Any]) -> str:
    """Vapi requires tool results as single-line strings."""
    return json.dumps(value, separators=(",", ":"), default=str)


def extract_tool_calls(payload: dict[str, Any]) -> list[dict[str, Any]]:
    message = payload.get("message", {})
    calls = message.get("toolCallList", [])
    if calls:
        return calls
    return [item.get("toolCall", {}) for item in message.get("toolWithToolCallList", []) if item.get("toolCall")]


def tool_name_and_arguments(tool_call: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    function = tool_call.get("function", {})
    name = tool_call.get("name") or function.get("name")
    arguments = tool_call.get("arguments") or tool_call.get("parameters") or function.get("parameters") or {}
    if isinstance(arguments, str):
        arguments = json.loads(arguments)
    return name, arguments if isinstance(arguments, dict) else {}


def execute_tool(name: str | None, arguments: dict[str, Any], session: Session) -> dict[str, Any]:
    if name == "find_patient_by_phone":
        phone_number = normalize_phone(str(arguments.get("phone_number", "")))
        patients = repository.list_active(session, last_name=None, date_of_birth=None, phone_number=phone_number)
        if not patients:
            return {"found": False}
        patient = patients[0]
        return {"found": True, "patient_id": str(patient.patient_id), "first_name": patient.first_name, "last_name": patient.last_name}

    if name == "create_patient":
        payload = PatientCreate.model_validate(arguments)
        patient = repository.create(session, payload.model_dump())
        session.commit()
        session.refresh(patient)
        logger.info("vapi_create_patient_payload=%s", payload.model_dump(mode="json"))
        return {"status": "created", "patient_id": str(patient.patient_id), "first_name": patient.first_name}

    if name == "update_patient":
        patient_id = uuid.UUID(str(arguments.pop("patient_id", "")))
        values = PatientUpdate.model_validate(arguments).model_dump(exclude_unset=True)
        if not values:
            raise ValueError("At least one update field is required")
        patient = repository.get_active(session, patient_id)
        if patient is None:
            return {"status": "not_found"}
        patient = repository.update(session, patient, values)
        session.commit()
        session.refresh(patient)
        return {"status": "updated", "patient_id": str(patient.patient_id), "first_name": patient.first_name}

    raise ValueError("Unsupported tool")


@router.post("/tools", summary="Vapi custom-tool webhook")
def vapi_tool_webhook(
    payload: dict[str, Any] = Body(...),
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_db_session),
) -> dict[str, list[dict[str, str]]]:
    expected_secret = settings.vapi_webhook_secret
    if not expected_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Vapi webhook is not configured")
    if not authorization or not secrets.compare_digest(authorization, f"Bearer {expected_secret}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Vapi webhook credentials")

    results: list[dict[str, str]] = []
    for tool_call in extract_tool_calls(payload):
        tool_call_id = str(tool_call.get("id", ""))
        name, arguments = tool_name_and_arguments(tool_call)
        try:
            result = execute_tool(name, arguments, session)
            results.append({"toolCallId": tool_call_id, "result": compact_result(result)})
        except (ValidationError, ValueError, TypeError, json.JSONDecodeError) as error:
            logger.warning("vapi_tool_error tool=%s error=%s", name, error)
            results.append({"toolCallId": tool_call_id, "error": str(error).replace("\n", " ")})
        except SQLAlchemyError:
            session.rollback()
            logger.exception("vapi_tool_database_error tool=%s", name)
            results.append({"toolCallId": tool_call_id, "error": "The record could not be saved."})
        except Exception:
            session.rollback()
            logger.exception("vapi_tool_unexpected_error tool=%s", name)
            results.append({"toolCallId": tool_call_id, "error": "The requested action could not be completed."})
    return {"results": results}
