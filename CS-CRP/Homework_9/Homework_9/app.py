import os
import time
import requests
from flask import Flask, send_from_directory, redirect, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# In-memory cache (remembers API answers for 5 minutes)
CACHE = {"data": None, "timestamp": 0}
CACHE_DURATION = 300  # seconds


@app.route("/")
def home():
    return send_from_directory(os.path.join(BASE_DIR, "home"), "index.html")


@app.route("/game")
def game_redirect():
    return redirect("/game/")


@app.route("/game/")
def game_index():
    return send_from_directory(os.path.join(BASE_DIR, "game"), "index.html")


@app.route("/game/<path:filename>")
def game_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, "game"), filename)


@app.route("/portfolio")
def portfolio_redirect():
    return redirect("/portfolio/")


@app.route("/portfolio/")
def portfolio_index():
    return send_from_directory(os.path.join(BASE_DIR, "portfolio"), "index.html")


@app.route("/portfolio/<path:filename>")
def portfolio_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, "portfolio"), filename)


@app.route("/api")
@app.route("/api/")
def api_page():
    return send_from_directory(os.path.join(BASE_DIR, "api"), "index.html")


@app.route("/api/pokemon")
def get_pokemon_data():
    now = time.time()
    if CACHE["data"] and (now - CACHE["timestamp"] < CACHE_DURATION):
        return jsonify({"source": "cache", "pokemon": CACHE["data"]})

    try:
        list_res = requests.get("https://pokeapi.co/api/v2/pokemon?limit=24", timeout=10)
        list_res.raise_for_status()
        results = list_res.json()["results"]

        cards = []
        for item in results:
            detail_res = requests.get(item["url"], timeout=10)
            detail_res.raise_for_status()
            d = detail_res.json()
            cards.append({
                "id": d["id"],
                "name": d["name"].capitalize(),
                "image": d["sprites"]["other"]["official-artwork"]["front_default"],
                "types": [t["type"]["name"] for t in d["types"]],
                "hp": d["stats"][0]["base_stat"],
                "attack": d["stats"][1]["base_stat"],
                "defense": d["stats"][2]["base_stat"],
                "height": d["height"] / 10,
                "weight": d["weight"] / 10,
            })

        CACHE["data"] = cards
        CACHE["timestamp"] = now
        return jsonify({"source": "live", "pokemon": cards})

    except Exception:
        return jsonify({
            "error": "Could not load live data from PokeAPI. Please check your connection and try again."
        }), 502


@app.errorhandler(404)
def page_not_found(e):
    return send_from_directory(BASE_DIR, "404.html"), 404



from pathlib import Path
from flask import Flask, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
# If you already have `app = Flask(...)`, keep your existing app instance and routes.

@app.route("/embedded")
@app.route("/embedded/")
def embedded_page():
    return send_from_directory(BASE_DIR / "embedded", "index.html")

@app.route("/embedded/<path:filename>")
def embedded_files(filename):
    return send_from_directory(BASE_DIR / "embedded", filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
