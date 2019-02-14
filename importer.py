import json
import os
from time import strptime

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
satellite_collection = db['satellites']

# Retrieve CelesTrak's entire SATCAT (satellite catalog)
satcat_text: str = requests.get(
    "https://celestrak.com/pub/satcat.txt").text
# print(satcat_text)
for satcat_entry in satcat_text.splitlines():
    designator = satcat_entry[0:12].strip()
    norad_catalog_number = satcat_entry[13:18].strip()
    has_multiple_names = satcat_entry[19:20] == 'M'
    is_payload = satcat_entry[20:21] == '*'
    operational_status_code = satcat_entry[21:22]
    names = satcat_entry[23:47].strip()
    source_or_ownership = satcat_entry[49:54].strip()
    launch_date = strptime(satcat_entry[56:66].strip(), r'%Y-%m-%d')
    launch_site = satcat_entry[68:73].strip()
    try:
        decay_date = strptime(satcat_entry[75:85].strip(), r'%Y-%m-%d')
    except ValueError as e:
        decay_date = None
    orbital_period = satcat_entry[87:94].strip()
    inclination = satcat_entry[96:101].strip()
    apogee_altitude = satcat_entry[103:109].strip()
    perigee_altitude = satcat_entry[111:117].strip()
    radar_cross_section = satcat_entry[119:127].strip()
    orbital_status_code = satcat_entry[129:132].strip()
    satellite_collection.replace_one({'designator': designator}, {
        'designator': designator,
        'noradCatalogNumber': norad_catalog_number,
        'hasMultipleNames': has_multiple_names,
        'isPayload': is_payload,
        'operationalStatusCode': operational_status_code,
        'names': names,
        'sourceOrOwnership': source_or_ownership,
        'launchDate': launch_date,
        'launchSite': launch_site,
        'orbitalPeriod': orbital_period,
        'inclination': inclination,
        'apogeeAltitude': apogee_altitude,
        'perigeeAltitude': perigee_altitude,
        'radarCrossSection': radar_cross_section,
        'orbitalStatusCode': orbital_status_code
    }, upsert=True)
    # If this SATCAT entry is a mission payload and is operational or partially operational, go get its TLE.
    if is_payload and (operational_status_code == '+' or operational_status_code == 'P' or operational_status_code == 'B' or operational_status_code == 'S' or operational_status_code == 'X'):
        tle = requests.get(
            'https://celestrak.com/satcat/tle.php?CATNR=' + norad_catalog_number).text
        soup = BeautifulSoup(tle, features='html.parser')
        tle = soup.select_one('pre').string.strip()
        czml = json.loads(tle2czml.tles_to_czml(tle, silent=True))
        for entry in czml:
            czml_collection.replace_one(
                {'id': entry['id']}, entry, upsert=True)

czml_collection.create_index([('id', TEXT)])
