from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.models.patient import Patient, Sex


def test_patient_model_compiles_for_postgresql():
    table_sql = str(CreateTable(Patient.__table__).compile(dialect=postgresql.dialect()))

    assert "CREATE TABLE patients" in table_sql
    assert "date_of_birth <= CURRENT_DATE" in table_sql
    assert [member.value for member in Sex] == ["Male", "Female", "Other", "Decline to Answer"]

    index_sql = [str(CreateIndex(index).compile(dialect=postgresql.dialect())) for index in Patient.__table__.indexes]
    assert any("WHERE deleted_at IS NULL" in statement for statement in index_sql)
