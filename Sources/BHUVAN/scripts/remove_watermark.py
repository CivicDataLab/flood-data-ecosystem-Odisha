import glob
import os

import numpy as np
import rasterio
from rasterio.crs import CRS

path = os.getcwd() + "/Sources/BHUVAN"
print("Base path: ", path)

os.makedirs(path + "/data/tiffs/removed_watermarks", exist_ok=True)

files = glob.glob(path + "/data/tiffs/*.tif")
print("Files with watermark: ", len(files))

wm_removed_files = glob.glob(path + "/data/tiffs/removed_watermarks/*.tif")
print("Files without watermark: ", len(wm_removed_files))

dates_watermark_removed = []
for file in wm_removed_files:
    dates_watermark_removed.append(file.split(r"/")[-1].split("_w")[0])

for file in files:
    date_string = file.split(r"/")[-1][:-4]
    if date_string in dates_watermark_removed:
        continue
    print(f"Processing: {date_string}")

    with rasterio.open(file) as raster:
        image1_ar = raster.read()
        meta = raster.meta.copy()

    a4 = image1_ar[3, :, :]

    # Odisha: flood = band4 > 0 (max is 157, no watermark at 255)
    flood_mask = (a4 > 0).astype("uint8")

    nonzero = np.count_nonzero(flood_mask)
    print(f"  Flood pixels detected: {nonzero}")

    meta.update({
        "compress": "deflate",
        "count": 1,
        "dtype": "uint8",
        "crs": CRS.from_epsg(4326),
        "nodata": 0,
    })

    output_path = path + f"/data/tiffs/removed_watermarks/{date_string}_watermarkremoved.tif"
    with rasterio.open(output_path, "w", **meta) as dst:
        dst.write(flood_mask, 1)

    print(f"  Saved: {output_path}")

print("\nDone.")