import math
from flask import Flask, render_template, jsonify
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.flask_db
print(db)

APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')

# Load city data from CSV file
cities_data = pd.read_csv("cities.csv")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather_data")
def get_weather_data():
    # Check if data needs to be updated
    print(should_update_data(), 'shoould upfare')
    # return {'None':None}
    if should_update_data():
        for index, city in cities_data.iterrows():
            print(city, index)
            weather_data = fetch_weather_data(city["latitude"], city["longitude"])
            update_mongo_data(city["name"], weather_data)

    # Update last update date
    db.last_update.replace_one({}, {"date": datetime.today()}, upsert=True)

    # Retrieve data from MongoDB for all cities
    processed_data = process_weather_data_all()

    return jsonify(processed_data)

def should_update_data():
    # Check if data was updated yesterday
    # print(db.find())
    date_format = '%d/%m/%Y'

    # Parse the string into a datetime object
    last_update = db.weather.find_one()['weather_data']['Days'][0]['date']
    last_update = datetime.strptime(last_update, date_format)

    print(last_update, 'aaaaaaa', (datetime.now().date() - last_update.date()).days <=1)
    if last_update and (datetime.now().date() - last_update.date()).days <=1:
        return False
    return True

def fetch_weather_data(lat, lon):
    # Fetch weather data from the API
    WEATHER_API_ENDPOINT = f"http://api.weatherunlocked.com/api/forecast/{lat},{lon}?app_id={APP_ID}&app_key={APP_KEY}"

    response = requests.get(WEATHER_API_ENDPOINT)
    # response.raise_for_status()
    print(response.json())
    # print(response.json().d)
    return response.json()

def calculate_vpd(temperature_c, relative_humidity):
    e_sat = 6.112 * math.exp((17.67 * temperature_c) / (temperature_c + 243.5))
    e_act = (relative_humidity * e_sat) / 100.0
    vpd = e_sat - e_act
    return vpd


def calculate_aridity_index(precip_mm, temp_c=None):
    aridity_index = -10*precip_mm+1800
    return aridity_index

def update_mongo_data(city_name, weather_data):
    # Update or insert data into MongoDB for a specific city
    db.weather.replace_one({"city_name": city_name}, {"city_name": city_name, "weather_data": weather_data}, upsert=True)

def process_weather_data_all():
    # Process the raw weather data for all cities
    processed_data = []

    for index, city in cities_data.iterrows():
        print(city, city['name'], index, 'aaaa')
        city_data = db.weather.find_one({"city_name": city["name"]})
        print(city_data, 'cityyy_dataaa---------')
        if not city_data:
            continue
        date, precip_total_mm, temp_avg_c, humidity = city_data['weather_data']['Days'][0]['date'], \
                                                       city_data['weather_data']['Days'][0]['precip_total_mm'], \
                                                       (city_data['weather_data']['Days'][0]['temp_max_c'] +
                                                        city_data['weather_data']['Days'][0]['temp_min_c']) / 2, \
                                                       (city_data['weather_data']['Days'][0]['humid_max_pct'] +
                                                        city_data['weather_data']['Days'][0]['humid_min_pct']) / 2

        # Extract relevant information for each city
        map_data = {
            "lat": city["latitude"],
            "lon": city["longitude"],
            "precip_total_mm": precip_total_mm,
            "date": date,
            "temp": temp_avg_c,
            "humidity": humidity,
            "vdp": calculate_vpd(temp_avg_c, humidity),
            "aridity_index": calculate_aridity_index(precip_total_mm)
        }

        processed_data.append({"city_name": city["name"], "map_data": map_data})
    print('processed_data:', processed_data)
    return processed_data

if __name__ == "__main__":
    app.run(debug=True)
