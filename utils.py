import json
import rasterio
from rasterio.mask import mask

# Load population raster
pop_raster = rasterio.open("./data/spain_pop.tif")


def get_population_from_polygon(polygon):
    polygon = json.loads(polygon)
    """
    Returns number of people in a polygon

    :param json polygon: Polygon in geoJSON format
    """
    # Mask raster by the polygon and crop it
    try:
        out_image, out_transform = mask(pop_raster, [polygon], crop=True)

        # Clean negative values
        out_image = out_image[out_image >= 0]

        # Get total population
        total_pop = int(out_image.sum())

        return total_pop
    except ValueError as error:
        return {"error": error}
