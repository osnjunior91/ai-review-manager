from fastapi import APIRouter
from typing_extensions import Final

import app.core as core
from app.core.config import get_settings
from app.core.database import MongoDatabase
from pymongo.errors import PyMongoError
from fastapi import HTTPException, status

settings = get_settings()

router = APIRouter()

@router.get("/health")
def read_health():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "description": settings.app_description,
        "version": settings.api_version
    }

@router.get("/version")
def read_version():
    return {
        "version": settings.api_version
    }

@router.get("/health/database")
def check_database():
    db = MongoDatabase()

    try:
        db.ping()

        return {
            "status": "healthy",
            "database": "mongodb",
            "connection": "connected"
        }

    except PyMongoError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "mongodb",
                "connection": "disconnected"
            }
        )

    finally:
        db.close()