import os
import subprocess
import timeit

from osgeo import gdal

gdal.DontUseExceptions()

path = os.getcwd() + "/Sources/BHUVAN/"

date_strings = [
        #2025
    "2025_24_08_06",
    "2025_09_07_18",
    
    #2024
                
    #2023
    

  # 2022
    "2022_16_08",
    "2022_18_08_18",
    "2022_19_08_18",
    "2022_21_08_06",
    "2022_22_08_18",
    "2022_24_08_18",
    "2022_28_08_06",
    "2022_05_10_18",

    # 2021
    "2021_25_05",
    "2021_25_05_10",
    "2021_26_05",
    "2021_27_05",
    "2021_27_05_06",
    "2021_27_05_18",
    "2021_28_05",
    "2021_29_05",
    "2021_29_05_06",
    "2021_29_05_18",
    "2021_31_05_18",
    "2021_03_06_06",
    "2021_14_09",
    "2021_27_09_18",
    "2021_05_12_18",

    # 2020
    "2020_22_05",
    "2020_23_05_18",
    "2020_26_08",
    "2020_26_08_06",
    "2020_27_08",
    "2020_28_08",
    "2020_28_08_11",
    "2020_28_08_18",
    "2020_29_08",
    "2020_29_08_18",
    "2020_30_08",
    "2020_31_08",
    "2020_03_09_11",

    # 2019
    "2019_03_05_18",
    "2019_04_05",
    "2019_04_05_06",
    "2019_05_05",
    "2019_06_05",
    "2019_08_05",
    "2019_09_05",

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
