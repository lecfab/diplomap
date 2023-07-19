"""Diplomap script to search for maps from various dates

This scripts will try to find the url of an official world-safety map for each
month of a given period. To search between years START and END, type:
$ diplomap-search.py [START [END]]

Found url will be stored as a list in images.json, and added to previous ones.
"""

import sys
from datetime import date
import re
import json
import requests
from requests.adapters import HTTPAdapter
s = requests.Session(); s.mount('https://', HTTPAdapter(max_retries=5))


def main():
    urls = list(get_monthly_images())
    current = get_current_image()
    if current is not None: urls.append(current)
    record_urls(urls)

def get_current_image():
    year = int(date.today().strftime("%Y"))
    url = get_minister_url(year)
    html = html_from_url(url)

    try:
        image_url = find_image(html)
    except Exception as err:
        print("Image error:", err)
        return None

    return image_url

def get_monthly_images():
    for year, month in get_period():
        try:
            text = find_archive(year, month)
        except Exception as err:
            print("Archive error:", err)
            continue

        try:
            image_url = find_image(text)
        except Exception as err:
            print("Image error:", err)
            continue

        yield image_url


def get_period():
    """Generate the list of months in the period defined by system parameters"""

    year_begin = int(sys.argv[1]) if len(sys.argv) > 1 else 2019
    year_end = int(sys.argv[2]) if len(sys.argv) > 2 else date.today().year
    for year in range(year_begin, year_end + 1):
        for month in range(1, 12 + 1):
            str_month = ("0"+str(month))[-2:]
            print(f"--------------- Month {year}-{month} ---------------")
            if str(year)+str_month > date.today().strftime("%Y%m"):
                print("This script is unable to foresee the future.")
                return
            yield year, str_month

def get_minister_url(year: int):
    """ Returns the apropriate url for a given year
    Args: year
    Returns: url of a diplomatie.gouv.fr page
    """
    core_url = "diplomatie.gouv.fr/fr/conseils-aux-voyageurs"
    if year < 2018: return f"http://{core_url}/conseils-par-pays"
    elif year < 2019: return f"https://www.{core_url}/conseils-par-pays-destination"
    else: return f"https://www.{core_url}"

def html_from_url(url: str):
    print(f"Request: {url}")
    r = requests.get(url, timeout=5)
    if not r.ok: raise Exception(r.status_code)
    return r.text

def find_archive(year: int, month: str):
    """Find an archived page for given date
    Args: year and month to search for in the web archive
    Returns: html content of an archived diplomatie.gouv.fr page
    """
    # chercher la page dans les archives autour de la date donnée
    archive = get_minister_url(year)
    archiver = f"https://web.archive.org/web/{year}{month}"
    request_link = f"{archiver}/{archive}"
    return html_from_url(request_link)

def find_image(text):
    """Find the url of the map in an html content
    Args: html content of a page from diplomatie.gouv.fr
    Returns: url corresponding to a world-safety map
    """

    # find url in html
    url = None
    for l in text.split("\n"):
        if re.search(r"local/cache-vignettes/L1280xH88[67]", l):
            url = re.sub(r'^.*href="([^"]*)".*$', r"https://www.diplomatie.gouv.fr/\1",  l)
    if url is None: raise Exception("No url found.")

    # check existence of the file
    print(f"Image: {url}")
    r_img = requests.get(url) # --user-agent="Mozilla"
    if not r_img.ok or r_img.headers["Content-Type"] != "image/jpeg":
        raise Exception(f"Image not found; try archive.")
    return url

def get_url_date(url):
    return re.sub(r'^.*/([0-9]{4})([0-9]{2})([0-9]{2})_.*$', r"\1-\2-\3",  url)

def record_urls(images):
    """Adds found urls to a json file
    Args: list of valid urls of world-safety maps
    """

    filename = "images.json"
    with open(filename, "r") as file_read:
        former_images = json.load(file_read)
    updated_images = set(former_images) | set(images)
    print(updated_images)

    print(f"Total images: {len(updated_images)} ({len(former_images)} existing, {len(images)} found)")
    with open(filename, "w") as file_write:
        json.dump(sorted(list(updated_images), key=get_url_date), file_write, indent=4)

if __name__ == "__main__":
    main()

# https://web.archive.org/web/20201023102258/https://www.diplomatie.gouv.fr/fr/conseils-aux-voyageurs
