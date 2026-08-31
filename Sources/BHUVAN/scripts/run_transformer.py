import glob
import os
import subprocess
from datetime import date, timedelta

cwd = os.getcwd()
# print(cwd)
path = os.getcwd() + "/Sources/BHUVAN/"
script_path = cwd + "/Sources/BHUVAN/scripts/transformer.py"
PY = "/Users/stephensmathew/anaconda3/envs/flood_env/bin/python"

print(path)
for year in [2026]:
    print(year)
    year = str(year)
    for month in ["07", "08"]:
        files1 = glob.glob(path + f"data/tiffs/removed_watermarks/{year}_??_{month}*.tif")
        files2 = glob.glob(path + f"data/tiffs/removed_watermarks/{year}_??-??_{month}*.tif")
        files = files1 + files2
        if not files:
            print(f"No files for the month {month}")
            continue

        print("Number of images:", len(files))
        subprocess.run([PY, script_path, year, month],
            check=True
        )
