import pandas as pd
import os
import re
import geopandas as gpd
from tqdm import tqdm 
import warnings
warnings.filterwarnings("ignore")

OD_VILLAGES = pd.read_csv(os.getcwd()+r'/flood-data-ecosystem-Odisha\Maps\Geojson\ODISHA_VILLAGES_MASTER.csv', encoding='utf-8').dropna()
OD_BLOCKS = gpd.read_file(os.getcwd()+r'\flood-data-ecosystem-Odisha\Maps\od_ids-drr_shapefiles\odisha_block_final.geojson', driver='GeoJSON')

#BLOCK_HQs = list(OD_BLOCKS[OD_BLOCKS.HQ=='y']['revenue_ci'])

tenders_df  = pd.read_csv(os.getcwd()+r'\flood-data-ecosystem-Odisha\Sources\TENDERS\data\floodtenders_districtgeotagged.csv', keep_default_na=False)

MASTER_DFs = []
for FOCUS_DISTRICT in tqdm(OD_VILLAGES.dtname.unique()):
    # Create dictionary for FOCUS DISTRICTS
    FOCUSDIST_village_dict = {}
    FOCUSDIST_subdistrict_dict = {}
    FOCUSDIST_block_dict = {}
    FOCUSDIST_gp_dict = {}
    FOCUSDIST_district_dict = {}
    
    for index,row in OD_VILLAGES[OD_VILLAGES.dtname==FOCUS_DISTRICT].iterrows():
        if row["vilnam_soi"]:
            row["vilnam_soi"] = re.sub(r'[^a-zA-Z]', "", row["vilnam_soi"])
            #if row["vilnam_soi"] in VILLAGE_CORRECTION_DICT:
            #    row["vilnam_soi"] = VILLAGE_CORRECTION_DICT[row["vilnam_soi"]]

            FOCUSDIST_village_dict[row["vilnam_soi"]] = {"village_id" : row["objectid"],
                                                     "block_name" : row["block_name"],
                                                     "block" : row["block_name"],
                                                     "gp_name": row["gp_name"],
                                                     "dtname" : row["dtname"]}

        FOCUSDIST_block_dict[row["block_name"]] = {"block" : row["block_name"],
                                               "subdistrict": row["sdtname"],
                                               #"gp_name" : row["gp_name"],
                                              "dtname" : row["dtname"]}

        FOCUSDIST_block_dict[row["block_name"]] = {"dtname" : row["dtname"]} 
        FOCUSDIST_gp_dict[row["gp_name"]] = {"dtname" : row["dtname"]} 
        FOCUSDIST_district_dict[row["dtname"]] = True
    
    try:
        del FOCUSDIST_village_dict['RIVER']
        del FOCUSDIST_village_dict['NO']
        del FOCUSDIST_village_dict['TOWN']
    except:
        pass
    
    FOCUSDIST_villages = list(FOCUSDIST_village_dict.keys())
    FOCUSDIST_blocks = list(FOCUSDIST_block_dict.keys())
    FOCUSDIST_subdistricts = list(FOCUSDIST_subdistrict_dict.keys())
    FOCUSDIST_gp = list(FOCUSDIST_gp_dict.keys())
    
    ## GEO-CODE VILLAGES, BLOCKS, REVENUE-CIRCLES
    tenders_df_FOCUSDISTRICT = tenders_df[tenders_df["DISTRICT_FINALISED"] == FOCUS_DISTRICT]
    for idx, row in tenders_df_FOCUSDISTRICT.iterrows():
        tender_villages = []
        tender_village_id = ""
        tender_block = ""
        tender_gp = ""
        tender_subdistrict = ""
        #tender_revenueci_location = ""

        tender_slug = str(row['tender_externalreference']) + ' ' + str(row['tender_title']) + ' ' + str(row['Work Description'])
        tender_slug = re.sub(r'[^a-zA-Z0-9 \n\.]', ' ', tender_slug)

        # List of substrings to remove from GPE names
        substrings_to_remove = ["(pt)", "\n"]
        # Construct the regex pattern by joining the substrings with "|"
        pattern = "|".join(map(re.escape, substrings_to_remove))

        for village in FOCUSDIST_villages:
            if not re.search(r'[a-zA-Z]', village):
                continue 
            village = re.sub(r"[\[\]]?", "", village)
            
            #if village in VILLAGE_CORRECTION_DICT:
            #    village = VILLAGE_CORRECTION_DICT[village]

            village_search = village.lower()
            village_search = re.sub(pattern, " ", village_search)

            if re.findall(r'\b%s\b'%village_search.strip(), tender_slug.lower()):
                tender_villages.append(village)
                tender_village_id = FOCUSDIST_village_dict[village]['village_id']
                tender_block = FOCUSDIST_village_dict[village]['block_name']
                #tender_revenueci = FOCUSDIST_village_dict[village]['revenuecircle']
                #tender_block = FOCUSDIST_village_dict[village]['block']
            
        
        for block in FOCUSDIST_blocks:
            block_search = block.lower()
            block_search = re.sub(pattern, " ", block_search)
            if re.findall(r'\b%s\b'%block_search.strip(), tender_slug.lower()):
                tender_block = block
                #tender_gp = FOCUSDIST_block_dict[block]['gp_name']
                #tender_subdistrict = FOCUSDIST_block_dict[block]['subdistrict']
                tender_block_location = block
                break

        for gp in FOCUSDIST_gp:
            gp_search = gp.lower()
            gp_search = re.sub(pattern, " ", gp_search)
            if re.findall(r'\b%s\b'%gp_search.strip(), tender_slug.lower()):
                tender_gp = gp
                break
        
        for subdistrict in FOCUSDIST_subdistricts:
            subdistrict_search = subdistrict.lower()
            subdistrict_search = re.sub(pattern, " ", subdistrict_search)
            if re.findall(r'\b%s\b'%subdistrict_search.strip(), tender_slug.lower()):
                tender_subdistrict = subdistrict
                break


        tenders_df_FOCUSDISTRICT.loc[idx,'tender_villages'] = str(tender_villages)[1:-1]
        tenders_df_FOCUSDISTRICT.loc[idx,'tender_block'] = tender_block
        tenders_df_FOCUSDISTRICT.loc[idx,'tender_subdistrict'] = tender_subdistrict
        tenders_df_FOCUSDISTRICT.loc[idx,'gp'] = tender_gp
        tenders_df_FOCUSDISTRICT.loc[idx,'tender_block_location'] = tender_block_location
        
    MASTER_DFs.append(tenders_df_FOCUSDISTRICT)  


