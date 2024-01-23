# from geopy.geocoders import Nominatim
import math
import requests
import os
from dotenv import load_dotenv
load_dotenv()
# app = Nominatim(user_agent="app")
# location = app.geocode("Moscow, Russia").raw
latitude = 75.93821
longitude = 96.76972

# dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
APP_ID = os.getenv('APP_ID')
APP_KEY = os.getenv('APP_KEY')

def calculate_vpd(temperature_c, relative_humidity):
    e_sat = 6.112 * math.exp((17.67 * temperature_c) / (temperature_c + 243.5))
    e_act = (relative_humidity * e_sat) / 100.0
    vpd = e_sat - e_act
    return vpd

def forecast(lat, long):
    link = f"http://api.weatherunlocked.com/api/forecast/{lat},{long}?app_id={APP_ID}&app_key={APP_KEY}"
    response = requests.get(link)
    json_data = response.json()
    return json_data

def calculate_aridity_index(precip_mm, temp_c=None):
    aridity_index = -10*precip_mm+1800
    return aridity_index



data = forecast(latitude, longitude)
print(data)
date, precip_total_mm, temp_avg_c, humidity = data['Days'][0]['date'], data['Days'][0]['precip_total_mm'], \
    (data['Days'][0]['temp_max_c'] +data['Days'][0]['temp_min_c'])/2, (data['Days'][0]['humid_max_pct'] +data['Days'][0]['humid_min_pct'])/2

vpd_result = calculate_vpd(temp_avg_c, humidity)
print("Vapor Pressure Deficit:", vpd_result)

# precip_total_mm
aridity_index_result = calculate_aridity_index(temp_avg_c, precip_total_mm)
print("Aridity Index:", aridity_index_result)

