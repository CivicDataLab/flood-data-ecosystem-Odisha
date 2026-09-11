import os
import pandas as pd
from pathlib import Path
import re
import glob

main_directory = Path.cwd() / 'Sources'
print(main_directory)

# Iterate through all folders and sub-folders
for root, dirs, files in os.walk(main_directory):
    root_path = Path(root)
    print(root_path)

    if 'variables' in root_path.parts:
        csv_files = list(root_path.glob('*.csv'))  # No need for '**/*.csv'
        # Not a monthly source file -- a prior combined/aggregated output
        # sitting in the same input folder. Skip it so it never gets
        # re-ingested as if it were one of the monthly files.
        csv_files = [c for c in csv_files if c.stem != 'inundation_pct_combined']
        dfs = []
        for csv in csv_files:
            # Reset per-file so a csv that fails to match any pattern below
            # can never silently reuse timeperiod/file_name left over from
            # a previous csv or a previous folder.
            timeperiod = None
            file_name = None

            if any(folder in str(csv.parts) for folder in ['BHARATMAPS', 'GCN250', 'NASADEM', 'ANTYODAYA', 'WRIS']):
                timeperiod = ''
                file_name = csv.stem
            elif any(folder in str(csv.parts) for folder in ['WORLDPOP']):  # , 'WRIS']):
                year_match = re.findall(r'\d{4}', csv.name)
                if year_match:
                    timeperiod = year_match[0]
                    file_name = csv.stem[:-5]

            elif any("SENTINEL" in str(parent) for parent in csv.parents):
                date_match = re.findall(r'\d{4}-\d{2}-\d{2}', csv.name)
                if date_match:
                    timeperiod = date_match[0][:-3].replace('-', '_')
                    file_name = csv.stem

            else:
                date_match = re.findall(r'\d{4}_\d{2}', csv.name)
                if date_match:
                    timeperiod = date_match[0]
                # file_name is now always derived from the current csv,
                # regardless of whether the date regex matched -- this is
                # the line that was previously nested inside `if date_match:`,
                # which let it (and timeperiod) silently keep a stale value
                # from a prior file/folder when a filename didn't match.
                file_name = csv.stem[:-8]

            if timeperiod is None or file_name is None:
                raise ValueError(
                    f"Couldn't parse timeperiod/file_name from {csv} — "
                    f"check its naming convention against the branches above."
                )

            print("file: ", file_name)
            df = pd.read_csv(csv)
            df['timeperiod'] = timeperiod
            dfs.append(df)

        if dfs:  # Check if there are any dataframes to concatenate
            master_df = pd.concat(dfs)
            master_df.to_csv(main_directory / f'master/{file_name}.csv', index=False)

# IMD
path = main_directory / 'IMD/data/rain/csv'
csvs = glob.glob(str(path / '*.csv'))
dfs = []
for csv in csvs:
    month = re.findall(r'\d{4}_\d{2}', csv)[0]
    df = pd.read_csv(csv)
    df['timeperiod'] = month
    dfs.append(df)

master_df = pd.concat(dfs)
master_df = master_df.rename(columns={'max': 'max_rain', 'mean': 'mean_rain', 'sum': 'sum_rain'})
master_df.to_csv(main_directory / 'master/rainfall.csv', index=False)

# BHUVAN
path = main_directory / 'BHUVAN/data/variables/inundation_pct'
csvs = glob.glob(str(path / '*.csv'))
# Same combined/aggregated leftover as above -- this block globs the same
# folder directly, so it needs the same exclusion or it'll crash here too.
csvs = [c for c in csvs if Path(c).stem != 'inundation_pct_combined']
dfs = []
for csv in csvs:
    month = re.findall(r'\d{4}_\d{2}', csv)[0]
    df = pd.read_csv(csv)
    df['timeperiod'] = month
    dfs.append(df)

master_df = pd.concat(dfs)
# Renamed from 'inundation.csv' to 'inundation_pct.csv' so the output
# filename matches the variable name master2.py actually looks for.
master_df.to_csv(main_directory / 'master/inundation_pct.csv', index=False)


# NRSC
path = main_directory / 'NRSC/data/variables'
csvs = glob.glob(str(path / '*.csv'))
dfs = []
for csv in csvs:
    month = re.findall(r'\d{4}_\d{2}', csv)[0]
    df = pd.read_csv(csv)
    df['timeperiod'] = month
    dfs.append(df)

master_df = pd.concat(dfs)
master_df.to_csv(main_directory / 'master/runoff.csv', index=False)