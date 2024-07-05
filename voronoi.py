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
import random
import rasterio
from rasterio.mask import mask

spanishPopRaster = rasterio.open("./data/spain_pop.tif")


def get_population(poly):
    # Convert string to JSON
    geoJSON = json.loads(poly)

    # Load population raster, mask it by the polygon and crop it
    try:
        out_image, out_transform = mask(spanishPopRaster, [geoJSON], crop=True)

        # Clean negative values
        out_image = out_image[out_image >= 0]

        # Get total population
        totalPop = int(out_image.sum())

        return totalPop
    except ValueError as error:
        return {"error": error}


fiware_containers = []
with open("./data/WasteContainers_FIWARE.json") as f:
    fiware_containers = json.load(f)

# Load containers out of FIWARE data platform
df_no_fiware_containers = pd.read_csv("./data/contenedores_aceite_sin_fiware.csv")

# Valencia districts
districts = gpd.read_file("./data/districtes-distritos.geojson")

# districts = unary_union(districts["geometry"])
districts = districts.dissolve()["geometry"][0]

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


def random_solution(size):
    """Creates a vector with random 0 and 1 values."""
    return [random.randint(0, 1) for _ in range(size)]


def generate_random_pop(pop_size, solution_size):
    """Creates a random vectors population."""
    return [random_solution(solution_size) for _ in range(pop_size)]


def get_solution_coords(solution_vector):
    points = []
    for i, location in enumerate(possible_locations):
        if solution_vector[i] == 1:
            points.append(location["location"])
    return points


def fitness(solution):
    # Get solution coords
    voronoi_coords = get_solution_coords(solution)

    # Generate voronoi polygons
    voronoi = voronoi_polygons(MultiPoint(voronoi_coords), extend_to=districts)

    # Intersect generated polygons with Valencia region
    voronoi_intersected = []
    for poly in voronoi.geoms:
        voronoi_intersected.append(intersection(poly, districts))

    voronoi = []
    for polygon in voronoi_intersected:

        dict_polygon = {"polygon": polygon}

        # Convert shapely.Polygon to geojson
        geometry = to_geojson(polygon)

        # Get pop in the poly
        population = get_population(geometry)

        # Store it
        dict_polygon["population"] = population
        voronoi.append(dict_polygon)

    service_level = 1 * 1000

    return sum(voronoi[i]["population"] - service_level for i in range(len(voronoi)))


def select_parents(population, population_fitness, parents_number):
    """Select a number of parents using roulette selection."""

    weights = [1.0 / w for w in population_fitness]  # Invert all weights
    sum_weights = sum(weights)
    weights = [w / sum_weights for w in weights]  # Normalize weights

    selected = random.choices(population, weights=weights, k=parents_number)
    return selected


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


# Params
solution_size = 394
pop_size = 100
generation_number = 100
parents_number = 50
mutation_rate = 0.01

# Generate initial pop
population = generate_random_pop(pop_size, solution_size)

# Main loop of the genetic algorithm
for generation in range(generation_number):

    # Get fitness of current pop
    fitness_poblacion = [fitness(solution) for solution in population]

    # Print the best fitness of current generation
    the_best = min(fitness_poblacion)
    print(f"Generation {generation + 1} | Best fitness: {the_best}")

    # Select parents
    parents = select_parents(population, fitness_poblacion, parents_number)

    # Generate new population through crossovers
    new_population = []
    while len(new_population) < pop_size:
        parent1, parent2 = random.sample(parents, 2)
        child1, child2 = cross_parents(parent1, parent2)
        new_population.extend([child1, child2])

    # Ensure that the new stock is correctly sized
    new_population = new_population[:pop_size]

    # Mutate the individuals of the new population
    for individual in new_population:
        mutate_solution(individual, mutation_rate)

    # Replace the old population with the new population
    population = new_population

# Assessing the fitness of the final stock
fitness_poblacion = [fitness(individuo) for individuo in population]

# Find and display the best individual from the final population.
best_solution = population[fitness_poblacion.index(min(fitness_poblacion))]
print(f"Mejor Individuo: {best_solution} | Fitness: {min(fitness_poblacion)}")
