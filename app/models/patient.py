import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import CheckConstraint, Date, DateTime, Enum as SqlEnum, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Sex(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    DECLINE_TO_ANSWER = "Decline to Answer"


class Patient(Base):
    """Persistent patient demographic record. Phone numbers are stored as 10 digits."""

    __tablename__ = "patients"
    __table_args__ = (
        CheckConstraint("char_length(first_name) BETWEEN 1 AND 50", name="ck_patients_first_name_length"),
        CheckConstraint("first_name ~ '^[A-Za-z]+([\\x27-][A-Za-z]+)*$'", name="ck_patients_first_name_format"),
        CheckConstraint("char_length(last_name) BETWEEN 1 AND 50", name="ck_patients_last_name_length"),
        CheckConstraint("last_name ~ '^[A-Za-z]+([\\x27-][A-Za-z]+)*$'", name="ck_patients_last_name_format"),
        CheckConstraint("date_of_birth <= CURRENT_DATE", name="ck_patients_date_of_birth_not_future"),
        CheckConstraint("phone_number ~ '^[0-9]{10}$'", name="ck_patients_phone_number_format"),
        # Optional field constraints (only apply when values are present)
        CheckConstraint("city IS NULL OR char_length(city) BETWEEN 1 AND 100", name="ck_patients_city_length"),
        CheckConstraint("state IS NULL OR state ~ '^[A-Z]{2}$'", name="ck_patients_state_format"),
        CheckConstraint("zip_code IS NULL OR zip_code ~ '^[0-9]{5}(-[0-9]{4})?$'", name="ck_patients_zip_code_format"),
        CheckConstraint("emergency_contact_phone IS NULL OR emergency_contact_phone ~ '^[0-9]{10}$'", name="ck_patients_emergency_contact_phone_format"),
        CheckConstraint("insurance_member_id IS NULL OR insurance_member_id ~ '^[A-Za-z0-9]+$'", name="ck_patients_insurance_member_id_format"),
        Index("ix_patients_last_name", "last_name"),
        Index("ix_patients_date_of_birth", "date_of_birth"),
        Index("ix_patients_phone_number_active", "phone_number", postgresql_where="deleted_at IS NULL"),
    )

    # Required fields (Phase 1: minimal voice collection)
    patient_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    sex: Mapped[Sex] = mapped_column(
        SqlEnum(Sex, name="sex_enum", values_callable=lambda enum_class: [member.value for member in enum_class]),
        nullable=False,
    )
    phone_number: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Optional fields (nullable at database level)
    email: Mapped[str | None] = mapped_column(String(254))
    address_line_1: Mapped[str | None] = mapped_column(String(200))
    address_line_2: Mapped[str | None] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(2))
    zip_code: Mapped[str | None] = mapped_column(String(10))
    insurance_provider: Mapped[str | None] = mapped_column(String(200))
    insurance_member_id: Mapped[str | None] = mapped_column(String(100))
    preferred_language: Mapped[str | None] = mapped_column(String(100), server_default="English")
    emergency_contact_name: Mapped[str | None] = mapped_column(String(100))
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(10))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
