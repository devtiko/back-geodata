import uvicorn
from fastapi import FastAPI

from src.core.settings import settings

app = FastAPI(title="GeoData API", version="1.0.0")

if __name__ == "__main__":
  uvicorn.run("src.main:app", host=settings.APP_HOST, port=settings.APP_PORT)
