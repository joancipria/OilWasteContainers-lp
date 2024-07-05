import random
from genetic_algorithm import (
    generate_random_pop,
    fitness,
    select_parents,
    cross_parents,
    mutate_solution,
)

# Params
solution_size = 394
pop_size = 100
generation_number = 100
parents_number = 50
mutation_rate = 0.01
tournament_size = 5

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
    parents = select_parents(
        population, fitness_poblacion, parents_number, tournament_size
    )

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
