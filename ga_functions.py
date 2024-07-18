from deap import creator
from utils import get_population_from_polygon, get_solution_coords, voronoi_division
from data import (
    individual_size,
    possible_locations,
    valencia_region_polygon,
    heuristic_individual,
)
import random

max_containers = 352
service_level = 1 * 1000  # Service level, containers per inhabitants


def create_individual_random():
    individual = [0] * individual_size
    ones_indices = random.sample(range(individual_size), max_containers)
    for i in ones_indices:
        individual[i] = 1
    return creator.Individual(individual)


def create_heuristic_individual(probability=0.01):
    if not (0 <= probability <= 1):
        raise ValueError("Probability must be between 0 and 1")

    swapped_list = []
    for element in heuristic_individual:
        if element not in (0, 1):
            raise ValueError("List elements must be binary (0 or 1)")

        if random.random() < probability:
            swapped_list.append(1 - element)  # Swap 1 to 0 or 0 to 1
        else:
            swapped_list.append(element)

    return creator.Individual(swapped_list)


def eval_fitness(solution, possible_locations=possible_locations):
    # Get solution coords
    solution_coords = get_solution_coords(solution, possible_locations)

    division = voronoi_division(solution_coords, valencia_region_polygon)

    # Append population to each voronoi polygon
    scores = []
    for polygon in division:
        # Get pop in the poly
        population = get_population_from_polygon(polygon)

        # Get score
        if population >= service_level:
            score = population - service_level
        else:
            score = 0

        scores.append(score)

    return (sum(scores[i] for i in range(len(scores))),)


def feasible(individual):
    if individual.count(1) > max_containers:
        return False
    else:
        return True


def distance(individual):
    return individual.count(1) - max_containers
