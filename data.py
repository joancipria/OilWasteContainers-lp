import json
import geopandas as gpd

# Valencia region
valencia_region_polygon = gpd.read_file("./data/valencia_region.geojson").dissolve()[
    "geometry"
][0]

# Raster file for pop calculations
raster_file = "./data/valencia.tif"

def load_input_data():
    try:
        with open("./data/possible_locations.json") as f:
            possible_locations = json.load(f)

        with open("./data/current_locations.json") as f:
            current_locations = json.load(f)

        with open("./results/max_population_min_overlap_heuristic.json") as f:
            heuristic_individual = json.load(f)["solution"]
            return (
                possible_locations,
                len(possible_locations),
                current_locations,
                heuristic_individual,
            )

    except ValueError as error:
        print({"error": error})


# Load input data
possible_locations, individual_size, current_locations, heuristic_individual = (
    load_input_data()
)
