from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Geospatial File Measurement API",
    description="API for processing geospatial files and calculating geometry measurements.",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Geospatial File Measurement API is running"
    }