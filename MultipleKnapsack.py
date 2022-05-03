"""
Given a collection of items of varying weights and values. The problem is to pack a subset of the items into five
bins, each of which has a maximum capacity of 100, so that the total packed value is a maximum.
"""
from ortools.linear_solver import pywraplp


# data
def create_data_input():
    data = {'weights': [48, 30, 42, 36, 36, 48, 42, 42, 36, 24, 30, 30, 42, 36, 36],
            'values': [10, 30, 25, 50, 35, 30, 15, 40, 30, 35, 45, 10, 20, 30, 25]
            }
    assert len(data['weights']) == len(data['values'])
    data['num_items'] = len(data['weights'])
    data['all_items'] = range(data['num_items'])

    data['bin_capacities'] = [100, 100, 100, 100, 100]
    data['num_bins'] = len(data['bin_capacities'])
    data['all_bins'] = range(data['num_bins'])
    return data


def build_model(data):
    # declare mip solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    solver.SetTimeLimit(6000)  # 6 seconds
    solver.EnableOutput()
    # solver.
    if solver is None:
        print("SCIP solver unavailable.")
        raise Exception

    # declare the variables # x[i, b] = 1 if item i is packed in bin b.
    x = {}
    for i in data['all_items']:
        for b in data['all_bins']:
            x[i, b] = solver.BoolVar(name=f'x_{i}_{b}')

    # define constraints
    # Each item is assigned to at most one bin.
    for i in data['all_items']:
        solver.Add(sum(x[i, b] for b in data['all_bins']) <= 1)  # it can be assigned the item "i" to the bin "b" or not

    # The amount packed in each bin cannot exceed its capacity.
    for b in data['all_bins']:
        solver.Add(sum(x[i, b] * data['weights'][i] for i in data['all_items']) <= data['bin_capacities'][b])

    # define objective
    # Maximize total value of packed items sum(x[i,b]* value(i) for i in all_items for b in all bins)
    objective = solver.Objective()
    for i in data['all_items']:
        for b in data['all_bins']:
            objective.SetCoefficient(var=x[i, b],
                                     coeff=data['values'][i])
    objective.SetMaximization()

    return solver, objective, x


def solve_model(solver):
    # invoke solver
    status = solver.Solve()
    return status


def build_solution(status, objective, data, x):
    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        if status == pywraplp.Solver.OPTIMAL:
            print('\n')
            print(f'OPTIMAL Solution founded. Total packed value: {objective.Value()}')
            print('\n')
        elif status == pywraplp.Solver.FEASIBLE:
            print('\n')
            print(f'FEASIBLE Solution founded. Total packed value: {objective.Value()}')
            print('\n')
        total_weight = 0
        for b in data['all_bins']:
            print(f'Bin {b}')
            bin_weight = 0
            bin_value = 0
            for i in data['all_items']:
                if x[i, b].solution_value() > 0:
                    print(f"Item {i} weight: {data['weights'][i]} value: {data['values'][i]}")
                    bin_weight += data['weights'][i]
                    bin_value += data['values'][i]
            print(f'Packed bin weight: {bin_weight}')
            print(f'Packed bin value: {bin_value}\n')
            total_weight += bin_weight
        print(f'Total packed weight: {total_weight}')
    elif status == pywraplp.Solver.INFEASIBLE:
        print('INFEASIBLE PROBLEM, The problem does not have an optimal solution.')


if __name__ == "__main__":
    data = create_data_input()
    solver, objective, x = build_model(data)
    status = solve_model(solver)
    build_solution(status, objective, data, x)
