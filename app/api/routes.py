from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid

from app.services.file_processor import read_geospatial_file
from app.services.crs_handler import prepare_for_measurement
from app.services.measurement import calculate_measurements
from app.services.storage import files_db


router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/api/files/")
async def upload_file(file: UploadFile = File(...)):
    allowed_extensions = {".zip", ".kml"}

    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only .zip and .kml files are supported."
        )

    file_id = str(uuid.uuid4())

    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        original_gdf = read_geospatial_file(str(file_path))

        measurement_gdf = prepare_for_measurement(original_gdf)

        measurements = calculate_measurements(
            original_gdf,
            measurement_gdf
        )

        file_data = {
            "id": file_id,
            "filename": file.filename,
            "original_crs": str(original_gdf.crs),
            "measurement_crs": str(measurement_gdf.crs),
            "feature_count": len(original_gdf),
            "measurements": measurements
        }

        files_db[file_id] = file_data

        return file_data

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Could not process the geospatial file: {str(error)}"
        )
@router.get("/api/files/{file_id}/")
async def get_file(file_id: str):
    if file_id not in files_db:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    return files_db[file_id]

@router.get("/api/files/{file_id}/measurements/")
async def get_file_measurements(file_id: str):
    if file_id not in files_db:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    file_data = files_db[file_id]

    return {
        "file_id": file_data["id"],
        "filename": file_data["filename"],
        "feature_count": file_data["feature_count"],
        "original_crs": file_data["original_crs"],
        "measurement_crs": file_data["measurement_crs"],
        "measurements": file_data["measurements"]
    }