# Geospatial File Measurement API

A RESTful API built with **FastAPI, GeoPandas, Shapely, and PyProj** to upload, process, and calculate geometric measurements from geospatial files.

The API supports KML files and zipped Shapefiles, extracts feature information, handles Coordinate Reference Systems (CRS), and calculates polygon areas and line lengths.

## Features

* Upload geospatial files in KML (`.kml`) and zipped Shapefile (`.zip`) formats.
* Extract feature geometry types and properties.
* Calculate polygon and multipolygon areas in square metres.
* Calculate line and multiline lengths in metres.
* Handle point geometries without calculating measurements.
* Detect and handle geographic Coordinate Reference Systems.
* Reproject geographic data to a suitable projected CRS before measurement.
* Provide REST API endpoints for uploading files, retrieving file details, and retrieving measurements.
* Return structured JSON responses and meaningful HTTP errors.

## Technology Stack

| Technology       | Purpose                                     |
| ---------------- | ------------------------------------------- |
| Python           | Core programming language                   |
| FastAPI          | REST API framework                          |
| Uvicorn          | ASGI server                                 |
| GeoPandas        | Geospatial file processing                  |
| Shapely          | Geometry operations                         |
| PyProj           | Coordinate reference system transformations |
| python-multipart | Multipart file uploads                      |

## Project Structure

```text
geospatial-file-measurement-api/
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── services/
│   │   ├── file_processor.py
│   │   ├── measurement.py
│   │   ├── crs_handler.py
│   │   └── storage.py
│   ├── models/
│   ├── utils/
│   └── main.py
├── sample_data/
│   └── test_polygon.kml
├── tests/
├── uploads/
├── requirements.txt
├── run.py
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

* Python 3.12 or another Python version compatible with the installed dependencies.
* pip
* Git (for cloning the repository)

### 1. Clone the repository

```bash
git clone https://github.com/Shrushti8855/geospatial-file-measurement-api.git
cd geospatial-file-measurement-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the API server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

* **Base URL:** http://127.0.0.1:8000
* **Interactive API documentation:** http://127.0.0.1:8000/docs
* **OpenAPI schema:** http://127.0.0.1:8000/openapi.json

## API Endpoints

### 1. Upload a Geospatial File

**Endpoint:** `POST /api/files/`

Uploads and processes a KML file or a ZIP archive containing a supported Shapefile dataset.

**Request format:** `multipart/form-data`

**Form field:** `file`

Example:

```bash
curl -X POST "http://127.0.0.1:8000/api/files/" \
  -F "file=@sample_data/test_polygon.kml"
```

Example response:

```json
{
  "id": "generated-file-uuid",
  "filename": "test_polygon.kml",
  "original_crs": "EPSG:4326",
  "measurement_crs": "EPSG:32643",
  "feature_count": 1,
  "measurements": [
    {
      "feature_id": 0,
      "geometry_type": "Polygon",
      "crs": "EPSG:32643",
      "properties": {
        "Name": "Test Polygon"
      },
      "measurement": 1168194.042862256
    }
  ]
}
```

The UUID and properties in this example are illustrative. Actual results depend on the uploaded file.

### 2. Retrieve File Information

**Endpoint:** `GET /api/files/{file_id}/`

Retrieves the stored information associated with an uploaded file ID.

Example:

```bash
curl "http://127.0.0.1:8000/api/files/YOUR_FILE_ID/"
```

### 3. Retrieve File Measurements

**Endpoint:** `GET /api/files/{file_id}/measurements/`

Retrieves the feature count, CRS information, and calculated measurements for an uploaded file.

Example:

```bash
curl "http://127.0.0.1:8000/api/files/YOUR_FILE_ID/measurements/"
```

Replace `YOUR_FILE_ID` with the ID returned by the upload endpoint.

## Measurement Logic

The API selects the measurement operation according to the geometry type.

| Geometry Type   | Operation      | Unit               |
| --------------- | -------------- | ------------------ |
| Polygon         | Area           | Square metres (m²) |
| MultiPolygon    | Area           | Square metres (m²) |
| LineString      | Length         | Metres (m)         |
| MultiLineString | Length         | Metres (m)         |
| Point           | No measurement | Not applicable     |

Empty geometries return no measurement. Unsupported geometry types also return no measurement in the current implementation.

## Coordinate Reference System (CRS) Handling

Accurate geospatial measurement requires an appropriate coordinate reference system.

Geographic CRS such as `EPSG:4326` represents locations using longitude and latitude in angular units. Calculating planar areas or lengths directly from these coordinates would not produce square metres or metres.

The API follows this process:

1. Read the input file and inspect its CRS.
2. Check whether the CRS is geographic.
3. Estimate a suitable UTM projected CRS for geographic data.
4. Reproject the geometries when necessary.
5. Calculate area or length using the projected geometries.

For the sample polygon around Pune, the estimated measurement CRS is `EPSG:32643`.

**Unit consideration:** The current implementation assumes that the projected CRS uses metres. Other projected CRSs may use different units and would require unit-aware handling.

## Processing Workflow

```text
Geospatial File Upload
        |
        v
File Extension Validation
        |
        v
GeoPandas File Processing
        |
        v
CRS Inspection
        |
        v
CRS Transformation (if needed)
        |
        v
Geometry Type Detection
        |
        v
Area / Length Calculation
        |
        v
In-Memory Result Storage
        |
        v
JSON API Response
```

## Error Handling

| HTTP Status                | Description                                           |
| -------------------------- | ----------------------------------------------------- |
| `200 OK`                   | Request processed successfully                        |
| `400 Bad Request`          | Unsupported file extension or file-processing failure |
| `404 Not Found`            | Requested file ID does not exist                      |
| `422 Unprocessable Entity` | Invalid request parameters or request format          |

## Testing

The API has been manually tested through the FastAPI Swagger interface.

Verified functionality includes:

* Uploading a sample KML polygon.
* Reading its geographic CRS.
* Reprojecting the geometry for measurement.
* Calculating the polygon area.
* Retrieving file details using the generated ID.
* Retrieving measurements using the measurements endpoint.
* Returning a 404 response for an invalid file ID.

The sample file is located at `sample_data/test_polygon.kml`.

## Current Limitations

* File metadata and measurements are stored in an in-memory Python dictionary.
* Stored records are lost when the server process restarts.
* File validation currently checks the filename extension; stronger content and archive validation is needed.
* The current implementation does not include comprehensive automated tests.
* Projected CRS units are assumed to be metres.

## Future Improvements

* Add persistent storage using SQLite or PostgreSQL.
* Add automated unit and integration tests using pytest.
* Improve upload validation and file-size limits.
* Add safer ZIP archive validation.
* Add structured logging and consistent response schemas.
* Support additional geospatial file formats.
* Add deployment configuration and API authentication where appropriate.

## Author

**Shrushti Shewale**

* GitHub: https://github.com/Shrushti8855

## License

No license has been selected yet. Add an appropriate open-source license before distributing the project under specific reuse terms.
