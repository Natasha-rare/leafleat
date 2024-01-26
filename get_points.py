import pandas as pd
from sklearn.cluster import KMeans
import geopandas as gpd
from shapely.geometry import Point
import plotly.express as px


def find_evenly_distributed_cities(num_cities=200):
    geonames_filepath = "RU.txt"  # Replace with the actual path
    column_names = ["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", "feature class", "feature code", "country_code","cc2", "admin1_code", "admin2_code", "admin3_code", 
                    "admin4 code", "population", "elevation", "dem", "timezone", "modification date"]
    geonames = pd.read_csv(geonames_filepath, sep='\t', header=None, names=column_names)
    geonames = geonames.sort_values(by=['longitude', 'latitude'])
    # print(geonames)
    # geonames = geonames[(27 <= geonames['longitude']) & (geonames['longitude'] <= 40) & (36 <= geonames['latitude']) & (geonames['latitude'] <= 61)][::100]
    # russian_cities = geonames[(geonames["country_code"] == "RU") & (geonames["admin1_code"].notnull())]

    # # Normalize coordinates
    # russian_cities["normalized_longitude"] = (russian_cities["longitude"] - russian_cities["longitude"].mean()) / russian_cities["longitude"].std()
    # russian_cities["normalized_latitude"] = (russian_cities["latitude"] - russian_cities["latitude"].mean()) / russian_cities["latitude"].std()

    # # Perform clustering
    # kmeans = KMeans(n_clusters=num_cities, random_state=42)
    # russian_cities["cluster"] = kmeans.fit_predict(russian_cities[["normalized_longitude", "normalized_latitude"]])

    # # Calculate adjusted centroids
    # centroids = russian_cities.groupby("cluster")[["normalized_longitude", "normalized_latitude"]].mean().reset_index()
    # centroids["longitude"] = centroids["normalized_longitude"] * russian_cities["longitude"].std() + russian_cities["longitude"].mean()
    # centroids["latitude"] = centroids["normalized_latitude"] * russian_cities["latitude"].std() + russian_cities["latitude"].mean()

    # # Reassign cities to the cluster with the closest adjusted centroid
    # russian_cities["centroid_distance"] = russian_cities.apply(lambda x: ((x["longitude"] - centroids.loc[x["cluster"], "longitude"])**2 + (x["latitude"] - centroids.loc[x["cluster"], "latitude"])**2)**0.5, axis=1)
    # russian_cities = russian_cities.sort_values("centroid_distance").groupby("cluster").head(1)

    return russian_cities[["name", "latitude", "longitude"]]

result = find_evenly_distributed_cities(num_cities=200)
print(result)
result[["name", "latitude", "longitude"]].to_csv('cities2.csv', index=False)


# result = find_evenly_distributed_cities(num_cities=200)
# print(result)
# result[["name", "latitude", "longitude"]].to_csv('cities.csv', index=False)
