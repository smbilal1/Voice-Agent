"""create patients table

Revision ID: 20260820_01
Revises:
Create Date: 2026-08-20 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260820_01"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

sex_enum = sa.Enum("Male", "Female", "Other", "Decline to Answer", name="sex_enum")
# The type is created explicitly in `upgrade`; the table column must not attempt
# to create it again (which causes DuplicateObject on PostgreSQL).
sex_enum_column = postgresql.ENUM(
    "Male", "Female", "Other", "Decline to Answer", name="sex_enum", create_type=False
)


def upgrade() -> None:
    sex_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "patients",
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("sex", sex_enum_column, nullable=False),
        sa.Column("phone_number", sa.String(length=10), nullable=False),
        sa.Column("email", sa.String(length=254)),
        sa.Column("address_line_1", sa.String(length=200), nullable=False),
        sa.Column("address_line_2", sa.String(length=200)),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=2), nullable=False),
        sa.Column("zip_code", sa.String(length=10), nullable=False),
        sa.Column("insurance_provider", sa.String(length=200)),
        sa.Column("insurance_member_id", sa.String(length=100)),
        sa.Column("preferred_language", sa.String(length=100), server_default="English", nullable=False),
        sa.Column("emergency_contact_name", sa.String(length=100)),
        sa.Column("emergency_contact_phone", sa.String(length=10)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("char_length(first_name) BETWEEN 1 AND 50", name="ck_patients_first_name_length"),
        sa.CheckConstraint("first_name ~ '^[A-Za-z]+([\\x27-][A-Za-z]+)*$'", name="ck_patients_first_name_format"),
        sa.CheckConstraint("char_length(last_name) BETWEEN 1 AND 50", name="ck_patients_last_name_length"),
        sa.CheckConstraint("last_name ~ '^[A-Za-z]+([\\x27-][A-Za-z]+)*$'", name="ck_patients_last_name_format"),
        sa.CheckConstraint("date_of_birth <= CURRENT_DATE", name="ck_patients_date_of_birth_not_future"),
        sa.CheckConstraint("phone_number ~ '^[0-9]{10}$'", name="ck_patients_phone_number_format"),
        sa.CheckConstraint("char_length(city) BETWEEN 1 AND 100", name="ck_patients_city_length"),
        sa.CheckConstraint("state ~ '^[A-Z]{2}$'", name="ck_patients_state_format"),
        sa.CheckConstraint("zip_code ~ '^[0-9]{5}(-[0-9]{4})?$'", name="ck_patients_zip_code_format"),
        sa.CheckConstraint("emergency_contact_phone IS NULL OR emergency_contact_phone ~ '^[0-9]{10}$'", name="ck_patients_emergency_contact_phone_format"),
        sa.CheckConstraint("insurance_member_id IS NULL OR insurance_member_id ~ '^[A-Za-z0-9]+$'", name="ck_patients_insurance_member_id_format"),
        sa.PrimaryKeyConstraint("patient_id"),
    )
    op.create_index("ix_patients_last_name", "patients", ["last_name"])
    op.create_index("ix_patients_date_of_birth", "patients", ["date_of_birth"])
    op.create_index(
        "ix_patients_phone_number_active",
        "patients",
        ["phone_number"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_patients_phone_number_active", table_name="patients")
    op.drop_index("ix_patients_date_of_birth", table_name="patients")
    op.drop_index("ix_patients_last_name", table_name="patients")
    op.drop_table("patients")
    sex_enum.drop(op.get_bind(), checkfirst=True)
