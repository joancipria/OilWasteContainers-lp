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


def create_heuristic_individual(mutation_probability=0.4):
    shuffled_chromosome = heuristic_individual[:]
    # Mutate it
    random.shuffle(shuffled_chromosome)

    # # Obtener los índices de todos los elementos 1 en la lista
    # ones_indices = [i for i, value in enumerate(chromosome) if value == 1]
    
    # # Seleccionar aleatoriamente los índices de los elementos 1 que se van a eliminar
    # indices_to_remove = random.sample(ones_indices, num_ones_to_remove)
    
    # # Crear una copia del cromosoma original
    # new_chromosome = chromosome[:]
    
    # # Eliminar los elementos en los índices seleccionados
    # for index in sorted(indices_to_remove, reverse=True):
    #     new_chromosome[index] = 0

    return creator.Individual(shuffled_chromosome)


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
