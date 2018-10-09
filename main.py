import tle2czml
from flask import (Flask, json, jsonify, make_response, render_template,
                   send_from_directory)

app = Flask("tleapp")
app.debug = True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cesium/<path:path>")
def send_cesium_files(path):
    return send_from_directory("node_modules/cesium/Build/Cesium", path)


@app.route("/orbits")
def get_orbits():
    tle2czml.create_czml("tles.txt")
    with open("orbit.czml", "r") as f:
        return jsonify(json.loads(f.read()))


if __name__ == "__main__":
    app.run()
