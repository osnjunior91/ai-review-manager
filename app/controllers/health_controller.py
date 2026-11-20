from fastapi import APIRouter
from typing_extensions import Final

import app.core as core
from app.core.config import get_settings

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