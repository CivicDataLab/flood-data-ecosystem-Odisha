import os
import subprocess
import timeit

from osgeo import gdal

gdal.DontUseExceptions()

os.environ["GDAL_HTTP_TIMEOUT"] = "120"
os.environ["GDAL_HTTP_CONNECTTIMEOUT"] = "30"
os.environ["GDAL_HTTP_MAX_RETRY"] = "5"
os.environ["GDAL_HTTP_RETRY_DELAY"] = "5"
gdal.SetConfigOption("GDAL_HTTP_TIMEOUT", "120")
gdal.SetConfigOption("GDAL_HTTP_MAX_RETRY", "5")
gdal.SetConfigOption("GDAL_HTTP_RETRY_DELAY", "5")

path = os.getcwd() + "/Sources/BHUVAN/"
os.makedirs(path + "data/tiffs/", exist_ok=True)

date_strings = [
    "2026_24_08_18",
    "2026_19_08_06",
    "2026_16_08_18",
    "2026_15_08_18",
    "2026_14_08_18",
    "2026_14_08_06",
    "2026_07_08_06",
    "2026_06_08_18",
    "2026_05_08_18",
    "2026_04_08_18",
    "2026_02_08_06"
]

layer_od = "flood%3Aod"
bbox_od = "81.38,17.8,87.5,22.57"

# Switched from the GWC endpoint (returns HTTP 400 on every request — confirmed
# by direct testing) to the plain WMS endpoint, same as UP.
url_od = "https://bhuvan-gp1.nrsc.gov.in/bhuvan/wms"

target_resolution_x = 0.00044915
target_resolution_y = -0.00044915

bbox_parts = [float(v) for v in bbox_od.split(",")]
bbox_w = bbox_parts[2] - bbox_parts[0]
bbox_h = bbox_parts[3] - bbox_parts[1]
width_px = round(bbox_w / target_resolution_x)
height_px = round(bbox_h / abs(target_resolution_y))

for dates in date_strings:
    input_xml_path = path + "/data/inundation.xml"
    output_tiff_path = path + f"/data/tiffs/{dates}.tif"

    command = [
        "gdal_translate", "-of", "WMS",
        f"WMS:{url_od}?&LAYERS={layer_od}_{dates}&TRANSPARENT=TRUE&SERVICE=WMS"
        f"&VERSION=1.1.1&REQUEST=GetMap&STYLES=&FORMAT=image%2Fpng&SRS=EPSG%3A4326"
        f"&BBOX={bbox_od}&WIDTH={width_px}&HEIGHT={height_px}",
        f"{path}/data/inundation.xml",
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    xml_content = open(input_xml_path).read()
    if result.returncode != 0 or "ServiceException" in xml_content:
        print(f"WMS fetch failed for {dates}")
        print("stderr:", result.stderr)
        print("xml:", xml_content[:500])
        continue

    xml_content = xml_content.replace("<BlockSizeX>1024</BlockSizeX>", "<BlockSizeX>512</BlockSizeX>")
    xml_content = xml_content.replace("<BlockSizeY>1024</BlockSizeY>", "<BlockSizeY>512</BlockSizeY>")
    with open(input_xml_path, "w") as f:
        f.write(xml_content)

    print("Warping Started")
    starttime = timeit.default_timer()

    gdal.Warp(
        output_tiff_path,
        input_xml_path,
        format="GTiff",
        xRes=target_resolution_x,
        yRes=target_resolution_y,
        creationOptions=["COMPRESS=DEFLATE", "TILED=YES"],
        callback=gdal.TermProgress,
    )

    print("Time took to Warp: ", timeit.default_timer() - starttime)
    print(f"Warping completed. Output saved to: {output_tiff_path}")

    # Sanity check: gdal.Warp doesn't error out on failed tile fetches, it just
    # fills them blank — so verify there's actually data before moving on.

import rasterio
import numpy as np

for f in ["2026_31_07_18", "2026_30_07_18", "2026_28_07_06", "2026_07_07_06"]:
    with rasterio.open(f"Sources/BHUVAN/data/tiffs/{f}.tif") as src:
        a = src.read(4)
        print(f, "max:", a.max(), "nonzero:", np.count_nonzero(a))