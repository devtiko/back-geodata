import uvicorn
from fastapi import FastAPI

app = FastAPI(title="GeoData API", version="1.0.0")

if __name__ == "__main__":
  uvicorn.run("src.main:app")
