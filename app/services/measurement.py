import geopandas as gpd


def calculate_measurement(row) -> float | None:
    """
    Calculate measurement for a single geometry.

    Polygon / MultiPolygon → area in square meters
    LineString / MultiLineString → length in meters
    Point → no measurement
    """

    geometry = row.geometry

    if geometry is None or geometry.is_empty:
        return None

    geometry_type = geometry.geom_type

    if geometry_type in {"Polygon", "MultiPolygon"}:
        return geometry.area

    if geometry_type in {"LineString", "MultiLineString"}:
        return geometry.length

    if geometry_type == "Point":
        return None

    return None


def calculate_measurements(
    original_gdf: gpd.GeoDataFrame,
    measurement_gdf: gpd.GeoDataFrame,
) -> list:
    """
    Calculate measurements while preserving the original
    feature properties and geometry information.
    """

    results = []

    for index in measurement_gdf.index:
        original_row = original_gdf.loc[index]
        measurement_row = measurement_gdf.loc[index]

        measurement = calculate_measurement(measurement_row)

        properties = {}

        for column in original_gdf.columns:
            if column != "geometry":
                value = original_row[column]

                if hasattr(value, "item"):
                    value = value.item()

                if value is None:
                    properties[column] = None
                elif isinstance(value, float) and value != value:
                    properties[column] = None
                elif str(value) == "NaT":
                    properties[column] = None
                else:
                    properties[column] = value

        results.append(
            {
                "feature_id": index,
                "geometry_type": measurement_row.geometry.geom_type,
                "crs": str(measurement_gdf.crs),
                "properties": properties,
                "measurement": measurement,
            }
        )

    return results