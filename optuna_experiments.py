import optuna
import random
import numpy
from deap import base, creator, tools, algorithms
from ga_functions import eval_fitness, feasible, max_containers, create_individual


# Define la función objetivo que ejecuta tu algoritmo genético
def objective(trial):
    # Parametros fijos
    not_feasible_penalty = 900000
    ngen = 200  # Number of generations
    indpb_mate = 0.5  # Independent probability for each attribute to be exchanged
    indpb_mutate = 0.05  # Independent probability for each attribute to be flipped.

    # Define los parámetros a optimizar
    mutation_prob = trial.suggest_uniform("mutation_prob", 0.01, 0.5)
    crossover_prob = trial.suggest_uniform("crossover_prob", 0.2, 0.8)
    population_size = trial.suggest_categorical("population_size", [200, 300, 400, 500])
    tournament_size = trial.suggest_categorical("tournament_size", [2, 4, 6, 8, 10])

    # Configura DEAP con los parámetros sugeridos por Optuna
    # Aquí construyes tu algoritmo genético con DEAP y configuras los operadores,
    # la población inicial, etc., utilizando los valores de mutation_prob,
    # crossover_prob y population_size

    # Ejemplo simplificado de configuración de DEAP
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("attr_bool", random.randint, 0, 1)
    toolbox.register(
        "individual",
        create_individual,
        # tools.initRepeat,
        # creator.Individual,
        # toolbox.attr_bool,
        # individual_size,
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Operators
    toolbox.register("evaluate", eval_fitness)
    toolbox.decorate("evaluate", tools.DeltaPenality(feasible, not_feasible_penalty))
    toolbox.register("mate", tools.cxUniform, indpb=indpb_mate)
    toolbox.register("mutate", tools.mutFlipBit, indpb=indpb_mutate)
    toolbox.register("select", tools.selTournament, tournsize=tournament_size)

    pop = toolbox.population(n=population_size)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    pop, log = algorithms.eaSimple(
        pop,
        toolbox,
        crossover_prob,
        mutation_prob,
        ngen,
        stats=stats,
        halloffame=hof,
        verbose=True,
    )
    best_individual = hof.items[0]
    best_fitness = eval_fitness(best_individual)

    # Evalúa la métrica que deseas optimizar (por ejemplo, precisión)
    # En este ejemplo ficticio, simplemente devuelve una métrica de prueba
    return best_fitness


# Configura y ejecuta el estudio de Optuna
study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=100)

# Imprime los mejores hiperparámetros encontrados por Optuna
print("Best trial:")
best_trial = study.best_trial
print(f"  Value: {best_trial.value}")
print("  Params: ")
for key, value in best_trial.params.items():
    print(f"    {key}: {value}")
