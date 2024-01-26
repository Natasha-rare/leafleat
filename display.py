import pandas as pd
from sklearn.cluster import KMeans
import geopandas as gpd
from shapely.geometry import Point
import plotly.express as px

csv_files = [ "full_cities.csv", "cities2.csv"]

# Read each CSV file into a pandas DataFrame and store them in a list
dfs = [pd.read_csv(file) for file in csv_files]

# # Concatenate the DataFrames along the rows axis
merged_df = pd.concat(dfs, ignore_index=True)

# Save the merged DataFrame to a new CSV file
merged_df.to_csv("full_cities.csv", index=False)

print("Merged CSV file saved successfully!")


result = pd.read_csv('full_cities.csv')
fig = px.scatter_mapbox(result, lon=result['longitude'], lat=result['latitude'], zoom=3, width=1200, height=900)
fig.update_layout(mapbox_style='open-street-map')
fig.show()

