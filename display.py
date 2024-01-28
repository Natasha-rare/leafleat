from datetime import datetime
import pandas as pd
from sklearn.cluster import KMeans
import geopandas as gpd
from shapely.geometry import Point
import plotly.express as px
from pymongo import MongoClient

# csv_files = [ "full_cities.csv", "cities2.csv"]

# # Read each CSV file into a pandas DataFrame and store them in a list
# dfs = [pd.read_csv(file) for file in csv_files]

# # # Concatenate the DataFrames along the rows axis
# merged_df = pd.concat(dfs, ignore_index=True)

# # Save the merged DataFrame to a new CSV file
# merged_df.to_csv("full_cities.csv", index=False)

# print("Merged CSV file saved successfully!")


# result = pd.read_csv('full_cities.csv')
# fig = px.scatter_mapbox(result, lon=result['longitude'], lat=result['latitude'], zoom=3, width=1200, height=900)
# fig.update_layout(mapbox_style='open-street-map')
# fig.show()

# data = pd.read_csv('full_cities.csv')
# print(data.shape, 'shape before drop')
# data.drop_duplicates(inplace=True)
# print(data.shape, 'shape after drop')
# data.to_csv("full_cities.csv", index=False)
# client = MongoClient('localhost', 27017)
# db = client.flask_db
# def get_city_data_by_day( day):
#     city_data = {}
#     cursor = db.weather.find({"Days.date": day})
#     print(cursor)
#     for document in cursor:
#         city = document['city']
#         city_data[city] = document
#     return city_data

# date_format = '%d/%m/%Y'
# # day = datetime.strptime('26/01/2024', date_format)
# cursor = db.weather.find({})
# for document in cursor:
#     print(document)
#     break
# # print(get_city_data_by_day('26/01/2024'))

from pymongo import MongoClient

# MongoDB connection parameters
db_uri = "mongodb://localhost:27017/"

# Connect to MongoDB
client = MongoClient(db_uri)
db = client.flask_db
collection = db.weather

# Update documents in the collection
cursor = collection.find({})

for document in cursor:
    print(document['city_name'], document['weather_data'])
    city_name = document['city_name']
    days = document['weather_data']['Days']
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
    # Update document in the collection
    collection.update_one(
        {'_id': document['_id']},
        {
            '$set': {
                'id': str(document['_id']),
                'city_name': city_name,
                'weather_data': new_weather_data
            }
        }
    )
    print('update sucessfull')
    print(document, 'update sucessfull')
    break

