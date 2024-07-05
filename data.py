import json
import pandas as pd
import geopandas as gpd
from shapely import (
    to_geojson,
    voronoi_polygons,
    Point,
    intersection,
    MultiPoint,
)

# Load fiware containers
fiware_containers = []
with open("./data/WasteContainers_FIWARE.json") as f:
    fiware_containers = json.load(f)

# Load containers out of FIWARE data platform
df_no_fiware_containers = pd.read_csv("./data/contenedores_aceite_sin_fiware.csv")

possible_locations = []

# Clean containers in FIWARE platform
for container in fiware_containers:
    # Filter oil containers
    if "aceiteContenedoresDipu2023" in container["id"]:

        # Check location
        if (container["location"] is not None) and (
            container["location"]["value"] is not None
        ):

            location = {}
            location["location"] = [container["location"]["value"]["coordinates"]]
            location["point"] = Point(container["location"]["value"]["coordinates"])

            possible_locations.append(location)

# Containers out of FIWARE platform
for index, row in df_no_fiware_containers.iterrows():
    location = {}
    location["location"] = [[row["geo_point_2d.lon"], row["geo_point_2d.lat"]]]
    location["point"] = Point([row["geo_point_2d.lon"], row["geo_point_2d.lat"]])
    possible_locations.append(location)

# Add id
for i, location in enumerate(possible_locations):
    location["id"] = i

# Valencia region
valencia_region_polygon = gpd.read_file("./data/valencia_region.geojson").dissolve()["geometry"][0]


def get_solution_coords(solution_vector):
    points = []
    for i, location in enumerate(possible_locations):
        if solution_vector[i] == 1:
            points.append(location["location"])
    return points
