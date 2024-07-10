import json
import geopandas as gpd

# Valencia region
valencia_region_polygon = gpd.read_file("./data/valencia_region.geojson").dissolve()[
    "geometry"
][0]


def load_input_data():
    try:
        with open("./data/possible_locations.json") as f:
            possible_locations = json.load(f)

            return possible_locations, len(possible_locations)

    except ValueError as error:
        print({"error": error})


# Load input data
possible_locations, individual_size = load_input_data()
