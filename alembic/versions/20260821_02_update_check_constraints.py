"""update_check_constraints_for_optional_fields

Revision ID: 20260821_02
Revises: b17019176727
Create Date: 2026-08-21 01:30:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = '20260821_02'
down_revision: Union[str, Sequence[str], None] = 'b17019176727'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old CHECK constraints that don't allow NULL
    op.drop_constraint('ck_patients_city_length', 'patients', type_='check')
    op.drop_constraint('ck_patients_state_format', 'patients', type_='check')
    op.drop_constraint('ck_patients_zip_code_format', 'patients', type_='check')
    
    # Add new CHECK constraints that allow NULL
    op.create_check_constraint(
        'ck_patients_city_length',
        'patients',
        'city IS NULL OR char_length(city) BETWEEN 1 AND 100'
    )
    op.create_check_constraint(
        'ck_patients_state_format',
        'patients',
        "state IS NULL OR state ~ '^[A-Z]{2}$'"
    )
    op.create_check_constraint(
        'ck_patients_zip_code_format',
        'patients',
        "zip_code IS NULL OR zip_code ~ '^[0-9]{5}(-[0-9]{4})?$'"
    )


def downgrade() -> None:
    # Drop nullable-aware CHECK constraints
    op.drop_constraint('ck_patients_city_length', 'patients', type_='check')
    op.drop_constraint('ck_patients_state_format', 'patients', type_='check')
    op.drop_constraint('ck_patients_zip_code_format', 'patients', type_='check')
    
    # Restore old CHECK constraints that require values
    op.create_check_constraint(
        'ck_patients_city_length',
        'patients',
        'char_length(city) BETWEEN 1 AND 100'
    )
    op.create_check_constraint(
        'ck_patients_state_format',
        'patients',
        "state ~ '^[A-Z]{2}$'"
    )
    op.create_check_constraint(
        'ck_patients_zip_code_format',
        'patients',
        "zip_code ~ '^[0-9]{5}(-[0-9]{4})?$'"
    )
