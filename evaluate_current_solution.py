import json
import geopandas as gpd
from shapely import Point
from utils import write_results, get_solution_coords, voronoi_division
from ga_functions import eval_fitness

valencia_region_polygon = gpd.read_file("./data/valencia_region.geojson").dissolve()[
    "geometry"
][0]

with open("./data/contenidors-oli-usat-contenedores-aceite-usado.json") as f:
    containers = json.load(f)


possible_locations = []
# For each container
for container in containers:
    # Get location
    location = [container["geo_point_2d"]["lon"], container["geo_point_2d"]["lat"]]

    # Check if locations is in valencia region
    if valencia_region_polygon.contains(Point(location)):
        # Then, append
        possible_locations.append(location)

solution = [1] * 352

fitness = eval_fitness(solution, possible_locations=possible_locations)[0]
solution_coords = get_solution_coords(solution, possible_locations=possible_locations)
voronoi_polygons = voronoi_division(solution_coords)
write_results("current", fitness, solution, voronoi_polygons)
