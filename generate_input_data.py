import json
import geopandas as gpd
from shapely import Point
import math
from utils import remove_similar_locations

# Valencia region
valencia_region_polygon = gpd.read_file("./data/valencia_region.geojson").dissolve()[
    "geometry"
][0]

# Load solid containers data (to get a huge amount possible locations)
solid_containers = []
with open("./data/contenidors-residus-solids-contenidores-residuos-solidos.json") as f:
    solid_containers = json.load(f)

# Load oil containers data (to get current locations)
oil_containers = []
with open("./data/contenidors-oli-usat-contenedores-aceite-usado.json") as f:
    oil_containers = json.load(f)


# Fill possible locations
possible_locations = []

# For each container
for container in solid_containers:
    # Get location
    location = [container["geo_point_2d"]["lon"], container["geo_point_2d"]["lat"]]

    # Check if locations is in valencia region
    if valencia_region_polygon.contains(Point(location)):
        # Then, append
        possible_locations.append(location)

# Remove similar locations
possible_locations = remove_similar_locations(possible_locations)

with open("./data/possible_locations.json", "w") as f:
    # indent=2 is not needed but makes the file human-readable
    # if the data is nested
    json.dump(possible_locations, f)

# Calc individual size
individual_size = len(possible_locations)

print("Possible locations: ", individual_size)
print("Input data saved in ./data/possible_locations.json")
