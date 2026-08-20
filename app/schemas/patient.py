import re
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.patient import Sex

US_STATES = frozenset(
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC".split()
)
NAME_PATTERN = re.compile(r"^[A-Za-z]+(?:['-][A-Za-z]+)*$")
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ZIP_PATTERN = re.compile(r"^\d{5}(?:-\d{4})?$")
MEMBER_ID_PATTERN = re.compile(r"^[A-Za-z0-9]+$")


def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError("must be a valid 10-digit U.S. phone number")
    return digits


class PatientCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    date_of_birth: date
    sex: Sex
    phone_number: str
    email: str | None = Field(default=None, max_length=254)
    address_line_1: str = Field(min_length=1, max_length=200)
    address_line_2: str | None = Field(default=None, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str
    zip_code: str
    insurance_provider: str | None = Field(default=None, max_length=200)
    insurance_member_id: str | None = Field(default=None, max_length=100)
    preferred_language: str = Field(default="English", min_length=1, max_length=100)
    emergency_contact_name: str | None = Field(default=None, max_length=100)
    emergency_contact_phone: str | None = None

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not NAME_PATTERN.fullmatch(value):
            raise ValueError("may only contain letters, hyphens, and apostrophes")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        if value is None:
            return None
        if value > date.today():
            raise ValueError("must not be in the future")
        return value

    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_phone(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if not value:
            return None
        if not EMAIL_PATTERN.fullmatch(value):
            raise ValueError("must be a valid email address")
        return value.lower()

    @field_validator("state")
    @classmethod
    def validate_state(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.upper()
        if normalized not in US_STATES:
            raise ValueError("must be a valid two-letter U.S. state abbreviation")
        return normalized

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not ZIP_PATTERN.fullmatch(value):
            raise ValueError("must be a valid 5-digit ZIP or ZIP+4 code")
        return value

    @field_validator("insurance_member_id")
    @classmethod
    def validate_member_id(cls, value: str | None) -> str | None:
        if not value:
            return None
        if not MEMBER_ID_PATTERN.fullmatch(value):
            raise ValueError("must be alphanumeric")
        return value


class PatientUpdate(PatientCreate):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    date_of_birth: date | None = None
    sex: Sex | None = None
    phone_number: str | None = None
    address_line_1: str | None = Field(default=None, min_length=1, max_length=200)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = None
    zip_code: str | None = None
    preferred_language: str | None = Field(default=None, min_length=1, max_length=100)

    @model_validator(mode="after")
    def disallow_null_required_fields(self) -> "PatientUpdate":
        required_fields = {
            "first_name",
            "last_name",
            "date_of_birth",
            "sex",
            "phone_number",
            "address_line_1",
            "city",
            "state",
            "zip_code",
            "preferred_language",
        }
        for field_name in self.model_fields_set & required_fields:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        return self


class PatientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patient_id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: date
    sex: Sex
    phone_number: str
    email: str | None
    address_line_1: str
    address_line_2: str | None
    city: str
    state: str
    zip_code: str
    insurance_provider: str | None
    insurance_member_id: str | None
    preferred_language: str
    emergency_contact_name: str | None
    emergency_contact_phone: str | None
    created_at: datetime
    updated_at: datetime
