import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse, Response

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.web.routes.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.log_level)
    logging.getLogger(__name__).info("application_started")
    yield
    logging.getLogger(__name__).info("application_stopped")


app = FastAPI(
    title="CareCloud Voice Patient Registration API",
    version="0.1.0",
    description="Backend service for the CareCloud Voice AI patient registration assessment.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {"data": None, "error": {"code": "VALIDATION_ERROR", "message": "Validation failed", "details": exc.errors()}}
        ),
    )


@app.exception_handler(HTTPException)
async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {"data": None, "error": {"code": f"HTTP_{exc.status_code}", "message": message, "details": None}}
        ),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger(__name__).exception("unhandled_request_error", extra={"request_id": request.state.request_id})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "data": None,
            "error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected server error occurred", "details": None},
        },
    )


@app.middleware("http")
async def add_request_context(request: Request, call_next) -> Response:
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    started_at = time.perf_counter()

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    logging.getLogger("app.request").info(
        "request_completed",
        extra={"request_id": request_id},
    )
    response.headers["X-Response-Time-Ms"] = str(round((time.perf_counter() - started_at) * 1000, 2))
    return response


app.include_router(api_router)
app.include_router(dashboard_router)
