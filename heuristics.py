from shapely import to_geojson
from data import possible_locations, individual_size
from utils import get_isochrone, get_population_from_polygon
from ga_functions import eval_fitness, max_containers

# Isochrone range
isochrone_range = 5  # minutes

# For each possible location, create an isochrone and get pop
points_and_pop = []
for i, location in enumerate(possible_locations):
    isochrone = to_geojson(get_isochrone(location, isochrone_range))
    population = get_population_from_polygon(isochrone)
    points_and_pop.append({"index": i, "population": population})

# Sort by ascending population
points_and_pop = sorted(
    points_and_pop, key=lambda point: point["population"], reverse=True
)

# Get the first max_containers elements from the sorted list
active_points = points_and_pop[:max_containers]
indices = [point["index"] for point in active_points]


# Initialize solution to 0s
solution = [0] * individual_size

# Update the positions specified in active_points to 1
for index in indices:
    solution[index] = 1

# Check constraint and evaluate solution
if solution.count(1) == max_containers:
    fitness = eval_fitness(solution)
    print("Fitness:", fitness)  # (374616,)
else:
    print("The solution does not respect the max_containers constraint")
