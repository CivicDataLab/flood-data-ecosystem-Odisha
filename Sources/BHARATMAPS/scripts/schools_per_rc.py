import pandas as pd
import geopandas as gpd
import os

cwd = os.getcwd()
schools_gdf = gpd.read_file(cwd+'/Sources/BHARATMAPS/data/RawData/BharatMaps_Schools.geojson')
odisha_subdist_gdf = gpd.read_file(cwd+'/assets/subdistricts_479_odisha_osm.geojson')

schools_in_rcs = gpd.sjoin(odisha_subdist_gdf, schools_gdf.to_crs(odisha_subdist_gdf.crs), how="left", predicate="contains")
schools_count = schools_in_rcs.groupby(['id','name']).size().reset_index(name='schools_count')

schools_count.to_csv(cwd+'/Sources/BHARATMAPS/data/variables/Schools.csv', index=False)