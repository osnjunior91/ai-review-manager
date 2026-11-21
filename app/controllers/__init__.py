
from app.controllers.health_controller import (
    router as health_router,
)
from app.controllers.reviews_controller import (
    router as reviews_router,
)
from app.controllers.review_analysis_controller import (
    router as review_analysis_router,
)
from app.controllers.review_reports_controller import (
    router as review_reports_router,
)


routers = [
    health_router,
    reviews_router,
    review_analysis_router,
    review_reports_router,
]
