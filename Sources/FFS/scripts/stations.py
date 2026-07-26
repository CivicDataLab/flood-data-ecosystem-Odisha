import os

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

path = os.getcwd()
state_polygon = gpd.read_file(path + "/Maps/od_ids-drr_shapefiles/odisha_block_final.geojson")
stations = pd.read_csv(path + "/Sources/FFS/data/station_coordinates.csv")

# creating a geometry column
geometry = [
    Point(xy) for xy in zip(stations["lon"], stations["lat"])
]  # Coordinate reference system : WGS84
stations_gdf = gpd.GeoDataFrame(stations, crs="EPSG:4326", geometry=geometry)
# Spatial join with state polygon.
gpd.sjoin(
    stations_gdf.to_crs("EPSG:4326"), state_polygon.to_crs("EPSG:4326"), how="inner"
).to_file(
    path + "/Sources/FFS/data/state_stations.geojson",
    driver="GeoJSON",
)
