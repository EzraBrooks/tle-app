import json
import os

import requests
import tle2czml
from bs4 import BeautifulSoup
from pymongo import TEXT, MongoClient

mongo_uri = "mongodb://localhost:27017/orbits"
try:
    # This is what it's called by default on Heroku
    mongo_uri = os.environ["MONGODB_URI"]
except KeyError as e:
    pass
mongo_client = MongoClient(mongo_uri)
db = mongo_client.get_database()
czml_collection = db['czml']

# Scrape CelesTrak for NORAD TLEs
norad_page_text = requests.get(
    "https://celestrak.com/NORAD/elements/master.php").text
soup = BeautifulSoup(norad_page_text, features="html.parser")
txt_links = soup.select("a[href*=.txt]")
for link in txt_links:
    filename = link.get("href")
    tle_file = requests.get(
        "https://celestrak.com/NORAD/elements/" + filename).text
    parsed = json.loads(tle2czml.tles_to_czml(tle_file, silent=True))
    for entry in parsed:
        czml_collection.replace_one(
            {'id': entry['id']}, entry, upsert=True)

czml_collection.create_index([('id', TEXT)])
