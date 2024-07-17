from shapely import to_geojson, Polygon
from data import possible_locations, individual_size
from utils import generate_isochrones
from ga_functions import eval_fitness, max_containers
import json

# Isochrone range
isochrone_range = 5  # minutes


def max_population_heuristic(
    possible_locations, individual_size, max_containers, isochrone_range
):
    """
    Selects a subset of locations that maximizes population ensuring the number of containers does not exceed max_containers.
    """
    # Get population
    points_and_pop = generate_isochrones(possible_locations, isochrone_range)

    # Get the first max_containers elements from the sorted list
    active_points = points_and_pop[:max_containers]
    indices = [point["index"] for point in active_points]

    # Initialize solution to 0s
    solution = [0] * individual_size

    # Update the positions specified in active_points to 1
    for index in indices:
        solution[index] = 1

    # Check constraint and evaluate solution
    num_containers = solution.count(1)

    if num_containers == max_containers:
        fitness = eval_fitness(solution)
        print("Fitness:", fitness, "Containers: ", num_containers)  # (374616,)

        # Convert and write to json file
        with open("./results/max_population_heuristic.json", "w") as outfile:
            json.dump(
                {
                    "fitness": fitness,
                    "num_containers": num_containers,
                    "solution": solution,
                },
                outfile,
            )
        return fitness, solution
    else:
        print("The solution does not respect the max_containers constraint")
        return None


def max_population_min_overlap_heuristic(
    possible_locations, individual_size, max_containers, isochrone_range, threshold=0.56
):
    """
    Selects a subset of locations that maximizes population while minimizing overlap and
    ensuring the number of containers does not exceed max_containers.
    """
    # Get population
    points_and_pop = generate_isochrones(possible_locations, isochrone_range)

    selected_indices = []
    selected_polygons = []

    for location in points_and_pop:
        if len(selected_indices) >= max_containers:
            break

        new_polygon = location["isochrone"]
        # Check if the new polygon overlaps significantly with any of the already selected polygons
        if all(
            new_polygon.intersection(selected_polygon).area
            < new_polygon.area * threshold
            for selected_polygon in selected_polygons
        ):
            selected_indices.append(location["index"])
            selected_polygons.append(new_polygon)

    # Initialize solution to 0s
    solution = [0] * individual_size

    # Update the positions specified in active_points to 1
    for index in selected_indices:
        solution[index] = 1

    # Check constraint and evaluate solution
    num_containers = solution.count(1)

    if solution.count(1) <= max_containers:
        fitness = eval_fitness(solution)
        print(
            "Fitness:",
            fitness,
            "Containers: ",
            num_containers,
            "Overlap threshold: ",
            threshold,
        )  # (260021,)

        # Convert and write to json file
        with open(
            "./results/max_population_min_overlap_heuristic.json", "w"
        ) as outfile:
            json.dump(
                {
                    "fitness": fitness,
                    "num_containers": num_containers,
                    "overlap_threshold": threshold,
                    "solution": solution,
                },
                outfile,
            )
        return fitness, solution
    else:
        print("The solution does not respect the max_containers constraint")
        return None


def main():
    # Run heuristics
    max_population_heuristic(
        possible_locations, individual_size, max_containers, isochrone_range
    )
    max_population_min_overlap_heuristic(
        possible_locations,
        individual_size,
        max_containers,
        isochrone_range,
        threshold=0.56,
    )
