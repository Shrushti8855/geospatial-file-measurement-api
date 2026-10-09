from pathlib import Path
import geopandas as gpd


def read_geospatial_file(file_path: str) -> gpd.GeoDataFrame:
    """
    Read a KML or Shapefile ZIP file and return a GeoDataFrame.
    """

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension == ".kml":
        gdf = gpd.read_file(path, driver="KML")

    elif extension == ".zip":
        gdf = gpd.read_file(f"zip://{path}")

    else:
        raise ValueError("Unsupported geospatial file format.")

    return gdf