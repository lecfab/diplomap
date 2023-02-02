"""Diplomap script to download all maps of a list

This script will take all the urls of the file images.json and download them
into the folder img/, replacing previous files. The name will follow the format
YYYY-MM-DD, given by a substring /YYYYMMDD_ in the initial url.
"""
import sys
import json
import re
import requests
from requests.adapters import HTTPAdapter
s = requests.Session(); s.mount('https://', HTTPAdapter(max_retries=5))

filename = "images.json"
foldername = "img/"

def get_images():
    with open(filename, "r") as file_read:
        images = json.load(file_read)
    return images

def get_url_date(url):
    return re.sub(r'^.*/([0-9]{4})([0-9]{2})([0-9]{2})_.*$', r"\1-\2-\3",  url)

def download_image(url):
    r_img = requests.get(url, timeout=10) # --user-agent="Mozilla"
    if not r_img.ok or r_img.headers["Content-Type"] != "image/jpeg":
        raise Exception(f"Image not found; try archive.")

    date = get_url_date(url)
    print(date)
    with open(f"img/{date}.jpg", 'wb') as f:
        f.write(r_img.content)

for url in get_images():
    try:
        download_image(url)
    except Exception as err:
        print(err, url)
