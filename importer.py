import json
import os

import requests
import tle2czml
from bs4 import BeautifulSoup
from pymongo import MongoClient

mongo_uri = "mongodb://localhost:27017"
try:
    # This is what it's called by default on Heroku
    mongo_uri = os.environ["MONGODB_URI"]
except KeyError as e:
    pass
mongo_client = MongoClient(mongo_uri)
db = mongo_client.get_default_database()
czml_collection = db['czml']

# Scrape CelesTrak for NORAD TLEs
norad_page_text = requests.get(
    "https://celestrak.com/NORAD/elements/master.php").text
soup = BeautifulSoup(norad_page_text)
txt_links = soup.select("a[href*=.txt]")
for link in txt_links:
    filename = link.get("href")
    tle_file = requests.get(
        "https://celestrak.com/NORAD/elements/" + filename).text
    with open(f"{filename}", "w") as temp_file:
        temp_file.write(tle_file)
    tle2czml.create_czml(filename, outputfile_path=f"{filename}.czml")
    with open(f"{filename}.czml", "r") as czml_file:
        parsed = json.loads(czml_file.read())
        for entry in parsed:
            czml_collection.replace_one(
                {'id': entry['id']}, entry, upsert=True)
