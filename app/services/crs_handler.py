import geopandas as gpd


def prepare_for_measurement(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Prepare a GeoDataFrame for accurate area and length measurements.

    If the input CRS is geographic (latitude/longitude),
    automatically reproject to a suitable projected CRS.
    """

    if gdf.crs is None:
        raise ValueError("Input file does not contain a CRS.")

    # If CRS is already projected, keep it.
    if not gdf.crs.is_geographic:
        return gdf

    # Automatically select a suitable projected CRS
    projected_crs = gdf.estimate_utm_crs()

    if projected_crs is None:
        raise ValueError("Could not determine a suitable projected CRS.")

    return gdf.to_crs(projected_crs)