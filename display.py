import pandas as pd
from sklearn.cluster import KMeans
import geopandas as gpd
from shapely.geometry import Point
import plotly.express as px

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
import pandas as pd

import pandas as pd

# Load geonames data
geonames_filepath = "RU.txt"  # Replace with the actual path
column_names = ["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", "feature class", "feature code", "country_code","cc2", "admin1_code", "admin2_code", "admin3_code", 
                    "admin4 code", "population", "elevation", "dem", "timezone", "modification date"]
geonames = pd.read_csv(geonames_filepath, sep='\t', header=None, names=column_names)
geonames = geonames.sort_values(by=['longitude', 'latitude'])

# Extract required columns
geonames = geonames[['name', 'alternatenames']]

# Load full_cities data
full_cities = pd.read_csv('full_cities.csv')

# Function to get alternate names
def get_alternate_names(city_name):
    try:
        alt_names = geonames.loc[geonames['name'] == city_name, 'alternatenames'].values
        # print(alt_names, city_name)
        return alt_names[0].split(',')[-1] if len(alt_names) > 0 else []
    except:
        return ''

# Apply the function to create the 'ru_translate' column
full_cities['ru_translate'] = full_cities['name'].apply(get_alternate_names)

print(full_cities)
