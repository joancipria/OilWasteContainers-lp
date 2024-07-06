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


def random_solution(size, max_ones):
    """Creates a vector with random 0 and 1 values, limiting 1 values to max_ones"""
    solution = [0] * size
    ones_positions = random.sample(range(size), max_ones)
    for pos in ones_positions:
        solution[pos] = 1
    return solution


def generate_random_pop(pop_size, solution_size, max_ones):
    """Creates a list with random solutions"""
    return [random_solution(solution_size, max_ones) for _ in range(pop_size)]


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
    """Select parents using the tournament strategy."""
    selected_parents = []
    for _ in range(parents_number):
        tournament = random.sample(
            list(zip(population, population_fitness)), tournament_size
        )
        winner = min(tournament, key=lambda x: x[1])
        selected_parents.append(winner[0])
    return selected_parents


def cross_parents_one_point(parent1, parent2, max_ones):
    """Cross two parents to generate two children using a crossover point."""
    cross_point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:cross_point] + parent2[cross_point:]
    child2 = parent2[:cross_point] + parent1[cross_point:]

    # Repair solution if it has more 1s than max_ones
    if child1.count(1) > max_ones:
        child1 = repair_solution(child1, max_ones)
    if child2.count(1) > max_ones:
        child2 = repair_solution(child2, max_ones)
    return child1, child2


def cross_parents_uniform(parent1, parent2, max_ones):
    """Cross two parents to generate two children using uniform crossover"""
    child1 = []
    child2 = []

    for gen1, gen2 in zip(parent1, parent2):
        if random.random() < 0.5:
            child1.append(gen1)
            child2.append(gen2)
        else:
            child1.append(gen2)
            child2.append(gen1)

    # Repair solution if it has more 1s than max_ones
    if child1.count(1) > max_ones:
        child1 = repair_solution(child1, max_ones)
    if child2.count(1) > max_ones:
        child2 = repair_solution(child2, max_ones)

    return child1, child2


def repair_solution(solution, max_ones):
    """Repair a solution by ensuring it has no more than max_ones 1s"""
    while solution.count(1) > max_ones:
        one_indices = [i for i, gene in enumerate(solution) if gene == 1]
        solution[random.choice(one_indices)] = 0
    return solution


def mutate_solution(solution, mutation_rate, max_ones):
    """Mutate an solution by randomly changing its genes at a given mutation rate."""
    for i in range(len(solution)):
        if random.random() < mutation_rate:
            if solution[i] == 0:
                if solution.count(1) < max_ones:
                    solution[i] = 1
            else:
                solution[i] = 0
