from fastapi import FastAPI
from app.controllers.reviews_controller import router as reviews_router
from app.controllers.health_controller import router as health_router
from typing_extensions import Final
from app.controllers import routers
from app.core.config import get_settings

app = FastAPI(
        title=get_settings().app_name, 
        description=get_settings().app_description, 
        version=get_settings().api_version
    )


for router in routers:
    app.include_router(router)
