# Tenders
Public procurement datasets are scraped from the [Odisha Tenders](https://tendersodisha.gov.in/nicgep/app) website. Flood tenders are identified and geotagged with revenue circles using the names of villages, revenue circles etc., present in tender work descriptions, IDs etc.

**Variables extracted from the source:** Count and Sum of Tenders, with various sub types.
1. `total-tender-awarded-value`: Total value of flood related tenders
2. `sdrf-tenders-awarded-value`: This variable gives information of total value of tenders that were granted under State Disaster Response Fund
3. `RIDF-tenders-awarded-value`: RIDF is the Rural Infrastructure Development Fund maintained by NABARD. This variable gives information of total value of tenders that were granted under RIDF.
4. `restoration-measures-tenders-awarded-value`: This variable gives sum of all tenders that are flagged as Restoration Measures
5. `immediate-measures-tenders-awarded-value`: This variable gives sum of all tenders that are flagged as Immediate Measures
6. `Others-tenders-awarded-value`: Every flood related tender is flagged as either "Preparedness", "Immediate Measure" or "Other" based on key words. This column gives sum of all tenders that are flagged as Other

## Project Structure
- `scripts` : Contains the scripts used to obtain the data
    - `flood_tenders.py`: Identification of flood tenders
    - `geocode_district.py`: Python script to Geocode the tenders at the district-level using keyword matching
    - `geocode_blocks.py`: Python script to Geocode the tenders at the block level using keyword matching against Indian Village shapefile
- `data`: Contains datasets generated using the scripts
    - `monthly_tenders`: Contains all the AOC tenders scraped from the tender website, organized by month and concatenated into a single file per month.
    - `flood_tenders`: Contains a subset of the "monthly_tenders", that have been identified to be used for flood response using pattern matching algorithms
    - `variables`: Contains individual folders for each of the variables listed above. Each folder contains month-wise csv files with details of tenders received that correspond to each variable.
   