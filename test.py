from data import possible_locations
from ga_functions import eval_fitness

solution = [1] * 5237

print(eval_fitness(solution, possible_locations))
