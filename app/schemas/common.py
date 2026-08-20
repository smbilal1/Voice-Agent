from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Any | None = None


class ApiResponse(BaseModel, Generic[DataT]):
    data: DataT
    error: None = None


class ErrorResponse(BaseModel):
    data: None = None
    error: ErrorDetail
