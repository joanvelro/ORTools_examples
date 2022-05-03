"""
Knapsack Problem
Pack a set of items, with given values and sizes (such as weights or volumes), into a container with a maximum
capacity. If the total size of the items exceeds the capacity, you can't pack them all. In that case, the problem is
to choose a subset of the items of maximum total value that will fit in the container.

The following sections show how to solve a knapsack problem using OR-Tools.
"""

from ortools.algorithms import pywrapknapsack_solver

# data
values = [
    360, 83, 59, 130, 431, 67, 230, 52, 93, 125, 670, 892, 600, 38, 48, 147,
    78, 256, 63, 17, 120, 164, 432, 35, 92, 110, 22, 42, 50, 323, 514, 28,
    87, 73, 78, 15, 26, 78, 210, 36, 85, 189, 274, 43, 33, 10, 19, 389, 276,
    312
]
weights = [[
    7, 0, 30, 22, 80, 94, 11, 81, 70, 64, 59, 18, 0, 36, 3, 8, 15, 42, 9, 0,
    42, 47, 52, 32, 26, 48, 55, 6, 29, 84, 2, 4, 18, 56, 7, 29, 93, 44, 71,
    3, 86, 66, 31, 65, 0, 79, 20, 65, 52, 13
]]
capacities = [850]

data = {'values': values,  # values of the items.
        'weights': weights,  # weights of the items.
        'capacities': capacities}  # capacity of the knapsack.

# declare solver
solver = pywrapknapsack_solver.KnapsackSolver(
    pywrapknapsack_solver.KnapsackSolver.
        KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'KnapsackExample')  # use the branch and bound algorithm

# call the solver
solver.Init(data['values'],
            data['weights'],
            data['capacities'])
computed_value = solver.Solve()  # The total value of the optimal solution is computed_value,
# which is the same as the total weight in this case
packed_items = []
packed_weights = []
total_weight = 0
print('Total value =', computed_value)
for i in range(len(data['values'])):
    if solver.BestSolutionContains(i):
        packed_items.append(i)
        packed_weights.append(data['weights'][0][i])
        total_weight += data['weights'][0][i]
print('Total weight:', total_weight)
print('Packed items:', packed_items)
print('Packed_weights:', packed_weights)

packed_items = [x for x in range(0, len(data['weights'][0]))
                if solver.BestSolutionContains(x)]
