import json
import rasterio
from rasterio.mask import mask
from shapely.geometry import Point, LineString
from pyproj import Geod

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
