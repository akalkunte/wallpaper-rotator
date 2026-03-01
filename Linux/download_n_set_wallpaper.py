#!/usr/bin/env python3
"""
Download Spotlight Wallpaper and set that as desktop background
This script downloads Spotlight wallpapers into the users Pictures/Wallpapers folder
and attempts to set the newly downloaded image as the desktop background.
"""

import os
import requests
import xml.etree.ElementTree as ET
import json
import datetime
from gi.repository import Gio
#import subprocess

#-----------------------
# Disable SSL warnings for self-signed certificates (optional, for testing)
requests.packages.urllib3.disable_warnings()
# Folder to download the pictures to.
download_folder = os.path.expanduser("~/Pictures/Wallpapers")
# Create the folder if it is not already present.
os.makedirs(download_folder, exist_ok=True)
#-----------------------
# Try to get the short description from the image URL and use that as filename.
def getFilenameFromURL(url):
  # Generate filename with current datetime
  now = datetime.datetime.now()
  # %f gives microseconds, we want milliseconds, so we take the first 3 digits of microseconds
  timestamp = now.strftime('%d%b%Y_%H%M%S.%f')[:-3]  # Remove last 3 digits of microseconds for milliseconds
  filename = os.path.join(download_folder, f"spotlight_{timestamp}.jpg")
  # The above is the default.
  url = url.replace("_ds_","_") # Sometimes _ds_ is present which can be removed so that we get a proper filename.

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

    filename = os.path.join(download_folder, f"{subStr}_{timestamp}.jpg")

  except Exception as e:
    filename = os.path.join(download_folder, f"spotlight_{timestamp}.jpg")

  return filename
#-----------------------
def setWallpaper(fullPathToPic):
  schema = "org.gnome.desktop.background"
  key1 = "picture-uri-dark"
  key2 = "picture-uri"
  picFileUri = Gio.File.new_for_path(fullPathToPic).get_uri()
  gSettings = Gio.Settings.new(schema)
  gSettings.set_string(key1,picFileUri)
  gSettings.set_string(key2,picFileUri)
  # Can be achieved by executing in a shell like this also :)
  #subprocess.Popen(["gsettings","set","org.gnome.desktop.background","picture-uri-dark",f"file://{filename}"])
  #subprocess.Popen(["gsettings","set","org.gnome.desktop.background","picture-uri",f"file://{filename}"])
  return
#-----------------------
## Not using the BING images as the Spotlight ones are much better.
## Can download and set the BING wallpaper images as well.
#bing_base = "https://www.bing.com"
## Generic BING-wallpaper-of-the-day URL for past 3 days. en-IN = India!
#uri = f"{bing_base}/HPImageArchive.aspx?format=xml&idx=0&n=3&mkt=en-IN"
## Desired resolution.
#resolution = "1920x1080"
#try:
#    # Fetch the XML data
#    response = requests.get(uri, verify=False)
#    response.raise_for_status()  # Raise an error for bad status codes
#
#    # Parse the XML
#    root = ET.fromstring(response.content)
#
#    # Process each image
#    for image in root.findall('image'):
#        # Get the urlBase
#        url_base_element = image.find('urlBase')
#        if url_base_element is not None:
#            url_base = url_base_element.text
#            # Generate the download URL
#            download_url = f"{bing_base}{url_base}_{resolution}.jpg"
#            # Split the urlBase to get the filename
#            filename = os.path.join(download_folder, url_base.split('=')[1] + ".jpg")
#            # Check if file already exists
#            if not os.path.exists(filename):
#                # Download the image
#                print(f"Downloading {download_url} as {filename}")
#                img_response = requests.get(download_url, verify=False)
#                img_response.raise_for_status()
#                with open(filename, 'wb') as f:
#                    f.write(img_response.content)
#            else:
#                print(f"File {filename} already exists, skipping.")
#
#            setWallpaper(filename)
#        else:
#            print("urlBase not found in XML element")
#
#except requests.RequestException as e:
#    print(f"Error fetching data: {e}")
#except ET.ParseError as e:
#    print(f"Error parsing XML: {e}")
#except Exception as e:
#    print(f"An unexpected error occurred: {e}")

# Windows Spotlight wallpapers - Can change bcnt value to download more.
spotlight_uri = "https://fd.api.iris.microsoft.com/v4/api/selection?&placement=88000820&bcnt=1&country=IN&locale=en-IN&fmt=json"

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
                        if not os.path.exists(filename):
                            print(f"Downloading {download_url} as {filename}")
                            img_response = requests.get(download_url, verify=False)
                            img_response.raise_for_status()
                            with open(filename, 'wb') as f:
                                f.write(img_response.content)
                        else:
                            print(f"File {filename} already exists, skipping.")
                        # set the downloaded file as wallpaper for all themes.
                        setWallpaper(filename)
                except json.JSONDecodeError:
                    print(f"Error parsing inner JSON for item {i+1}")
    else:
        print("No 'batchrsp' or 'items' key in Spotlight JSON")
except requests.RequestException as e:
    print(f"Error fetching Spotlight data: {e}")
except json.JSONDecodeError as e:
    print(f"Error parsing Spotlight JSON: {e}")
except Exception as e:
    print(f"An unexpected error occurred with Spotlight: {e}")
