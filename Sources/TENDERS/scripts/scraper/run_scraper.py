import subprocess
import os
from datetime import date, timedelta

cwd = os.getcwd()
script_path = cwd+r'/IDS-DRR-Assam\Sources\TENDERS\scripts\scraper\scraper_assam_recent_tenders_tender_status.py'

for year in range(2023,2025):
    year = str(year)
    for month in range(7,9):        
        month=str(month)
        print(year+'_'+month)
        subprocess.call([r"C:\Users\saura\anaconda3\envs\cdl-env\python.exe", script_path, year, month])