MASTER_DFs.append(tenders_df[tenders_df["DISTRICT_FINALISED"] == 'NA'])
MASTER_DFs.append(tenders_df[tenders_df["DISTRICT_FINALISED"] == 'CONFLICT'])

MASTER_DF = pd.concat(MASTER_DFs)

#HQ Flag and RC Finalisation
#MASTER_DF['HQ_flag'] = False
MASTER_DF['BLOCK_FINALISED'] = ''
for idx, row in MASTER_DF.iterrows():
    #if row['tender_revenueci_location'] in RC_HQs:
    #    MASTER_DF.loc[idx, 'HQ_flag'] = True
    
    #if row['HQ_flag'] == False:
    MASTER_DF.loc[idx, 'BLOCK_FINALISED'] = row['tender_block_location']

    if row['tender_block_location'] == '':
        MASTER_DF.loc[idx, 'BLOCK_FINALISED'] = row['tender_block']
    
    if row['tender_block_location'] == row['tender_block']:
        MASTER_DF.loc[idx, 'BLOCK_FINALISED'] = row['tender_block']

    # If HQ True AND row['tender_revenueci_location'] != row['tender_revenueci']?
MASTER_DF.to_csv(os.getcwd()+r'/flood-data-ecosystem-Odisha\/Sources/TENDERS/data/floodtenders_blockgeotagged.csv')
