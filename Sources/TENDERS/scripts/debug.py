import pandas as pd
import os
import geopandas as gpd

data_path = os.getcwd()+'/Sources/TENDERS/data/'
od_gdf = gpd.read_file(os.getcwd()+'/Maps/od_ids-drr_shapefiles/odisha_block_final.geojson')

flood_tenders_geotagged_df = pd.read_csv(data_path + 'floodtenders_blockgeotagged.csv')

# Merge with GeoJSON using BLOCK_FINALISED 
flood_tenders_geotagged_df = flood_tenders_geotagged_df.merge(od_gdf,
                                 left_on=['DISTRICT_FINALISED', 'BLOCK_FINALISED'],
                                 right_on=['dtname', 'block_name'],
                                 how='left')

print("Rows:", len(flood_tenders_geotagged_df))
print("Non-null object_id:", flood_tenders_geotagged_df["object_id"].notna().sum())

