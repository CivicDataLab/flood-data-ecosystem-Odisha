import glob
import os
import sys
import time

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
import rasterstats

if len(sys.argv) < 3:
    print("Please provide year and month as arguments.")
    sys.exit(1)

print(sys.argv)
year = str(sys.argv[1])
month = str(sys.argv[2])
print("Month: ", year + month)

tic = time.perf_counter()
path = os.getcwd() + "/Sources/BHUVAN/"

os.makedirs(path + "data/tiffs/stitched_monthly", exist_ok=True)
os.makedirs(path + "data/tiffs/removed_watermarks", exist_ok=True)
os.makedirs(path + "data/variables/inundation_pct", exist_ok=True)

od_rc_gdf = gpd.read_file(
    os.getcwd() + "/Maps/od_ids-drr_shapefiles/odisha_block_final.geojson"
)

# Corrected glob: YYYY_DD_MM_HH
files = glob.glob(
    path + f"data/tiffs/removed_watermarks/{year}_??_{month}_??_watermarkremoved.tif"
)
files_no_hour = glob.glob(
    path + f"data/tiffs/removed_watermarks/{year}_??_{month}_watermarkremoved.tif"
)
files = files + files_no_hour

print("Number of maps available for the month: ", len(files))

if len(files) == 0:
    print(f"No files found for {month}/{year}, skipping.")
    sys.exit(0)

# Read first raster then accumulate
with rasterio.open(files[0]) as raster:
    raster_array = raster.read(1).astype(np.int16)
    meta = raster.meta.copy()
    crs = raster.crs
    transform = raster.transform
    nodata = raster.nodata

for file in files[1:]:
    with rasterio.open(file) as src:
        raster_array += src.read(1).astype(np.int16)

# Update metadata
meta.update({
    "compress": "deflate",
    "count": 1,
    "dtype": "int16",
    "nodata": -1,
})

# Save stitched raster once
stitched_path = path + f"data/tiffs/stitched_monthly/stitched_{year}_{month}.tif"
with rasterio.open(stitched_path, "w", **meta) as dst:
    dst.write(raster_array, 1)
print(f"Saved stitched raster: {stitched_path}")


# --- ZONAL STATS: INUNDATION PERCENTAGE ---

def count_nonzero(x):
    return np.count_nonzero(x.compressed())


mean_dicts = rasterstats.zonal_stats(
    od_rc_gdf.to_crs(crs),
    raster_array,
    affine=transform,
    stats=["count"],
    nodata=nodata,
    add_stats={"count_nonzero": count_nonzero},
    geojson_out=True,
)

zonal_stats_df = pd.concat(
    [pd.DataFrame([rc["properties"]]) for rc in mean_dicts]
).reset_index(drop=True)

zonal_stats_df["inundation_pct"] = (
    zonal_stats_df["count_nonzero"] / zonal_stats_df["count"]
)


# --- ZONAL STATS: INTENSITY ---

def nonzero_mean(x):
    x = x.compressed()
    nonzero_values = x[x != 0]
    return np.mean(nonzero_values) if len(nonzero_values) > 0 else 0


max_val = raster_array.max()
intensity_array = (
    np.divide(raster_array, max_val) if max_val > 0 else raster_array.astype(float)
)

mean_dicts = rasterstats.zonal_stats(
    od_rc_gdf.to_crs(crs),
    intensity_array,
    affine=transform,
    stats=["mean", "sum"],
    nodata=nodata,
    add_stats={"intensity_mean_nonzero": nonzero_mean},
    geojson_out=True,
)

intensity_df = pd.concat(
    [pd.DataFrame([rc["properties"]]) for rc in mean_dicts]
).reset_index(drop=True)

intensity_df.rename(
    columns={"mean": "intensity_mean", "sum": "intensity_sum"}, inplace=True
)

zonal_stats_df = pd.merge(
    zonal_stats_df,
    intensity_df[["intensity_mean", "intensity_mean_nonzero", "intensity_sum", "object_id"]],
    on="object_id",
)

zonal_stats_df = zonal_stats_df[[
    "object_id",
    "count",
    "count_nonzero",
    "inundation_pct",
    "intensity_mean",
    "intensity_mean_nonzero",
    "intensity_sum",
]]

zonal_stats_df.columns = [
    "object_id",
    "count_bhuvan_pixels",
    "count_inundated_pixels",
    "inundation_pct",
    "inundation_intensity_mean",
    "inundation_intensity_mean_nonzero",
    "inundation_intensity_sum",
]

output_csv = path + f"data/variables/inundation_pct/inundation_pct_{year}_{month}.csv"
zonal_stats_df.to_csv(output_csv, index=False)
print(f"Saved CSV: {output_csv}")

toc = time.perf_counter()
print("Time Taken: {:.2f} seconds".format(toc - tic))