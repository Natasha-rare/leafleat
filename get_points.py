import pandas as pd
from sklearn.cluster import KMeans
import geopandas as gpd
from shapely.geometry import Point

# Function to find evenly distributed cities in Russia
def find_evenly_distributed_cities(num_cities=200):
    # Load GeoNames dataset (you can download it from https://download.geonames.org/export/dump/RU.zip)
    geonames_filepath = "RU.txt"  # Replace with the actual path
    column_names = ["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", "feature class", "feature code", "country_code","cc2", "admin1_code", "admin2_code", "admin3_code", 
                    "admin4 code", "population", "elevation", "dem", "timezone", "modification date"]
    geonames = pd.read_csv(geonames_filepath, sep='\t', header=None, names=column_names)
    print(geonames)
    russian_cities = geonames[(geonames["country_code"] == "RU") & (geonames["admin1_code"].notnull())]

    # Create a GeoDataFrame
    geometry = [Point(lon, lat) for lon, lat in zip(russian_cities["longitude"], russian_cities["latitude"])]
    gdf = gpd.GeoDataFrame(russian_cities, geometry=geometry)
    print(gdf, russian_cities)
    # Perform k-means clustering
    kmeans = KMeans(n_clusters=num_cities, random_state=42)
    gdf["cluster"] = kmeans.fit_predict(gdf[["longitude", "latitude"]])

    # Select one city from each cluster (you can choose other criteria for selection)
    evenly_distributed_cities = gdf.groupby("cluster").apply(lambda x: x.iloc[0]).reset_index(drop=True)

    return evenly_distributed_cities[["name", "latitude", "longitude"]]

# Example usage
result = find_evenly_distributed_cities(num_cities=200)
print(result)
result[["name", "latitude", "longitude"]].to_csv('cities.csv', index=False)