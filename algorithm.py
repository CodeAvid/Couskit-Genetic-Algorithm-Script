import data as dt
import cost_functions
import mutation
from copy import deepcopy

max_generations = 5001
num_runs = 1
input_file = 'sample/input.json'
output_file = 'sample/output.json'
cost_function = cost_functions.cost
cost_function2 = cost_functions.cost2


def evolutionary_algorithm():
    best_timetable = None
    data = dt.load_data(input_file)
    neighbour = mutation.neighbour
    for i in range(num_runs):
        chromosome = dt.generate_chromosome(data)

        for j in range(max_generations):
            new_chromosome = neighbour(deepcopy(chromosome))
            ft = cost_function(chromosome)
            if ft == 0:
                break
            ftn = cost_function(new_chromosome)
            if ftn <= ft:
                chromosome = new_chromosome
            if j % 200 == 0:
                print('Iteration', j, 'cost', cost_function(chromosome))

        # print('Run', i + 1, 'cost', cost_function(chromosome), 'chromosome', chromosome)

        if best_timetable is None or cost_function2(chromosome) <= cost_function2(best_timetable):
            best_timetable = deepcopy(chromosome)

    chromosome = best_timetable

    neighbour2 = mutation.neighbour2

    for j in range(3 * max_generations):
        new_chromosome = neighbour2(deepcopy(chromosome))
        ft = cost_function2(chromosome)
        ftn = cost_function2(new_chromosome)
        if ftn <= ft:
            chromosome = new_chromosome
        if j % 200 == 0:
            print('Iteration', j, 'cost', cost_function2(chromosome))

    # print('Run', 'cost', cost_function2(chromosome), 'chromosome', chromosome)

    dt.write_data(chromosome[0], output_file)


evolutionary_algorithm()
