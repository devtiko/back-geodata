import uvicorn
from fastapi import FastAPI

from src.app.geocoding.router import router as geocoding_router
from src.app.locality.router import router as locality_router
from src.app.municipality.router import router as municipality_router
from src.app.state.router import router as state_router
from src.core.settings import settings

app = FastAPI(title="GeoData API", version="1.0.0")

app.include_router(router=state_router, prefix="/api/v1")
app.include_router(router=municipality_router, prefix="/api/v1")
app.include_router(router=locality_router, prefix="/api/v1")
app.include_router(router=geocoding_router, prefix="/api/v1")

if __name__ == "__main__":
  uvicorn.run("src.main:app", host=settings.APP_HOST, port=settings.APP_PORT)
