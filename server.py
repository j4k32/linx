from flask import Flask, request, jsonify, current_app
from datetime import datetime, timezone, date
import requests
from math import ceil

import os

NASA_REMS_MSL_URL = "https://mars.nasa.gov/rss/api/?feed=weather&feedtype=json&ver=1.0&category=msl"
'''
This is acting like a cache, but normally 
redis or something similar would be preferable to use
than a dict. 
'''
sol_index = {}

'''
1. sol_index must me mutex. Can't be read from and updated simultaneously.
2. request should be async. Is currently blocking.
3. Should be called regulary once per sol.
4. For stability; would probably be better to save in db and load cache from there.
'''
def update_mars_data():
    global sol_index
    try:
        response = requests.get(NASA_REMS_MSL_URL)
        response.raise_for_status()
        weather_data = response.json()
        sol_index = {entry["sol"]: entry for entry in weather_data["soles"]}
    except Exception as e: 
        current_app.logger.warning(f"Error fetching NASA sol data: {e}")

def init_mars_data():
    update_mars_data()

def create_app():
    flask_app = Flask(__name__)
    flask_app.app_context().push()
    with flask_app.app_context():
        init_mars_data()
    return flask_app

app = create_app()

def convert_to_sol(requested_date: datetime.date):
    delta = requested_date - date(2012, 8, 6)
    return str(ceil(delta.days * 86400 / 88775.245))    

@app.route('/', methods=['GET'])
def get_mars_weather():
    try:
        date_str = request.args.get("date")
        req_date = datetime.fromisoformat(date_str).astimezone(timezone.utc).date()
    except:
        return jsonify({"error": "Incorrect date format"}), 400

    sol_date_str = convert_to_sol(req_date)
    mars_weather_info = sol_index.get(sol_date_str)
    if mars_weather_info:
        return jsonify({"sol_date": mars_weather_info}), 200
    else:
        return jsonify({"error": f"Requested date not found"}), 400


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))