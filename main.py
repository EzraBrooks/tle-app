import os

import requests
import tle2czml
from bs4 import BeautifulSoup
from bson import json_util
from flask import (Flask, Response, json, jsonify, render_template,
                   send_from_directory)
from pymongo import MongoClient

mongo_uri = "mongodb://localhost:27017"
try:
    # This is what it's called by default on Heroku
    mongo_uri = os.environ["MONGODB_URI"]
except KeyError as e:
    pass
mongo_client = MongoClient(mongo_uri)
orbits_db = mongo_client.get_database('orbits')
czml_collection = orbits_db.get_collection('czml')

app = Flask("tleapp")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cesium/<path:path>")
def send_cesium_files(path):
    return send_from_directory("node_modules/cesium/Build/Cesium", path)


@app.route("/orbit/<id>")
def get_orbit(id):
    return Response(json_util.dumps([
        czml_collection.find_one({'id': 'document'}),
        czml_collection.find_one(
            {'id': {'$regex': f'.*{id}.*', '$options': 'i'}})
    ]), status=200, content_type="application/json")


@app.route("/orbits")
def get_orbits():
    return Response(json_util.dumps(czml_collection.aggregate([
        {'$match': {
            'id': {'$regex': '^((?!deb)(?!r/b).)*$', '$options': 'i'}}},
        {'$limit': 100}
    ])), status=200, content_type="application/json")


if __name__ == "__main__":
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
    app.run()
