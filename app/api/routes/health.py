from datetime import datetime, timezone

from fastapi import APIRouter, Request, status

from app.core.config import settings

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK, summary="Service health check")
async def health_check(request: Request) -> dict[str, str]:
    """Return lightweight liveness information for local and Railway health checks."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": request.state.request_id,
    }
