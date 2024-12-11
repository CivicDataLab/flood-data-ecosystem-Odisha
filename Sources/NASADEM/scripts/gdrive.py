import os

from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.oauth2 import service_account


cwd = os.getcwd()

service_account = "ids-drr@ids-drr.iam.gserviceaccount.com"  # Add service account.
# authenticate to Google Drive (of the Service account)
gauth = GoogleAuth()
scopes = ["https://www.googleapis.com/auth/drive"]
#gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(#service_account, 
#    f"{cwd}/Sources/NASADEM/ids-drr-74983d4a2634.json", scopes=scopes
#)
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(service_account, r'Sources\\NASADEM\\ids-drr-74983d4a2634.json', scopes=scopes)

drive = GoogleDrive(gauth)

# To get folder ID
# file_list = drive.ListFile().GetList()
# print(file_list)
# for file in file_list:
#     print(file["title"], file["id"])


# Define the folder and filenames
folder_name = 'NASADEM'
filenames = ['NASADEM_DEM_30.tif', 'NASADEM_SLOPE_30.tif']


# Download files from Google Drive to local system
for filename in filenames:
    file_list = drive.ListFile({'q': f"'{folder_name}' in parents and title='{filename}'"}).GetList()
    for file in file_list:
        file.GetContentFile(os.path.join(cwd, filename))
        print(f'Downloaded {filename} to {cwd}')

'''

NASADEM_folder_id = "1NfiKDY3JaOCrL2vRgZOojefhzwTLP8gW"

# get list of files
file_list = drive.ListFile(
    {"q": "'{}' in parents and trashed=false".format(NASADEM_folder_id)}
).GetList()
# print(file_list)

if file_list:
    for file in file_list:
        filename = file["title"]
        print(file["title"], file["mimeType"])

        # download file into working directory (in this case a tiff-file)
        file.GetContentFile(
            cwd + "/Sources/NASADEM/data/" + filename, mimetype=file["mimeType"]
        )

        # delete file afterwards to keep the Drive empty
        file.Delete()
else:
    print("No Files Found!!")
'''