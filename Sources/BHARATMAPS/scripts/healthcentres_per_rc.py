import pandas as pd
import geopandas as gpd
import os

cwd = os.getcwd()
health_centres_gdf = gpd.read_file(cwd+'/Sources/BHARATMAPS/data/RawData/BharatMaps_HealthCenters.geojson')
odisha_subdist_gdf = gpd.read_file(cwd+'/assets/subdistricts_479_odisha_osm.geojson')

health_centres_in_rcs = gpd.sjoin(odisha_subdist_gdf, health_centres_gdf.to_crs(odisha_subdist_gdf.crs), how="left", predicate="contains")
health_centres_count = health_centres_in_rcs.groupby(['id','name']).size().reset_index(name='health_centres_count')

health_centres_count.to_csv(cwd+'/Sources/BHARATMAPS/data/variables/healthcentres_per_rc.csv', index=False)