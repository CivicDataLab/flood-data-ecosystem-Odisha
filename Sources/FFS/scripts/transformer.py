import os

import geopandas as gpd
import pandas as pd

path = os.getcwd()

ffs_df = pd.read_csv(path + "/Sources/FFS/data/scraped_data.csv")
ffs_df["year_month"] = ffs_df.Date.str[:4] + "_" + ffs_df.Date.str[5:7]

stations_file = gpd.read_file(path + "/Sources/FFS/data/state_stations.geojson")
state_shpfile = gpd.read_file(path + "/Maps/subdistrict/subdistricts_479_osm.shp")

result = gpd.sjoin(
    stations_file[["stationCode", "geometry"]],
    state_shpfile[["name", "geometry"]],
)

# DAILY RIVER LEVELS
grouped_df = ffs_df.groupby(["stationCode", "Date"]).agg(
    {"dataValue": ["mean", "min", "max"]}
)
grouped_df = grouped_df.reset_index()
grouped_df.columns = [
    "stationCode",
    "Date",
    "riverlevel_mean",
    "riverlevel_min",
    "riverlevel_max",
]
grouped_df = grouped_df.merge(result[["stationCode", "name"]], on="stationCode")
grouped_df.to_csv(
    path + "/Sources/FFS/data/variables/riverlevel_daily.csv", index=False
)

# MONTHLY RIVER LEVELS - MASTER
grouped_df = ffs_df.merge(result[["stationCode", "name"]], on="stationCode")
grouped_df = grouped_df.groupby(["name", "year_month"]).agg(
    {"dataValue": ["mean", "min", "max"]}
)
grouped_df = grouped_df.reset_index()
grouped_df.columns = [
    "name",
    "timeperiod",
    "riverlevel_mean",
    "riverlevel_min",
    "riverlevel_max",
]
grouped_df.to_csv(path + "/Sources/FFS/data/variables/riverlevel.csv", index=False)
