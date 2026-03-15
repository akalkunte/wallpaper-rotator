#!/usr/bin/env python3
"""
Download Bing / Spotlight Wallpaper of the Day

This script downloads the last N Bing / spotlight wallpaper in 1920x1080 resolution to a local folder.
Calls an executable to set the downloaded image as wallpaper.

"""

import os
import glob
import sys
import subprocess
import requests
import json
import datetime
import winreg

# Disable SSL warnings for self-signed certificates (optional, for testing)
requests.packages.urllib3.disable_warnings()

# Folder to download the pictures to.
download_folder = os.path.expanduser(r"~\Pictures\Wallpapers")

# Create the folder if it is not already present.
os.makedirs(download_folder, exist_ok=True)

# Full path to executable to set wallpaper
setWPExe = r"SetWallpaper.exe"

# Extract a file name from the URL if unsuccessful then fall back to "spotlight"
def getFilenameFromURL(url):
  filename = f"spotlight_"
  # The above is the default.
  url = url.replace("_ds_","_") # Sometimes "_ds_" is present which can be removed so that we get a proper filename.

  # Try to get the string between the second and third underscore characters.
  try:
    index = url.index('_')
    subStr = url[(index+1):]
    index = subStr.index('_')
    subStr = subStr[(index+1):]
    index = subStr.index('_')
    # Check if result is too small
    if(len(subStr[:(index)]) < 4):
      subStr = subStr[(index+1):]
      index = subStr.index('_')
      subStr = subStr[:(index)]
    else:
      subStr = subStr[:(index)]

    filename = subStr

  except Exception as e:
    print(f"Error extracting filename from URL: {url} Exception: {e}")
    filename = f"spotlight_"

  return filename

def downloadImage():
    # Windows Spotlight wallpapers - Can change "bcnt" value to download more.
    spotlight_uri = "https://fd.api.iris.microsoft.com/v4/api/selection?&placement=88000820&bcnt=1&country=IN&locale=en-IN&fmt=json"
    filename = ""
    try:
        response = requests.get(spotlight_uri, verify=False)
        response.raise_for_status()
        data = response.json()
        # Assuming the JSON has batchrsp with items
        if 'batchrsp' in data and 'items' in data['batchrsp']:
            for i, item in enumerate(data['batchrsp']['items']):
                if 'item' in item:
                    try:
                        inner_data = json.loads(item['item'])
                        if 'ad' in inner_data and 'landscapeImage' in inner_data['ad'] and 'asset' in inner_data['ad']['landscapeImage']:
                            download_url = inner_data['ad']['landscapeImage']['asset']
                            # Get filename from URL
                            filename = getFilenameFromURL(download_url)
                            # Check if file with similar name exists.
                            if not glob.glob(os.path.join(download_folder, filename) + "*.*"):
                                # %f gives microseconds, we want milliseconds, so we take the first 3 digits of microseconds
                                timestamp = datetime.datetime.now().strftime('%d%b%Y_%H%M%S.%f')[:-3]  # Remove last 3 digits of microseconds for milliseconds
                                filename = os.path.join(download_folder, filename) + f"_{timestamp}.jpg"
                                print(f"Downloading {download_url} as {filename}")
                                img_response = requests.get(download_url, verify=False)
                                img_response.raise_for_status()
                                with open(filename, 'wb') as f:
                                    f.write(img_response.content)
                            else:
                                print(f"File {filename} already exists, skipping.")
                                return -9, filename # E_FILE_EXISTS

                    except json.JSONDecodeError:
                        print(f"Error parsing inner JSON for item {i+1}")
                        return -8, filename # E_JSON_PARSE_ERROR
        else:
            print("No 'batchrsp' or 'items' key in Spotlight JSON")
            return -7, filename # E_JSON_STRUCTURE_ERROR
    except requests.RequestException as e:
        print(f"Error fetching Spotlight data: {e}")
        return -6, filename # E_REQUEST_ERROR
    except json.JSONDecodeError as e:
        print(f"Error parsing Spotlight JSON: {e}")
        return -8, filename # E_JSON_PARSE_ERROR
    except Exception as e:
        print(f"An unexpected error occurred with Spotlight: {e}")
        return -5, filename # E_UNEXPECTED_ERROR
    return 0, filename # Success

def downloadAndSetWallpaper():
    # Get downloaded filename
    retCode = -1
    filename = ""
    retry = 5 # Retries to get a new image downloaded.
    while retry > 0 and retCode != 0:
        retCode, filename = downloadImage()
        if retCode == 0:
            print(f"Downloaded wallpaper successfully: {filename}")
        elif retCode == -9:
            print(f"Wallpaper already exists: {filename}")
            retry -= 1
        else:
            print(f"Error downloading wallpaper, code: {retCode}. Retrying... ({retry} attempts left)")
            retry -= 1
    if retCode != 0:
        print("Failed to download a new wallpaper after multiple attempts.")
        return
    # Call exe to set this image as wallpaper.
    try:
        result = subprocess.run([setWPExe, filename], capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        print(f"Exit Code: {result.returncode}")
        # Update registry with this info.
        myKey = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Wallpapers")
        winreg.SetValueEx(myKey, "CurrentWallpaperPath", 0, winreg.REG_SZ, filename)
        winreg.CloseKey(myKey)

    except Exception as e:
        print(f"Set wallpaper exception: {e}")
    return FileNotFoundError

if __name__ == "__main__":
    downloadAndSetWallpaper()

#import xml.etree.ElementTree as ET
# # Base BING URL
# bing_base = "https://www.bing.com"
# # Generic BING-wallpaper-of-the-day URL for past 3 days. en-IN = India!
# uri = f"{bing_base}/HPImageArchive.aspx?format=xml&idx=0&n=3&mkt=en-IN"
# # Desired resolution.
# resolution = "1920x1080"
# try:
#     # Fetch the XML data
#     response = requests.get(uri, verify=False)
#     response.raise_for_status()  # Raise an error for bad status codes
#
#     # Parse the XML
#     root = ET.fromstring(response.content)
#
#     # Process each image
#     for image in root.findall('image'):
#         # Get the urlBase
#         url_base_element = image.find('urlBase')
#         if url_base_element is not None:
#             url_base = url_base_element.text
#             # Generate the download URL
#             download_url = f"{bing_base}{url_base}_{resolution}.jpg"
#             # Split the urlBase to get the filename
#             filename = os.path.join(download_folder, url_base.split('=')[1] + ".jpg")
#             # Check if file already exists
#             if not os.path.exists(filename):
#                 print(f"Downloading {download_url} as {filename}")
#                 # Download the image
#                 img_response = requests.get(download_url, verify=False)
#                 img_response.raise_for_status()
#                 with open(filename, 'wb') as f:
#                     f.write(img_response.content)
#             else:
#                 print(f"File {filename} already exists, skipping.")
#         else:
#             print("urlBase not found in XML element")
#
# except requests.RequestException as e:
#     print(f"Error fetching data: {e}")
# except ET.ParseError as e:
#     print(f"Error parsing XML: {e}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")
