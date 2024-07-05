import random
from shapely import (
    to_geojson,
    voronoi_polygons,
    Point,
    intersection,
    MultiPoint,
)
from utils import get_population_from_polygon
from data import possible_locations, valencia_region_polygon, get_solution_coords


def random_solution(size):
    """Creates a vector with random 0 and 1 values."""
    return [random.randint(0, 1) for _ in range(size)]


def generate_random_pop(pop_size, solution_size):
    """Creates a random vectors population."""
    return [random_solution(solution_size) for _ in range(pop_size)]


def fitness(solution):
    # Get solution coords
    solution_coords = get_solution_coords(solution)

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
            voronoi.append(dict_polygon)

    # SL (Service Level, 1 container per 1000 inhabitants)
    service_level = 1 * 1000

    return sum(voronoi[i]["population"] - service_level for i in range(len(voronoi)))


def select_parents(population, population_fitness, parents_number, tournament_size):
    """SSelect parents using the tournament strategy."""
    selected_parents = []
    for _ in range(parents_number):
        tournament = random.sample(
            list(zip(population, population_fitness)), tournament_size
        )
        winner = min(tournament, key=lambda x: x[1])
        selected_parents.append(winner[0])
    return selected_parents


def cross_parents(parent1, parent2):
    """Cross two parents to generate two children using a crossover point."""
    cross_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:cross_point] + parent2[cross_point:]
    child2 = parent2[:cross_point] + parent1[cross_point:]
    return child1, child2


def mutate_solution(solution, mutation_rate):
    """Mutate an solution by randomly changing its genes at a given mutation rate."""
    for i in range(len(solution)):
        if random.random() < mutation_rate:
            solution[i] = 1 if solution[i] == 0 else 0
