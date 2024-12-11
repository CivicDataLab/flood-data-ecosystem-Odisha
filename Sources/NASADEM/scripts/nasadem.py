import ee
import geemap
import os 
import time
import rasterio
import geopandas as gpd
import rasterstats
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


service_account = 'ids-drr@ids-drr.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, r'Sources\\NASADEM\\ids-drr-74983d4a2634.json')
ee.Initialize(credentials)

cwd = os.getcwd()
assam_rc_gdf = gpd.read_file(cwd+r'\Maps\BM_Odisha_district.geojson')

hp_sds = ee.FeatureCollection(r"projects/ids-drr/assets/bm_odisha_district")
geometry = hp_sds.geometry() 

# Get GEE Image
nasadem = ee.Image('NASA/NASADEM_HGT/001')
elevation = nasadem.select('elevation')

asset_id_elevation = 'users/slevin/NASADEM_DEM_30'
task_elevation = ee.batch.Export.image.toDrive(image=elevation.clip(geometry),
                                     region=geometry,
                                     description='NASADEM_DEM_30',
                                     #assetId=asset_id_elevation,
                                     folder='NASADEM',
                                     scale= 30,
                                     maxPixels=1e13)
task_elevation.start()
print('Task ID (elevation):', task_elevation.id)

#slope = ee.Terrain.slope(elevation)
asset_id_slope = 'users/slevin/NASADEM_SLOPE_30'
slope = ee.Terrain.slope(elevation)
task_slope = ee.batch.Export.image.toDrive(image=slope.clip(geometry),
                                     region=geometry,
                                     description='NASADEM_SLOPE_30',
                                     #assetId=asset_id_slope,
                                     folder='NASADEM',
                                     scale= 30,
                                     maxPixels=1e13)
task_slope.start()
print('Task ID (slope):', task_slope.id)

# Wait for tasks to finish
tasks = [task_elevation, task_slope]
for task in tasks:
    while task.status()['state'] in ['READY', 'RUNNING']:
        print(f'Waiting for task {task.id} to complete...')
        time.sleep(30)
    if task.status()['state'] == 'COMPLETED':
        print(f'Task {task.id} completed.')
    else:
        print(f'Task {task.id} failed.')


# Authenticate and initialize PyDrive
gauth = GoogleAuth()
#gauth.LocalWebserverAuth()  
scopes = ['https://www.googleapis.com/auth/drive']# Opens a web browser for authentication
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(service_account, r'Sources\\NASADEM\\ids-drr-74983d4a2634.json', scopes=scopes)

drive = GoogleDrive(gauth)


# Define the folder and filenames
folder_name = 'NASADEM'
filenames = ['NASADEM_DEM_30.tif', 'NASADEM_SLOPE_30.tif']


# Download files from Google Drive to local system
for filename in filenames:
    file_list = drive.ListFile({'q': f"'{folder_name}' in parents and title='{filename}'"}).GetList()
    for file in file_list:
        file.GetContentFile(os.path.join(cwd, filename))
        print(f'Downloaded {filename} to {cwd}')
'''
task.start()
print('Task ID:', task.id)
task_status = ee.batch.Task.list()
while any(t.status()['state'] in ['READY', 'RUNNING'] for t in task_status):
    print('Waiting for tasks to complete...')
    time.sleep(30)
    task_status = ee.batch.Task.list()

# Download assets locally using geemap
save_path = os.path.join(cwd, 'NASADEM_DEM_30.tif')
geemap.download_ee_image(asset_id=asset_id_elevation, filename=save_path, scale=30, region=geometry)
print('Downloaded elevation to', save_path)

save_path = os.path.join(cwd, 'NASADEM_SLOPE_30.tif')
geemap.download_ee_image(asset_id=asset_id_slope, filename=save_path, scale=30, region=geometry)
print('Downloaded slope to', save_path)


import os

import ee
import geemap

cwd = os.getcwd()

# Initialize Google Earth Engine.
service_account = "<service_account>"  # Add service account.
credentials = ee.ServiceAccountCredentials(
    service_account,
    f"{cwd}/<secret.env>",  # Add json with service account credentials.
)
ee.Initialize(credentials)

# Path to the administrative boundary shapefile.
state_boundary_path = cwd + "<administrative_boundary_shapefile_path>"
try:
    state_boundary = geemap.shp_to_ee(state_boundary_path)
    geometry = state_boundary.geometry()
    if state_boundary is None:
        raise ValueError("Conversion of shapefile to Earth Engine object failed.")
except Exception as e:
    print(f"Error converting shapefile: {e}")


# Get GEE Image
nasadem = ee.Image("NASA/NASADEM_HGT/001")

elevation = nasadem.select("elevation")
task = ee.batch.Export.image.toDrive(
    image=elevation.clip(geometry),
    region=geometry,
    description="NASADEM_DEM_30",
    folder="NASADEM",
    scale=30,
    maxPixels=1e13,
)
task.start()
print("Task ID:", task.id)


slope = ee.Terrain.slope(elevation)
task = ee.batch.Export.image.toDrive(
    image=slope.clip(geometry),
    region=geometry,
    description="NASADEM_SLOPE_30",
    folder="NASADEM",
    scale=30,
    maxPixels=1e13,
)
task.start()
print("Task ID:", task.id)
'''