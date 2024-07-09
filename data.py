import json
import pandas as pd
import geopandas as gpd
from shapely import Point

# Valencia region
valencia_region_polygon = gpd.read_file("./data/valencia_region.geojson").dissolve()[
    "geometry"
][0]

# Load oil containers data
oil_containers = []
with open("./data/contenidors-oli-usat-contenedores-aceite-usado.json") as f:
    oil_containers = json.load(f)


possible_locations = []

# For each container
for container in oil_containers:
    # Get location
    location = [container["geo_point_2d"]["lon"], container["geo_point_2d"]["lat"]]

    # Check if locations is in valencia region
    if valencia_region_polygon.contains(Point(location)):
        possible_locations.append(location)

# Calc individual size
individual_size = len(possible_locations)


def get_solution_coords(solution_vector):
    points = []
    for i, location in enumerate(possible_locations):
        if solution_vector[i] == 1:
            points.append(location)
    return points
