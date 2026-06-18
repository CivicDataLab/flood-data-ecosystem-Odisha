import pandas as pd
import os
import geopandas as gpd

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE      = os.getcwd()
DATA_PATH = os.path.join(BASE, 'Sources', 'TENDERS', 'data')
VARS_PATH = os.path.join(DATA_PATH, 'variables')
GEOJSON   = os.path.join(BASE, 'Maps', 'od_ids-drr_shapefiles', 'odisha_block_final.geojson')

# ── Load ───────────────────────────────────────────────────────────────────────
od_gdf = gpd.read_file(GEOJSON, driver='GeoJSON')

flood_tenders_df = pd.read_csv(
    os.path.join(DATA_PATH, 'floodtenders_blockgeotagged.csv'),
    keep_default_na=False
)

#merge 
flood_tenders_df['_dist_key']  = flood_tenders_df['DISTRICT_FINALISED'].str.upper().str.strip()
flood_tenders_df['_block_key'] = flood_tenders_df['BLOCK_FINALISED'].str.upper().str.strip()

od_gdf['_dist_key']  = od_gdf['dtname'].str.upper().str.strip()
od_gdf['_block_key'] = od_gdf['block_name'].str.upper().str.strip()

flood_tenders_df = flood_tenders_df.merge(
    od_gdf[['_dist_key', '_block_key', 'object_id']],
    on=['_dist_key', '_block_key'],
    how='left'
)

# Drop temp keys — originals are preserved
flood_tenders_df.drop(columns=['_dist_key', '_block_key'], inplace=True)

print("Total rows       :", len(flood_tenders_df))
print("Block-tagged rows:", flood_tenders_df['object_id'].notna().sum())
print("Untagged rows    :", flood_tenders_df['object_id'].isna().sum())

# ── Clean Awarded Value ────────────────────────────────────────────────────────
# Column is already named 'Awarded Value' coming out of the block geotagger
flood_tenders_df['Awarded Value'] = pd.to_numeric(
    flood_tenders_df['Awarded Value'].astype(str).str.replace(',', '', regex=False),
    errors='coerce'
)

# ── Only aggregate rows that have a valid block object_id ─────────────────────
tagged_df = flood_tenders_df[flood_tenders_df['object_id'].notna()].copy()

os.makedirs(VARS_PATH, exist_ok=True)


# ── Helper ─────────────────────────────────────────────────────────────────────
def save_variable(variable_df, col_name):
    """Group by month and write one CSV per month for a given variable."""
    var_dir = os.path.join(VARS_PATH, col_name)
    os.makedirs(var_dir, exist_ok=True)
    for year_month in variable_df['month'].unique():
        monthly = variable_df[variable_df['month'] == year_month][['object_id', col_name]]
        monthly.to_csv(
            os.path.join(var_dir, f'{col_name}_{year_month}.csv'),
            index=False
        )


# ── 1. Total tender awarded value ─────────────────────────────────────────────
col = 'total_tender_awarded_value'
agg = (
    tagged_df
    .groupby(['month', 'object_id'])[['Awarded Value']]
    .sum()
    .reset_index()
    .rename(columns={'Awarded Value': col})
)
save_variable(agg, col)
print(f"Saved: {col}")


# ── 2. Scheme-wise tender awarded value ───────────────────────────────────────
# FIX: filter out blank/NaN schemes; use separate loop var and col_name
schemes = [s for s in tagged_df['Scheme'].unique() if s and str(s).strip() not in ('', 'nan')]

for scheme in schemes:
    col_name = str(scheme).strip() + '_tenders_awarded_value'
    agg = (
        tagged_df[tagged_df['Scheme'] == scheme]
        .groupby(['month', 'object_id'])[['Awarded Value']]
        .sum()
        .reset_index()
        .rename(columns={'Awarded Value': col_name})
    )
    save_variable(agg, col_name)

print(f"Saved: {len(schemes)} scheme variables")


# ── 3. Response Type-wise tender awarded value ────────────────────────────────
# FIX: same pattern — filter blanks, separate col_name
response_types = [
    r for r in tagged_df['Response Type'].unique()
    if r and str(r).strip() not in ('', 'nan')
]

for response_type in response_types:
    col_name = str(response_type).strip() + '_tenders_awarded_value'
    agg = (
        tagged_df[tagged_df['Response Type'] == response_type]
        .groupby(['month', 'object_id'])[['Awarded Value']]
        .sum()
        .reset_index()
        .rename(columns={'Awarded Value': col_name})
    )
    save_variable(agg, col_name)

print(f"Saved: {len(response_types)} response type variables")
print(f"\nDone. All variables saved to {VARS_PATH}")