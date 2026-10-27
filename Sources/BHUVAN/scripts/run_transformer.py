import glob
import os
import subprocess

cwd = os.getcwd()
path = cwd + "/Sources/BHUVAN/"
script_path = cwd + "/Sources/BHUVAN/scripts/transformer.py"
PY = "/Users/stephensmathew/anaconda3/envs/flood_env/bin/python"

print(path)

for year in [2026]:
    print(f"\nYear: {year}")
    year = str(year)

    for month in ["09"]:
        files = glob.glob(
            path + f"data/tiffs/removed_watermarks/{year}_??_{month}_??_watermarkremoved.tif"
        )
        files_no_hour = glob.glob(
            path + f"data/tiffs/removed_watermarks/{year}_??_{month}_watermarkremoved.tif"
        )
        files = files + files_no_hour

        if not files:
            print(f"  No files for month {month}/{year}, skipping.")
            continue

        print(f"  Month {month}/{year} → {len(files)} file(s) found")
        subprocess.run([PY, script_path, year, month], check=True)