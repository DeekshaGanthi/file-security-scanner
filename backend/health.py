"""Independent process and database health checks."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.database import check_database

router = APIRouter()


@router.get("/health/live")
def live():
    return {"status": "alive"}


@router.get("/health/ready")
def ready():
    try:
        check_database()
        return {"status": "ready", "database": "connected"}
    except Exception:
        # Connection errors may contain credentials or infrastructure details.
        return JSONResponse(status_code=503, content={
            "status": "not_ready", "database": "unavailable"
        })
