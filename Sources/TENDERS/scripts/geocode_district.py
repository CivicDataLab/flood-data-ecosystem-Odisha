import pandas as pd
import geopandas as gpd
import re
import os
from difflib import SequenceMatcher

tenders_df = pd.read_csv(os.getcwd()+r'\flood-data-ecosystem-Odisha\Sources\TENDERS\data\flood_tenders_all.csv')

#HP_VILLAGES = gpd.read_file(os.getcwd()+'/Maps/assam_village_complete_with_revenueCircle_district_35_oct2022.geojson',
 #                              driver='GeoJSON')
OD_VILLAGES = pd.read_csv(os.getcwd()+r'\flood-data-ecosystem-Odisha\Maps\Geojson\ODISHA_VILLAGES_MASTER.csv', encoding='utf-8').dropna()

#Clean village names
od_villages = OD_VILLAGES["vilnam_soi"]
#hp_villages = hp_villages.to_frame()
village_duplicates_df = OD_VILLAGES[od_villages.isin(od_villages[od_villages.duplicated()])].sort_values("vilnam_soi")
#village_duplicates_df = HP_VILLAGES[HP_VILLAGES.isin(HP_VILLAGES[HP_VILLAGES.duplicated()])].sort_values(by="VILNAM_SOI")


'''
VILLAGE_CORRECTION_DICT = {
    "SOKARBILA(BOLGARBARI)(DARIAPAR" : "SOKARBILA(BOLGARBARI)(DARIAPAR)",
    "MANGALDAI EXTENDED TOWN (BHEBA" : "MANGALDAI EXTENDED TOWN (BHEBA)",
    "UPPER DIHING R.F. (SOUTH BLOCK" : "UPPER DIHING R.F. (SOUTH BLOCK)",
    "KACHARI MAITHCHAGAON NO.1(BAR" : "KACHARI MAITHCHAGAON NO.1(BAR)",
}


HP_VILLAGES.revenue_ci = HP_VILLAGES.revenue_ci.str.replace('\(Pt\)','')
HP_VILLAGES.revenue_ci = HP_VILLAGES.revenue_ci.str.replace('\(Pt-I\)','')
HP_VILLAGES.revenue_ci = HP_VILLAGES.revenue_ci.str.replace('\(Pt-II\)','')
HP_VILLAGES.revenue_ci = HP_VILLAGES.revenue_ci.str.replace('\n',' ')
HP_VILLAGES.revenue_ci = HP_VILLAGES.revenue_ci.str.strip()

HP_VILLAGES.sdtname_2 = HP_VILLAGES.sdtname_2.str.replace('\(Pt\)','')
HP_VILLAGES.sdtname_2 = HP_VILLAGES.sdtname_2.str.replace('\(Pt-I\)','')
HP_VILLAGES.sdtname_2 = HP_VILLAGES.sdtname_2.str.replace('\(Pt-II\)','')
'''
#tenders_df['location'] = tenders_df['location'].fillna(tenders_df['Location'])

# Dropping the original columns if you no longer need them
#tenders_df.drop(columns=['Location'], inplace=True)


locations = []
for idx, row in tenders_df.iterrows():
    LOCATION = row['location'].lower()
    LOCATION = LOCATION.replace('village','')
    LOCATION = LOCATION.replace('district','')
    LOCATION = LOCATION.replace('dist','')
    LOCATION = re.sub(r'[^a-zA-Z\n\.]', ' ', LOCATION)
    scores = []
    for subdistrict in OD_VILLAGES.sdtname.dropna().unique():
        score = SequenceMatcher(None, LOCATION, subdistrict.lower().strip()).ratio()
        scores.append(score)
    if max(scores)>0.8:
        locations.append(OD_VILLAGES.sdtname.dropna().unique()[scores.index(max(scores))])
    else:
        locations.append(row['location'])

tenders_df.Location = locations

blocks = OD_VILLAGES[["block_name",'dtname']].drop_duplicates().dropna()
#These revenue circles are across multiple districts
problematic_blocks = blocks[blocks.duplicated(['block_name'],keep=False)].sort_values('block_name')

# GEOCODE DISTRICTS

#MAKE A DICTIONARY OF ONLY NON-REPEATED REVENUE CIRCLES, SUB-DISTRICTS, BLOCKS and VILLAGES MAPPED TO THEIR DISTRICTS
#assam_revenue_circles_dict = HP_VILLAGES[['revenue_ci','district_2']].dropna().drop_duplicates().drop_duplicates(['revenue_ci'],keep=False).set_index('revenue_ci').to_dict(orient='index')
od_subdist_dict = OD_VILLAGES[['sdtname','dtname']].dropna().drop_duplicates().drop_duplicates(['sdtname'],keep=False).set_index('sdtname').to_dict(orient='index')
od_blocks_dict = OD_VILLAGES[['block_name','dtname']].dropna().drop_duplicates().drop_duplicates(['block_name'],keep=False).set_index('block_name').to_dict(orient='index')
OD_VILLAGES_dict = OD_VILLAGES[['vilnam_soi','dtname']].drop_duplicates(['vilnam_soi'],keep=False).set_index('vilnam_soi').to_dict(orient='index')


