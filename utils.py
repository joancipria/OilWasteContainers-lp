import json
import rasterio
from rasterio.mask import mask
from shapely.geometry import Point, LineString, Polygon
from shapely import to_geojson
from pyproj import Geod
import requests

geod = Geod(ellps="WGS84")

# Load population raster
pop_raster = rasterio.open("./data/spain_pop.tif")


def get_population_from_polygon(polygon):
    """
    Returns number of people in a polygon

    :param json polygon: Polygon in geoJSON format.
    """
    # Mask raster by the polygon and crop it
    try:
        polygon = json.loads(polygon)
        out_image, out_transform = mask(pop_raster, [polygon], crop=True)

        # Clean negative values
        out_image = out_image[out_image >= 0]

        # Get total population
        total_pop = int(out_image.sum())

        return total_pop
    except ValueError as error:
        return {"error": error}


def get_distance_between_points(point_a, point_b):
    """
    Returns distance (m) between point_a and point_b.

    :param list point_a: Point A in [lon, lat] format
    """
    try:
        line_string = LineString([Point(point_a), Point(point_b)])
        distance = geod.geometry_length(line_string)
        return distance
    except ValueError as error:
        return {"error": error}


def remove_similar_locations(locations, threshold=10):
    """
    Remove locations that are within a given distance threshold (in meters).

    :param list locations: Locations in [lon, lat] format
    :param int threshold: Distance threshold in meters
    """
    unique_locations = []

    for loc in locations:
        if all(
            get_distance_between_points(loc, unique_loc) > threshold
            for unique_loc in unique_locations
        ):
            unique_locations.append(loc)

    return unique_locations


def get_solution_coords(solution_vector, possible_locations):
    """
    Converts solution representation into a list of [long,lat] locations
    """
    points = []
    for i, location in enumerate(possible_locations):
        if solution_vector[i] == 1:
            points.append(location)
    return points


def get_isochrone(location, minutes):
    """
    Returns isochrone polygon given a location and minutes
    """
    try:
        # Calc isochrones
        isochrone_range = [minutes * 60]

        headers = {
            "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
            "Authorization": "5b3ce3597851110001cf62487c1cebfad2324c61823ac5e4fe9be9b1",  # Private
            "Content-Type": "application/json; charset=utf-8",
        }

        body = {"locations": [location], "range": isochrone_range}
        call = requests.post(
            " http://localhost:8080/ors/v2/isochrones/foot-walking",
            json=body,
            headers=headers,
        )
        result = call.json()

        return Polygon(result["features"][0]["geometry"]["coordinates"][0])
    except ValueError as error:
        return {"error": error}


def generate_isochrones(possible_locations, isochrone_range):
    """
    For each possible location, create an isochrone and get pop
    """
    points_and_pop = []
    for i, location in enumerate(possible_locations):
        isochrone = get_isochrone(location, isochrone_range)
        population = get_population_from_polygon(to_geojson(isochrone))
        points_and_pop.append(
            {"index": i, "population": population, "isochrone": isochrone}
        )

    # Sort by ascending population
    points_and_pop = sorted(
        points_and_pop, key=lambda point: point["population"], reverse=True
    )
    return points_and_pop
