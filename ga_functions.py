from deap import creator
from shapely import (
    to_geojson,
    voronoi_polygons,
    intersection,
    MultiPoint,
)
from utils import get_population_from_polygon, get_solution_coords
from data import valencia_region_polygon, individual_size, possible_locations
import random

max_containers = 352
service_level = 1 * 1000  # Service level, containers per inhabitants


def create_individual():
    individual = [0] * individual_size
    ones_indices = random.sample(range(individual_size), max_containers)
    for i in ones_indices:
        individual[i] = 1
    return creator.Individual(individual)


def eval_fitness(solution):
    # Get solution coords
    solution_coords = get_solution_coords(solution, possible_locations)

    # Generate voronoi polygons
    voronoi = voronoi_polygons(
        MultiPoint(solution_coords), extend_to=valencia_region_polygon
    )

    # Intersect generated polygons with Valencia region
    voronoi_intersected = []
    for polygon in voronoi.geoms:
        voronoi_intersected.append(intersection(polygon, valencia_region_polygon))

    # Append population to each voronoi polygon
    voronoi = []
    for polygon in voronoi_intersected:
        if not polygon.is_empty:

            dict_polygon = {"polygon": polygon}

            # Convert shapely.Polygon to geojson
            geometry = to_geojson(polygon)

            # Get pop in the poly
            population = get_population_from_polygon(geometry)

            # Store it
            dict_polygon["population"] = population

            # Get score
            if population >= service_level:
                dict_polygon["score"] = population - service_level
            else:
                dict_polygon["score"] = 0

            voronoi.append(dict_polygon)

    return (sum(voronoi[i]["score"] for i in range(len(voronoi))),)


def feasible(individual):
    if individual.count(1) > max_containers:
        return False
    else:
        return True


def distance(individual):
    return individual.count(1) - max_containers
