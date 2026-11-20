
from app.controllers.health_controller import router as health_router
from app.controllers.reviews_controller import router as reviews_router

routers = [
    health_router,
    reviews_router,
]
