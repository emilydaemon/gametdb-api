from flask import Flask
from pathlib import Path
import requests

app = Flask(__name__)

regions = ["US", "JA", "EN", "FR", "DE", "ES", "IT", "NL", "PT", "CH", "AU", "SE", "DK", "NO", "FI", "TR", "KO", "ZH", "RU", "MX", "CA"]

headers = {"User-Agent": "Unofficial GameTDB API/0.1dev (Contact: https://donut.eu.org/contact)"}

# Terutns a dict.
def parse_tdb(tdb):
    tdb = tdb.rstrip()
    tdb = dict(item.split(" = ") for item in tdb.split("\n"))
    return tdb

def region_covers_urls(console, game_id):
    output = {}
    for region in regions:
        for fext in ["png", "jpg"]:
            url = f"https://art.gametdb.com/{console}/cover/{region}/{game_id}.{fext}"
            res = requests.head(url, headers=headers)
            output[region] = url
    return output;

def main_covers_urls(console, game_id):
    output = {}
    many_fexts = False # many file extensions? TODO: ACTUALLY do something with this
    # TODO: ps2, 3ds, wiiu
    if console == "switch":
        cover_type = "coverHQ"
        cover_types = ["box", "coverM", "coverfullHQ", "backHQ", "coverfullHQ2", "label", "cart"]
        many_fexts = True
    elif console == "wii":
        cover_type = "cover"
        cover_types = ["cover3D", "coverfullHQ", "coverB", "cover3DB", "coverB2", "cover3DB2", "disc", "disccustom"]
    elif console == "dsi":
        cover_type = "coverHQ"
        cover_types = ["box", "backHQ", "coverDS", "coverS", "coverM", "backM", "backHQ", "coverHQB", "boxB"]
        many_fexts = True
    for region in regions:
        for fext in ["png", "jpg"]:
            url = f"https://art.gametdb.com/{console}/{cover_type}/{region}/{game_id}.{fext}"
            res = requests.head(url, headers=headers)
            print(f"{url}, {res.status_code}")
            if res.status_code == 200:
                output["2d"] = url
                break
    for i in cover_types:
        for fext in ["png", "jpg"]:
            url = f"https://art.gametdb.com/{console}/{i}/{region}/{game_id}.{fext}"
            res = requests.head(url, headers=headers)
            print(f"{url}, {res.status_code}")
            if res.status_code == 200:
                output[i] = url
    print(output)
    return output

@app.route("/")
def homepage():
    output = ""
    output += "<h1>This is a gametdb-api instance</h1>"
    output += "<p>For documentation, see <a href='#'>this page.</a></p>"
    return output

# Get game title from ID
@app.route("/api/v1/<console>/title/<game_id>")
def title_api(console, game_id):
    if console not in tdbs:
        return { "error": "Console not found" }, 404
    if game_id in tdbs[console]:
        return { "title": tdbs[console][game_id], }
    else:
        return { "error": "Title not found" }, 404

"""
# Get game ID from title
@app.route("/api/v1/<console>/id/<title>")
def id_api(console, game_id):
    if console not in tdbs:
        return { "error": "Console not found" }, 404
    for k, v in tdbs[console].items():
    else:
        return { "error": "Title not found" }, 404
"""

# Get game cover arts
@app.route("/api/v1/<console>/covers/<game_id>")
def covers_api(console, game_id):
    if console not in tdbs:
        return { "error": "Console not found" }, 404
    if game_id not in tdbs[console]:
        return { "error": "Title not found" }, 404
    return main_covers_urls(console, game_id)

@app.route("/api/v1/<console>/region_covers/<game_id>")
def region_covers_api(console, game_id):
    if console not in tdbs:
        return { "error": "Console not found" }, 404
    if game_id not in tdbs[console]:
        return { "error": "Title not found" }, 404
    return region_covers_urls(console, game_id)

# This _might_ be an easter egg. :^)
@app.route("/api/v1/fuck-status")
def fucks_given_api():
    return { "fucks-given": 0, }

with app.app_context():
    tdbs = {}
    for f in Path("tdb").glob("*tdb.txt"):
        name = f.name[:-len("tdb.txt")]
        tdbs[name] = f.read_text("utf-8")
        tdbs[name] = parse_tdb(tdbs[name])
        print(f"Loaded '{name}' ({f.name}) title database.")
