# IMD
Aggregate rainfall data from IMD (Indian Meteorological Department) for each sub-district in Odisha - on a monthly basis.

**Variables extracted from the source:** 
1. `max_rain`: Maximum rainfall value in the sub-district
2. `mean_rain`: Mean rainfall value in the sub-district
3. `sum_rain`: Sum rainfall value in the sub-district

## Project Structure

-   `scripts` : Contains the scripts used to obtain the data
    -   `main.py`: Downloads the RAINFALL data.
    -   `utils.py`: Removes unnecessary columns from data.
-   `data`: Contains datasets generated using the scripts
