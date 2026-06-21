import pandas as pd
import glob
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import sys

# Check argument
if len(sys.argv) < 2:
    print("Usage: python projections.py <column_name>")
    sys.exit(1)

projected_variable = sys.argv[1]

# Get WORLDPOP directory regardless of where script is run from
script_dir = os.path.dirname(os.path.abspath(__file__))
path = os.path.dirname(script_dir)

print("WORLDPOP path:", path)

def flatten(l):
    return [item for sublist in l for item in sublist]

# Find input files
files = glob.glob(os.path.join(path, "data", "worldpopstats_*.csv"))

print(f"Found {len(files)} files")

if len(files) == 0:
    raise FileNotFoundError(
        f"No files found matching {os.path.join(path, 'data', 'worldpopstats_*.csv')}"
    )

dfs = []

for file in files:
    print("Reading:", file)

    df = pd.read_csv(file)

    # Drop duplicate columns ending in _x
    df = df.drop(
        columns=[c for c in df.columns if c.endswith("_x")],
        errors="ignore"
    )

    year = int(os.path.basename(file).split("_")[-1].replace(".csv", ""))
    df["year"] = year

    dfs.append(df)

master_df = pd.concat(dfs, ignore_index=True)
master_df = master_df.sort_values("year").reset_index(drop=True)

print("Master dataframe shape:", master_df.shape)

if projected_variable not in master_df.columns:
    raise ValueError(
        f"Column '{projected_variable}' not found.\nAvailable columns:\n{master_df.columns.tolist()}"
    )

def extrapolate_variable(rc_data):

    rc_data = rc_data.dropna(subset=[projected_variable])

    if len(rc_data) < 2:
        return [np.nan] * 6

    years = rc_data["year"].values.reshape(-1, 1)
    values = rc_data[projected_variable].values.reshape(-1, 1)

    model = LinearRegression()
    model.fit(years, values)

    projection_years = np.array(
        [2021, 2022, 2023, 2024, 2025, 2026]
    ).reshape(-1, 1)

    projected_values = model.predict(projection_years)

    return projected_values.flatten().tolist()

extrapolated_data = master_df.groupby("object_id").apply(
    extrapolate_variable,
    include_groups=False
)

extrapolated_df = pd.DataFrame(
    extrapolated_data.tolist(),
    columns=["2021", "2022", "2023", "2024", "2025", "2026"]
)

extrapolated_df.index = extrapolated_data.index
extrapolated_df = extrapolated_df.reset_index()

extrapolated_df = pd.melt(
    extrapolated_df,
    id_vars=["object_id"],
    var_name="year",
    value_name=projected_variable
)

output_file = os.path.join(
    path,
    "data",
    f"{projected_variable}_projections.csv"
)

extrapolated_df.to_csv(output_file, index=False)

print("\nDone!")
print("Output:", output_file)
print("Shape:", extrapolated_df.shape)