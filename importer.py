#!/usr/bin/env python3
import os
from time import strptime

import requests
from bs4 import BeautifulSoup
from bson import json_util
from pymongo import TEXT, MongoClient
from tqdm import tqdm

import tle2czml


def parse_satcat_entry(satcat_entry: str):
    launch_date = None
    decay_date = None
    try:
        launch_date = strptime(satcat_entry[56:66].strip(), r'%Y-%m-%d')
        decay_date = strptime(satcat_entry[75:85].strip(), r'%Y-%m-%d')
    finally:
        return {
            'designator': satcat_entry[0:12].strip(),
            'noradCatalogNumber': satcat_entry[13:18].strip(),
            'hasMultipleNames': satcat_entry[19:20] == 'M',
            'isPayload': satcat_entry[20:21] == '*',
            'operationalStatusCode': satcat_entry[21:22],
            'names': satcat_entry[23:47].strip(),
            'sourceOrOwnership': satcat_entry[49:54].strip(),
            'launchDate': launch_date,
            'launchSite': satcat_entry[68:73].strip(),
            'decayDate': decay_date,
            'orbitalPeriod': satcat_entry[87:94].strip(),
            'inclination': satcat_entry[96:101].strip(),
            'apogeeAltitude': satcat_entry[103:109].strip(),
            'perigeeAltitude': satcat_entry[111:117].strip(),
            'radarCrossSection': satcat_entry[119:127].strip(),
            'orbitalStatusCode': satcat_entry[129:132].strip()
        }


def get_tles():
    return requests.get(
        'https://celestrak.com/NORAD/elements/active.txt').text


mongo_uri = "mongodb://localhost:27017/orbits"
try:
    # This is what it's called by default on Heroku
    mongo_uri = os.environ["MONGODB_URI"]
except KeyError as e:
    pass
mongo_client = MongoClient(mongo_uri)
db = mongo_client.get_database()
czml_collection = db['czml']
satellite_collection = db['satellites']
czml_collection.drop()
satellite_collection.drop()

# Retrieve CelesTrak's entire SATCAT (satellite catalog)
satcat_text: str = requests.get(
    "https://celestrak.com/pub/satcat.txt").text

print("Parsing SATCAT entries...")
satellites = [parse_satcat_entry(satellite)
              for satellite in tqdm(satcat_text.splitlines())]
print("Inserting SATCAT entries into database...")
satellite_collection.insert_many(satellites)

print("Retrieving TLEs...")
tles = get_tles()

print("Converting TLEs to CZML...")
czml_documents = [json_util.loads(tle2czml.tles_to_czml(
    tles, silent=True))]

print("Inserting CZML into MongoDB...")
for czml_document in czml_documents:
    czml_collection.insert_many(czml_document)

czml_collection.create_index([('id', TEXT)])
