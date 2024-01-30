import math
from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pandas as pd
import time
import threading

load_dotenv()
app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.flask_db

APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')

cities_data = pd.read_csv("full_cities.csv")
last_updated = 2900

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather_data")
def get_weather_data():
    args = request.args
    date = args.get("date")
    # Check if data needs to be updated
    should_update = should_update_data()
    print(should_update, 'should update')
    # should_update = True
    # Fetch weather data in a separate thread if update is needed
    if should_update:
        threading.Thread(target=fetch_and_update_weather_data).start()

    # Retrieve and return processed data from MongoDB
    processed_data = process_weather_data_all(date)
    return jsonify(processed_data)

def fetch_and_update_weather_data():
    global last_updated
    shape = cities_data.shape[0]
    index = last_updated
    while index < shape:
        city = cities_data.iloc[index]
        try:
            weather_data = fetch_weather_data(city["latitude"], city["longitude"])
            update_mongo_data(city["name"], weather_data)
            # return
            if index % 100 == 0:
                print(index, 'updated in database: aaa')
            #     yield process_weather_data_all()
        except requests.exceptions.ConnectTimeout as e:
            last_updated = index
            print("Connection timed out. Retrying in 30 seconds...")
            time.sleep(30)
            index -= 1
        except Exception as e:
            last_updated = index
            print("Error occurred:", e)
            time.sleep(70)
            index -= 1
        index+=1
        last_updated = index
        print(last_updated)

    # Update last update date
    db.last_update.replace_one({}, {"date": datetime.today()}, upsert=True)
    last_updated = 0
    

def fetch_weather_data(lat, lon):
    WEATHER_API_ENDPOINT = f"http://api.weatherunlocked.com/api/forecast/{lat},{lon}?app_id={APP_ID}&app_key={APP_KEY}"
    response = requests.get(WEATHER_API_ENDPOINT, timeout=3)
    response.raise_for_status()  
    return response.json()

def should_update_data():
    
    last_update = db.last_update.find_one()
    print(last_update)
    if last_update:
        last_update_date = last_update.get('date')
        print(last_update_date, datetime.now(), (datetime.now() - last_update_date).days)
        if last_update_date and (datetime.now() - last_update_date).days < 1:
            return False
    return True

def calculate_vpd(temperature_c, relative_humidity):
    e_sat = 6.112 * math.exp((17.67 * temperature_c) / (temperature_c + 243.5))
    e_act = (relative_humidity * e_sat) / 100.0
    vpd = e_sat - e_act
    return vpd

def calculate_aridity_index(precip_mm, temp_c=None):
    aridity_index = -10*precip_mm + 1800
    return aridity_index

# def update_mongo_data(city_name, weather_data):
#     # Append new weather data to the historical data array
#     db.weather.update_one({"city_name": city_name}, {"$push": {"weather_data": weather_data}}, upsert=True)
# # from datetime import datetime
def update_weather_data(weather_data):
    days = weather_data['Days']
    new_weather_data = {}
    for day in days:
        date = day['date']
        new_weather_data[date] = {
            'sunrise_time': day['sunrise_time'],
            'sunset_time': day['sunset_time'],
            'moonrise_time': day['moonrise_time'],
            'moonset_time': day['moonset_time'],
            'temp_max_c': day['temp_max_c'],
            'temp_max_f': day['temp_max_f'],
            'temp_min_c': day['temp_min_c'],
            'temp_min_f': day['temp_min_f'],
            'precip_total_mm': day['precip_total_mm'],
            'precip_total_in': day['precip_total_in'],
            'rain_total_mm': day['rain_total_mm'],
            'rain_total_in': day['rain_total_in'],
            'snow_total_mm': day['snow_total_mm'],
            'snow_total_in': day['snow_total_in'],
            'prob_precip_pct': day['prob_precip_pct'],
            'humid_max_pct': day['humid_max_pct'],
            'humid_min_pct': day['humid_min_pct'],
            'windspd_max_mph': day['windspd_max_mph'],
            'windspd_max_kmh': day['windspd_max_kmh'],
            'windspd_max_kts': day['windspd_max_kts'],
            'windspd_max_ms': day['windspd_max_ms'],
            'windgst_max_mph': day['windgst_max_mph'],
            'windgst_max_kmh': day['windgst_max_kmh'],
            'windgst_max_kts': day['windgst_max_kts'],
            'windgst_max_ms': day['windgst_max_ms'],
            'slp_max_in': day['slp_max_in'],
            'slp_max_mb': day['slp_max_mb'],
            'slp_min_in': day['slp_min_in'],
            'slp_min_mb': day['slp_min_mb'],
        }
    return new_weather_data

def update_mongo_data(city_name, weather_data):
    today_date = datetime.now().date()
    date_format = '%d/%m/%Y'
    weather_info = update_weather_data(weather_data)
    # # for date, data in weather_info.items():
    # #     print(datetime.strptime(date, date_format).date() >= today_date, date, today_date)
    # # return
    # # Append new weather data to the historical data array
    # update_query = {
    #     "$push": {
    #         "weather_data": {
    #             f"{date}": data for date, data in weather_info.items() if datetime.strptime(date, date_format).date() >= today_date
    #         }
    #     }
    # }
    # db.weather.update_one({"city_name": city_name}, update_query, upsert=True)
    # filtered_weather_info = {
    #     date: data for date, data in weather_info.items()
    #     if datetime.strptime(date, date_format).date() >= today_date
    # }

    # Update the document only if there is data to update
        # Update query to set or update the weather_data object for each date
    update_queries = [
        {
            "$set": {
                f"weather_data.{date}": data
            }
        }
        for date, data in weather_info.items()
    ]
    # print(update_queries)
    # return
    # Update the document in the database for each date
    for query in update_queries:
        db.weather.update_one({"city_name": city_name}, query, upsert=True)
    print(city_name, 'in update')

def process_weather_data_all(date=None):
    processed_data = []
    date_format = '%Y-%m-%d'
    if not date:
        date = datetime.now().date.strftime('%d/%m/%Y')
    else:
        date = datetime.strptime(date, date_format).strftime('%d/%m/%Y')
    print(date)
    # return
    for index, city in cities_data.iterrows():
        city_data = db.weather.find_one({"city_name": city["name"]})
        if not city_data:
            continue
        weather_history = city_data.get("weather_data", {})
        # print('--', index)
        if weather_history:
            try:
                weather = weather_history[date]
            except Exception as e:
                print(f"Error processing data for {city['name']}: {e}")
                # print(weather_history.items())
                last_elem =  list(weather_history.keys())[0]
                weather = weather_history[last_elem]
            precip_total_mm = weather['precip_total_mm']
            temp_avg_c = (weather['temp_max_c'] + weather['temp_min_c']) / 2
            humidity = (weather['humid_max_pct'] + weather['humid_min_pct']) / 2
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
            processed_data.append({"city_name": city["name"], "map_data": map_data})
       
    return processed_data



if __name__ == "__main__":
    app.run(debug=True)
