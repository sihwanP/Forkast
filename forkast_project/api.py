from ninja import NinjaAPI

# Initialize the main API Interface
api = NinjaAPI(
    title="Forkast AI API",
    version="1.0.0",
    description="Unified API for Forkast AI Platform (Django-only Architecture)"
)

# Register routers from apps
# api.add_router("/platform", platform_router) # Connected later when views are refactored
from apps.analytics.api import router as analytics_router
api.add_router("/analytics", analytics_router)
