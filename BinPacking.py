"""
The goal of packing problems is to find the best way to pack a set of items of given sizes into containers with fixed
 capacities. A typical application is loading boxes onto delivery trucks efficiently. Often, it's not possible to pack
 all the items, due to the capacity constraints. In that case, the problem is to find a subset of the items with maximum
 total size that will fit in the containers.

There are many types of packing problems. Two of the most important are knapsack problems and bin packing.

Knapsack problems
-------------------
In the simple knapsack problem, there is a single container (a knapsack). The items have values as well as sizes,
and the goal is to pack a subset of the items that has maximum total value.

For the special case in which value is equal to size, the goal is to maximize the total size of the packed items.

There are also more general versions of the knapsack problem. Here are a couple of examples:

    Multidimensional knapsack problems, in which the items have more than one physical quantity, such as weight and
    volume, and the knapsack has a capacity for each quantity. Here, the term dimension does not necessarily refer to
    the usual spatial dimensions of height, length, and width. However, some problems might involve spatial dimensions,
    for example, finding the optimal way to pack rectangular boxes into a rectangular storage bin.

    Multiple knapsack problems, in which there are multiple knapsacks, and the goal is to maximize the total value of
    the packed items in all knapsacks.

Note that you can have a multidimensional problem with a single knapsack, or a multiple knapsack problem with just one
 dimension.

The bin-packing problem
--------------------------
One of the most well-known packing problems is bin-packing, in which there are multiple containers (called bins) of
 equal capacity. Unlike the multiple knapsack problem, the number of bins is not fixed. Instead, the goal is to find
 the smallest number of bins that will hold all the items.

Here's a simple example to illustrate the difference between the multiple knapsack problem and the bin-packing problem.
 Suppose a company has delivery trucks, each of which has an 18,000 pound weight capacity, and 130,000 pounds of items
  to deliver.

    Multiple knapsack: You have five trucks and you want to load a subset of the items that has maximum weight onto
    them.

    Bin packing: You have 20 trucks (more than enough to hold all the items) and you want to use the fewest trucks that
     will hold them all.

The following summarizes the differences between the two problems:

    Multiple knapsack problem: Pack a subset of the items into a fixed number of bins, with varying capacities,
    so that the total value of the packed items is a maximum.

    Bin packing problem: Given as many bins with a common capacity as necessary, find the fewest that will hold all
     the items. In this problem, the items aren't assigned values, because the objective doesn't involve value.


"""

from ortools.linear_solver import pywraplp
from numpy import random


# create the data


def build_model(data):
    print('Building model...')
    # Declare solver
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')
    solver.SetTimeLimit(6000)
    solver.EnableOutput()

    # Create variables
    # Variables
    # x[i, j] = 1 if item i is packed in bin j.
    x = {}
    for i in data['items']:
        for j in data['bins']:
            x[(i, j)] = solver.IntVar(lb=0,
                                      ub=1,
                                      name='x_%i_%i' % (i, j))

    # y[j] = 1 if bin j is used.
    y = {}
    for j in data['bins']:
        y[j] = solver.IntVar(lb=0,
                             ub=1,
                             name='y[%i]' % j)

    # As in the multiple knapsack example, you define an array of variables x[(i, j)], whose value is 1 if item i is
    # placed in bin j, and 0 otherwise.
    #
    # For bin packing, you also define an array of variables, y[j], whose value is 1 if bin j is used—that is,
    # if any items are packed in it—and 0 otherwise. The sum of the y[j] will be the number of bins used.

    # Constraints
    # Each item must be in exactly one bin.
    for i in data['items']:
        solver.Add(sum(x[i, j] for j in data['bins']) == 1)

    # The amount packed in each bin cannot exceed its capacity.
    for j in data['bins']:
        solver.Add(sum(x[(i, j)] * data['weights'][i] for i in data['items']) <= y[j] * data['bin_capacity'])

    # Define the objective: minimize the number of bins used.
    solver.Minimize(solver.Sum([y[j] for j in data['bins']]))

    return solver, y, x


def solve_model(solver):
    print('Solving...')
    status = solver.Solve()
    return status


def build_solution(data, status, y, x):
    print('Building solution...')
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        if status == pywraplp.Solver.OPTIMAL:
            print('\nOPTIMAL Solution Founded\n')
        elif status == pywraplp.Solver.FEASIBLE:
            print('\nFEASIBLE Solution Founded\n')

        num_bins = 0.
        for j in data['bins']:
            if y[j].solution_value() == 1:
                bin_items = []
                bin_weight = 0
                for i in data['items']:
                    if x[i, j].solution_value() > 0:
                        bin_items.append(i)
                        bin_weight += data['weights'][i]
                if bin_weight > 0:
                    num_bins += 1
                    print('Bin number', j)
                    print('  Items packed:', bin_items)
                    print('  Total weight:', bin_weight)
                    print()
        print()
        print('Number of bins used:', num_bins)
        print('Time = ', solver.WallTime(), ' milliseconds')

    elif status == pywraplp.Solver.INFEASIBLE:
        print('\nINFEASIBLE PROBLEM: The problem does not have an optimal solution.')


def create_data_model():
    """Create the data for the example."""
    data = {}
    weights = [48, 30, 19, 36, 36, 27, 42, 42, 36, 24, 30]  # vector containing the weights of the items.
    data['weights'] = weights
    data['items'] = list(range(len(weights)))
    data['bins'] = data['items']
    data['bin_capacity'] = 100  # capacity of the bins.
    return data


def create_large_data_model():
    """Create the data for the example."""
    data = {}
    weights = list(random.uniform(low=25, high=50, size=100))  # vector containing the weights of the items.
    data['weights'] = weights
    data['items'] = list(range(len(weights)))
    data['bins'] = data['items']
    data['bin_capacity'] = 200  # capacity of the bins.
    return data


if __name__ == "__main__":
    # data = create_data_model()
    data = create_large_data_model()
    solver, y, x = build_model(data)
    status = solve_model(solver)
    build_solution(data, status, y, x)
