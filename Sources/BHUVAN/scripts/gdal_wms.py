import os
import subprocess
import timeit

from osgeo import gdal

gdal.DontUseExceptions()

path = os.getcwd() + "/Sources/BHUVAN/"

layer_slugs = [
    "or_050911_flood",
    "or_080911_flood",
    "or_100911_flood",
    "or_120911_flood",
    "or_140911_flood",
    "or_170911_flood",
    "or_190911_flood",
    "or_260911_flood",
    "or_280911_flood",
    "or_290911_flood",
    "or_011011_flood",
    "or_28291013_flood",
    "or_291013_flood",
    "or_281013_flood",
    "or_281013m_flood",
    "or_251013_flood",
]

# Specify the state information to scrape data for.
state_info = {"state": "Odisha", "code": "od"}


for slug in layer_slugs:

    tiff_date = slug.split("_")[1]
    tiff_date = "-".join(tiff_date[i : i + 2] for i in range(0, len(tiff_date), 2))

    # Define your input and output paths
    input_xml_path = path + f"{state_info['state']}/data/inundation.xml"
    output_tiff_path = path + f"{state_info['state']}/data/tiffs/{tiff_date}.tif"

    bbox_od = "81.388586,17.810312,87.485805,22.567593"
    url_cache = (
        "https://bhuvan-ras2.nrsc.gov.in/mapcache"  # For cached data - before 2014
    )
    url_latest = "https://bhuvan-gp1.nrsc.gov.in/bhuvan/wms"  # For Latest data

    # Download the WMS(Web Map Sevice) layer and save as XML.
    command = [
        "gdal_translate",
        "-of",
        "WMS",
        f"WMS:{url_cache}?&LAYERS={slug}&TRANSPARENT=TRUE&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&FORMAT=image%2Fpng&SRS=EPSG%3A4326&BBOX={bbox_od}",
        f"{path}{state_info['state']}/data/inundation.xml",
    ]
    subprocess.run(command)

    # Specify the target resolution in the X and Y directions
    target_resolution_x = 0.0001716660336923202072
    target_resolution_y = -0.0001716684356881450775

    # Perform the warp operation using gdal.Warp()
    print("Warping Started")
    starttime = timeit.default_timer()

    gdal.Warp(
        output_tiff_path,
        input_xml_path,
        format="GTiff",
        xRes=0.0001716660336923202072,
        yRes=-0.0001716684356881450775,
        creationOptions=["COMPRESS=DEFLATE", "TILED=YES"],
        callback=gdal.TermProgress,
    )

    print("Time took to Warp: ", timeit.default_timer() - starttime)
    print(f"Warping completed. Output saved to: {output_tiff_path}")
