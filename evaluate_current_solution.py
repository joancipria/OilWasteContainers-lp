from data import current_locations, valencia_region_polygon
from ga_functions import eval_fitness
from utils import voronoi_division, write_results

solution = [1] * 352

fitness = eval_fitness(solution, possible_locations=current_locations)[0]
voronoi_polygons = voronoi_division(current_locations, valencia_region_polygon)
write_results("current", fitness, solution, current_locations, voronoi_polygons)
