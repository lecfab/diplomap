# import requests module
import requests
from datetime import date
import re

images = []
# https://web.archive.org/web/20201023102258/https://www.diplomatie.gouv.fr/fr/conseils-aux-voyageurs
for year in range(2015, 2016 + 1):
    if year < 2018:
        archive = "http://diplomatie.gouv.fr/fr/conseils-aux-voyageurs/conseils-par-pays"
    elif year < 2019:
        archive = "https://www.diplomatie.gouv.fr/fr/conseils-aux-voyageurs/conseils-par-pays-destination"
    else:
        archive = "https://www.diplomatie.gouv.fr/fr/conseils-aux-voyageurs"

    for month in range(1, 12 + 1):
        month = ("0" if (month < 10) else "") + str(month)
        year = str(year)
        print(f"--------------- Month {year}-{month} ---------------")

        if year+month > date.today().strftime("%Y%m"):
            print("This script is unable to foresee the future.")
            break

        archiver = f"https://web.archive.org/web/{year}{month}"
        # html = conseils-$year-$month.html
        # txt = monde-$year-$month.txt
        # jpg = monde-$year-$month.jpg

        r = requests.get(f"{archiver}/{archive}")
        if not r.ok:
            print("Loading error: ", r.status_code)
            continue

        link = None
        for l in r.text.split("\n"):
            if re.search(r"local/cache-vignettes/L1280xH88[67]", l):
                link = re.sub(r'^.*href="([^"]*)".*$', r"https://www.diplomatie.gouv.fr/\1",  l)
                # print(l, link) #
        if link is None:
            print("No link found.")
            continue

        r_img = requests.get(link) # --user-agent="Mozilla"
        if r_img.ok and r_img.headers["Content-Type"] == "image/jpeg":
            # we obtained a valid image
            images.append(link)
            # print(f"Image found")
        else:
            print(f"Image not found; need to try archive: ", link)

print(images)
