import math
from flask import Flask, render_template, jsonify
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pandas as pd
import time
import threading
from deep_translator import GoogleTranslator
load_dotenv()
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.flask_db

APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')

cities_data = pd.read_csv("full_cities.csv")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather_data")
def get_weather_data():
    # Check if data needs to be updated
    should_update = should_update_data()
    print(should_update, 'should update')
    # should_update = True
    # Fetch weather data in a separate thread if update is needed
    if should_update:
        threading.Thread(target=fetch_and_update_weather_data).start()

    # Retrieve and return processed data from MongoDB
    processed_data = process_weather_data_all()
    return jsonify(processed_data)

def fetch_and_update_weather_data():
    for index, city in cities_data.iterrows():
        try:
            weather_data = fetch_weather_data(city["latitude"], city["longitude"])
            update_mongo_data(city["name"], weather_data)
        except requests.exceptions.ConnectTimeout as e:
            print("Connection timed out. Retrying in 30 seconds...")
            time.sleep(30)
            continue
        except Exception as e:
            print("Error occurred:", e)
            time.sleep(90)
            continue

    # Update last update date
    db.last_update.replace_one({}, {"date": datetime.today()}, upsert=True)

def fetch_weather_data(lat, lon):
    WEATHER_API_ENDPOINT = f"http://api.weatherunlocked.com/api/forecast/{lat},{lon}?app_id={APP_ID}&app_key={APP_KEY}"
    response = requests.get(WEATHER_API_ENDPOINT, timeout=3)
    response.raise_for_status()  
    return response.json()

def should_update_data():
    date_format = '%d/%m/%Y'
    last_update = db.weather.find_one({'weather_data.Days.0.date': {"$exists": True}})
    if last_update:
        last_update = datetime.strptime(last_update['weather_data']['Days'][0]['date'], date_format)
        if (datetime.now().date() - last_update.date()).days <= 1:
            return False
    return True

def calculate_vpd(temperature_c, relative_humidity):
    e_sat = 6.112 * math.exp((17.67 * temperature_c) / (temperature_c + 243.5))
    e_act = (relative_humidity * e_sat) / 100.0
    vpd = e_sat - e_act
    return vpd

def calculate_aridity_index(precip_mm, temp_c=None):
    aridity_index = -10*precip_mm+1800
    return aridity_index

def update_mongo_data(city_name, weather_data):
    db.weather.replace_one({"city_name": city_name}, {"city_name": city_name, "weather_data": weather_data}, upsert=True)

def process_weather_data_all():
    processed_data = []
    for index, city in cities_data.iterrows():
        city_data = db.weather.find_one({"city_name": city["name"]})
        if not city_data:
            continue
        date = city_data['weather_data']['Days'][0]['date']
        precip_total_mm = city_data['weather_data']['Days'][0]['precip_total_mm']
        temp_avg_c = (city_data['weather_data']['Days'][0]['temp_max_c'] + city_data['weather_data']['Days'][0]['temp_min_c']) / 2
        humidity = (city_data['weather_data']['Days'][0]['humid_max_pct'] + city_data['weather_data']['Days'][0]['humid_min_pct']) / 2

        map_data = {
            "lat": city["latitude"],
            "lon": city["longitude"],
            "precip_total_mm": precip_total_mm,
            "date": date,
            "temp": temp_avg_c,
            "humidity": humidity,
            "vpd": calculate_vpd(temp_avg_c, humidity),
            "aridity_index": calculate_aridity_index(precip_total_mm)
        }
        # city_name =  GoogleTranslator(source='auto', target='ru').translate(city["name"])
        # print(city_name)
        processed_data.append({"city_name":city["name"], "map_data": map_data})
    return processed_data

if __name__ == "__main__":
    app.run(debug=True)