import os
import subprocess
import timeit

from osgeo import gdal

gdal.DontUseExceptions()

path = os.getcwd() + "/Sources/BHUVAN/"

date_strings = [
        #2025

    ]  # Sample date for assam - "2023_07_07_18"

# Specify the state information to scrape data for.
# state_info = {"state": "Assam", "code": "as"}


for dates in date_strings:

    # Define your input and output paths
    input_xml_path = path + "/data/inundation.xml"
    output_tiff_path = path + f"/data/tiffs/{dates}.tif"

    layer_od = "flood%3Aod"
    bbox_od =  "81.38 17.8 87.5 22.57"  #"77.08,23.87,84.63,30.40" #"89.6922970,23.990548,96.0205936,28.1690311"

    #url_cached = "https://bhuvan-ras2.nrsc.gov.in/mapcache"
    url_od = "https://bhuvan-gp1.nrsc.gov.in/bhuvan/gwc/service/wms"

    # Download the WMS(Web Map Sevice) layer and save as XML.
    command = [
        "gdal_translate",
        "-of",
        "WMS",
        f"WMS:{url_od}?&LAYERS={layer_od}_{dates}&TRANSPARENT=TRUE&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&FORMAT=image%2Fpng&SRS=EPSG%3A4326&BBOX={bbox_od}",
        f"{path}/data/inundation.xml",
    ]
    subprocess.run(command)

    # Specify the target resolution in the X and Y directions (50 meters)
    target_resolution_x = 0.00044915  # 0.0008983  # 0.0001716660336923202072
    target_resolution_y = -0.00044915  # -0.0008983  # -0.0001716684356881450775

    # Perform the warp operation using gdal.Warp()
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