#MAKE LIST OF DISTRICTS, REVENUE CIRCLES, SUB-DISTRICTS, BLOCKS and VILLAGES WITH NON-REPEATING NAMES
problematic_blocksUPPERCASE = [] #Empty after forcefitted. #[rc.upper().strip() for rc in problematic_subdistricts.revenue_ci.unique()]
problematic_blkUPPERCASE = [block.upper().strip() for block in problematic_blocks.block_name.unique()]
od_villages = list(set(OD_VILLAGES_dict.keys())-set(problematic_blocksUPPERCASE)-set(problematic_blkUPPERCASE))
od_blocks = list(set(od_blocks_dict.keys())-set(problematic_blocksUPPERCASE)-set(problematic_blkUPPERCASE))
od_districts = list(set(OD_VILLAGES.dtname.dropna()))#-set(['KAMRUP','KAMRUP METRO']))

#assam_revenue_circles = list(set(assam_revenue_circles_dict.keys()))#-set(problematic_subdistricts.revenue_ci.unique())-set(problematic_sdts.sdtname_2.unique()))
od_sub_districts = list(set(od_subdist_dict.keys())-set(problematic_blocks.block_name.unique())-set(problematic_blocks.block_name.unique()))


# METHOD-2 WEIGHTAGE METHOD
# GET TENDER DISTRICT BASED ON externalReference COLUMN

tenders_df['tender_district_externalReference'] = None
for idx, row in tenders_df.iterrows():
    
    district_identifier = str(row['tender_externalreference']).split(r'/')[0].lower()
    if 'rgr' in district_identifier:
        district_identifier = district_identifier.split('rgr')[0].strip()[:-1]
    
    #if district_identifier in three_letter_distirct_identifiers_dict:
    #    tenders_df.loc[idx,'tender_district_externalReference'] = three_letter_distirct_identifiers_dict[district_identifier]
        
for idx, row in tenders_df.iterrows():
    if row['tender_externalreference'] != None:
        continue
    tender_slug = str(row['tender_externalreference'])
    tender_slug = re.sub(r'[^a-zA-Z0-9 \n\.]', ' ', tender_slug)
    for district in od_districts:
        if re.findall(r'\b%s\b'%district.lower().strip(), tender_slug.lower()):
            tenders_df.loc[idx,'tender_district_externalReference'] = district
            break
'''            
## REVENUE
for idx, row in tenders_df.iterrows():
    if row['tender_externalreference'] != None:
        continue
    
    tender_slug = str(row['tender_externalreference'])
    tender_slug = re.sub('[^a-zA-Z0-9 \n\.]', ' ', tender_slug)
    
    for revenue_circle in assam_revenue_circles:
        if re.findall(r'\b%s\b'%revenue_circle.lower().strip(), tender_slug.lower()):
            tenders_df.loc[idx,'tender_district_externalReference'] = assam_revenue_circles_dict[revenue_circle]['district_2']
            break '''

            
## SUB DISTRICT
for idx, row in tenders_df.iterrows():
    if row['tender_externalreference'] != None:
        continue
    
    tender_slug = str(row['tender_externalreference'])
    tender_slug = re.sub(r'[^a-zA-Z0-9 \n\.]', ' ', tender_slug)
    
    for sub_district in od_sub_districts:
        if re.findall(r'\b%s\b'%sub_district.lower(), tender_slug.lower()):
            tenders_df.loc[idx,'tender_district_externalReference'] = od_subdist_dict[sub_district]['dtname']
            break

# GET TENDER DISTRICT BASED ON TITLE AND WORK DESCRIPTION

tenders_df['tender_district_title_description'] = None
for idx, row in tenders_df.iterrows():
    tender_slug = str(row['tender_title']) + ' ' + str(row['Work Description'])
    tender_slug = re.sub(r'[^a-zA-Z0-9 \n\.]', ' ', tender_slug)
    for district in od_districts:
        if re.findall(r'\b%s\b'%district.lower().strip(), tender_slug.lower()):
            tenders_df.loc[idx,'tender_district_title_description'] = district
            break
           
## BLOCK
for idx, row in tenders_df.iterrows():
    if row['tender_district_title_description'] != None:
        continue
    
    tender_slug = str(row['tender_title']) + ' ' + str(row['Work Description'])
    tender_slug = re.sub('[^a-zA-Z0-9 \n\.]', ' ', tender_slug)
    
    for block in od_blocks:
        if re.findall(r'\b%s\b'%block.lower().strip(), tender_slug.lower()):
            print(block)
            tenders_df.loc[idx,'tender_district_title_description'] = od_blocks_dict[block]['dtname']
            break

            
