import pandas as pd
import os
import re
import geopandas as gpd
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE       = os.getcwd()
VILLAGES_PATH = os.path.join(BASE, 'Maps', 'od_ids-drr_shapefiles', 'ODISHA_VILLAGES_MASTER.csv')
BLOCKS_PATH   = os.path.join(BASE, 'Maps', 'od_ids-drr_shapefiles', 'odisha_block_final.geojson')
INPUT_PATH    = os.path.join(BASE, 'Sources', 'TENDERS', 'data', 'floodtenders_districtgeotagged.csv')
OUTPUT_PATH   = os.path.join(BASE, 'Sources', 'TENDERS', 'data', 'floodtenders_blockgeotagged.csv')

# ── Load data ──────────────────────────────────────────────────────────────────
OD_VILLAGES = pd.read_csv(VILLAGES_PATH, encoding='utf-8').dropna()
OD_BLOCKS   = gpd.read_file(BLOCKS_PATH, driver='GeoJSON')
tenders_df  = pd.read_csv(INPUT_PATH, keep_default_na=False)

# Substrings to strip from location names before regex matching
REMOVE_SUBSTRINGS = ["(pt)", "\n"]
REMOVE_PATTERN    = "|".join(map(re.escape, REMOVE_SUBSTRINGS))

# Noise village names to always exclude
VILLAGE_NOISE = {'RIVER', 'NO', 'TOWN'}

# ── Main loop ──────────────────────────────────────────────────────────────────
MASTER_DFs = []

for FOCUS_DISTRICT in tqdm(OD_VILLAGES.dtname.unique()):

    # -- Build lookup dicts for this district ----------------------------------
    FOCUSDIST_village_dict = {}
    FOCUSDIST_block_dict   = {}
    FOCUSDIST_gp_dict      = {}
    FOCUSDIST_subdistrict_dict = {}

    for _, row in OD_VILLAGES[OD_VILLAGES.dtname == FOCUS_DISTRICT].iterrows():

        # Village dict
        vil = row["vilnam_soi"]
        if vil and vil not in VILLAGE_NOISE:
            vil_clean = re.sub(r'[^a-zA-Z]', "", str(vil))
            if vil_clean and vil_clean not in VILLAGE_NOISE:
                FOCUSDIST_village_dict[vil_clean] = {
                    "village_id": row["objectid"],
                    "block_name": row["block_name"],
                    "gp_name":    row["gp_name"],
                    "dtname":     row["dtname"],
                }

        # Block dict  — FIX: only written once, retains subdistrict
        FOCUSDIST_block_dict[row["block_name"]] = {
            "block":       row["block_name"],
            "subdistrict": row["sdtname"],
            "dtname":      row["dtname"],
        }

        # GP dict
        FOCUSDIST_gp_dict[row["gp_name"]] = {"dtname": row["dtname"]}

        # Subdistrict dict
        FOCUSDIST_subdistrict_dict[row["sdtname"]] = {"dtname": row["dtname"]}

    FOCUSDIST_villages    = list(FOCUSDIST_village_dict.keys())
    FOCUSDIST_blocks      = list(FOCUSDIST_block_dict.keys())
    FOCUSDIST_gp          = list(FOCUSDIST_gp_dict.keys())
    FOCUSDIST_subdistricts = list(FOCUSDIST_subdistrict_dict.keys())

    # -- Tag tenders for this district -----------------------------------------
    tenders_df_FOCUSDISTRICT = tenders_df[
        tenders_df["DISTRICT_FINALISED"] == FOCUS_DISTRICT
    ].copy()

    for idx, row in tenders_df_FOCUSDISTRICT.iterrows():

        # FIX: initialise ALL variables — including tender_block_location
        tender_villages        = []
        tender_village_id      = ""
        tender_block           = ""
        tender_gp              = ""
        tender_subdistrict     = ""
        tender_block_location  = ""   

        # Build the searchable slug
        tender_slug = (
            str(row['tender_externalreference']) + ' ' +
            str(row['tender_title'])             + ' ' +
            str(row['Work Description'])
        )
        tender_slug = re.sub(r'[^a-zA-Z0-9 \n\.]', ' ', tender_slug)

        # -- Village matching --
        for village in FOCUSDIST_villages:
            if not re.search(r'[a-zA-Z]', village):
                continue
            village = re.sub(r"[\[\]]?", "", village)
            village_search = re.sub(REMOVE_PATTERN, " ", village.lower())
            if re.findall(r'\b%s\b' % village_search.strip(), tender_slug.lower()):
                tender_villages.append(village)
                tender_village_id = FOCUSDIST_village_dict[village]['village_id']
                tender_block      = FOCUSDIST_village_dict[village]['block_name']

        # -- Block matching --
        for block in FOCUSDIST_blocks:
            block_search = re.sub(REMOVE_PATTERN, " ", block.lower())
            if re.findall(r'\b%s\b' % block_search.strip(), tender_slug.lower()):
                tender_block_location = block
                break

        # -- GP matching --
        for gp in FOCUSDIST_gp:
            gp_search = re.sub(REMOVE_PATTERN, " ", gp.lower())
            if re.findall(r'\b%s\b' % gp_search.strip(), tender_slug.lower()):
                tender_gp = gp
                break

        # -- Subdistrict matching --
        for subdistrict in FOCUSDIST_subdistricts:
            subdistrict_search = re.sub(REMOVE_PATTERN, " ", subdistrict.lower())
            if re.findall(r'\b%s\b' % subdistrict_search.strip(), tender_slug.lower()):
                tender_subdistrict = subdistrict
                break

        tenders_df_FOCUSDISTRICT.loc[idx, 'tender_villages']       = str(tender_villages)[1:-1]
        tenders_df_FOCUSDISTRICT.loc[idx, 'tender_block']          = tender_block
        tenders_df_FOCUSDISTRICT.loc[idx, 'tender_subdistrict']    = tender_subdistrict
        tenders_df_FOCUSDISTRICT.loc[idx, 'gp']                    = tender_gp
        tenders_df_FOCUSDISTRICT.loc[idx, 'tender_block_location'] = tender_block_location

    MASTER_DFs.append(tenders_df_FOCUSDISTRICT)

# Append unresolved rows
MASTER_DFs.append(tenders_df[tenders_df["DISTRICT_FINALISED"] == 'NA'])
MASTER_DFs.append(tenders_df[tenders_df["DISTRICT_FINALISED"] == 'CONFLICT'])

MASTER_DF = pd.concat(MASTER_DFs)

# ── BLOCK_FINALISED resolution ─────────────────────────────────────────────────
# FIX: clear priority logic instead of the original overwrite-then-check pattern
#   1. Direct block-name hit in slug  → tender_block_location
#   2. Village-derived block          → tender_block
#   3. Neither                        → ''
MASTER_DF['BLOCK_FINALISED'] = ''

for idx, row in MASTER_DF.iterrows():
    if row['tender_block_location']:
        MASTER_DF.loc[idx, 'BLOCK_FINALISED'] = row['tender_block_location']
    elif row['tender_block']:
        MASTER_DF.loc[idx, 'BLOCK_FINALISED'] = row['tender_block']
    # else stays ''

# ── Save ───────────────────────────────────────────────────────────────────────
MASTER_DF.to_csv(OUTPUT_PATH, index=False)
print(f"Done. {len(MASTER_DF)} rows saved to {OUTPUT_PATH}")
print(f"BLOCK_FINALISED fill rate: {(MASTER_DF['BLOCK_FINALISED'] != '').sum()} / {len(MASTER_DF)}")