import json
import os
from time import strptime

import requests
from bs4 import BeautifulSoup
from pymongo import TEXT, MongoClient

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

def get_tle(norad_catalog_number: str):
    tle_text = requests.get(
            'https://celestrak.com/satcat/tle.php?CATNR=' + satellite['noradCatalogNumber']).text
    soup = BeautifulSoup(tle_text, features='html.parser')
    tle_element = soup.select_one('pre')
    if tle_element is not None:
        return tle_element.string.strip()
    else:
        return None

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

# Retrieve CelesTrak's entire SATCAT (satellite catalog)
satcat_text: str = requests.get(
    "https://celestrak.com/pub/satcat.txt").text

satellites = [parse_satcat_entry(satellite) for satellite in satcat_text.splitlines()]
for satellite in satellites:
    satellite_collection.replace_one({'designator': satellite['designator']}, satellite, upsert=True)

# If this SATCAT entry is a mission payload and is operational or partially operational, go get its TLE.
operational_payloads = [satellite for satellite in satellites if satellite['isPayload'] and satellite['operationalStatusCode'] in ['+', 'P', 'B', 'S', 'X']]

tles = [get_tle(payload['noradCatalogNumber']) for payload in operational_payloads]

for tle in tles:
    if tle is not None:
        czml = json.loads(tle2czml.tles_to_czml(tle, silent=True))
        for entry in czml:
            czml_collection.replace_one(
                {'id': entry['id']}, entry, upsert=True)

czml_collection.create_index([('id', TEXT)])