## SUB DISTRICT
for idx, row in tenders_df.iterrows():
    if row['tender_district_title_description'] != None:
        continue
    
    tender_slug = str(row['tender_title']) + ' ' + str(row['Work Description'])
    tender_slug = re.sub(r'[^a-zA-Z0-9 \n\.]', ' ', tender_slug)
    
    for sub_district in od_sub_districts:
        if re.findall(r'\b%s\b'%sub_district.lower(), tender_slug.lower()):
            tenders_df.loc[idx,'tender_district_title_description'] = od_subdist_dict[sub_district]['dtname']
            break
# GET TENDER DISTRICT BASED ON LOCATION COLUMN
tenders_df['tender_district_location'] = None
for idx, row in tenders_df.iterrows():
    tender_slug = str(row['location']) 
    tender_slug = re.sub(r'[^a-zA-Z0-9 \n\.]', ' ', tender_slug)
    for district in od_districts:
        if re.findall(r'\b%s\b'%district.lower().strip(), tender_slug.lower()):
            tenders_df.loc[idx,'tender_district_location'] = district
            break
          
## BLOCK
for idx, row in tenders_df.iterrows():
    if row['tender_district_location'] != None:
        continue
    
    tender_slug = str(row['location'])
    tender_slug = re.sub('[^a-zA-Z0-9 \n\.]', ' ', tender_slug)
    
    for block in od_blocks:
        if re.findall(r'\b%s\b'%block.lower().strip(), tender_slug.lower()):
            tenders_df.loc[idx,'tender_district_location'] = od_blocks_dict[block]['dtname']
            break

            
## SUB DISTRICT
for idx, row in tenders_df.iterrows():
    if row['tender_district_location'] != None:
        continue
    
    tender_slug = str(row['location'])
    tender_slug = re.sub(r'[^a-zA-Z0-9 \n\.]', ' ', tender_slug)
    
    for sub_district in od_sub_districts:
        if re.findall(r'\b%s\b'%sub_district.lower(), tender_slug.lower()):
            tenders_df.loc[idx,'tender_district_location'] = od_subdist_dict[sub_district]['dtname']
            break
'''
# BTC FLAG
tenders_df['BTC_flag'] = None
for idx, row in tenders_df.iterrows():
    BTC_flag = False
    
    #tender_slug = str(row['Tender ID']) + ' ' + str(row['tender_title']) + ' ' + str(row['Work Description'] + ' ' + str(row['location']))
    #tender_slug = re.sub('[^a-zA-Z0-9 \n\.]', ' ', tender_slug)
    
    #skip Bodoland tenders
    department_slug = str(row["Organisation Chain"] + ' ' + row["Department"])
    department_slug = re.sub('[^a-zA-Z0-9 \n\.]', ' ', department_slug)
    if re.findall(r"bodoland", department_slug.lower()):
        BTC_flag= True
    
    bodoland_dept_slugs = ["BoTC", "BTC"]
    for slug in bodoland_dept_slugs:
        if slug in row["Tender ID"]:
            BTC_flag= True

    tenders_df.loc[idx,'BTC_flag'] = BTC_flag
'''
# WEIGHTAGE LOGIC
tenders_df['tender_district_externalReference'].fillna('NA',inplace=True) 
tenders_df['tender_district_title_description'].fillna('NA',inplace=True) 
tenders_df['tender_district_location'].fillna('NA',inplace=True) 

tenders_df['DISTRICT_FINALISED'] = ''

for idx, row in tenders_df.iterrows():
    district1 = row['tender_district_externalReference']
    district2 = row['tender_district_title_description']
    district3 = row['tender_district_location']
    districts = [district1,district2,district3]
    districts = set([x for x in districts if x!='NA'])

    if len(districts)==1:
        DISTRICT_SELECTED = list(districts)[0]
    elif len(districts)==0:
        DISTRICT_SELECTED = 'NA'
    else:
        DISTRICT_SELECTED = 'CONFLICT'
    
    tenders_df.loc[idx,'DISTRICT_FINALISED'] = DISTRICT_SELECTED

tenders_df.to_csv(os.getcwd()+'/flood-data-ecosystem-Odisha/Sources/TENDERS/data/floodtenders_districtgeotagged.csv',index=False)

print('Total number of flood related tenders: ', tenders_df.shape[0])
print('Number of tenders whose district could not be geo-tagged: ',tenders_df[tenders_df['DISTRICT_FINALISED']=='NA'].shape[0])
print('Number of tenders whose district identification is a CONFLICT: ',tenders_df[tenders_df['DISTRICT_FINALISED']=='CONFLICT'].shape[0])