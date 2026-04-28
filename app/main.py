from fastapi import FastAPI

from app.api import auth_controller, vehicle_controller
from app.core.config import settings

app = FastAPI(title=settings.project_name)

app.include_router(auth_controller.router)
app.include_router(vehicle_controller.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
