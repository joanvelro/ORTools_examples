"""
A nurse scheduling problem with shift request

In the next example, a hospital supervisor needs to create a schedule for four nurses over a three-day period, subject
 to the following conditions:

In this case, we add nurse requests for specific shifts

    Each day is divided into three 8-hour shifts.
    Every day, each shift is assigned to a single nurse, and no nurse works more than one shift.
    Each nurse is assigned to at least two shifts during the three-day period.

The following sections present a solution to the nurse scheduling problem.

https://developers.google.com/optimization/scheduling/employee_scheduling
"""

from ortools.sat.python import cp_model


def build_model(num_nurses, num_shifts, num_days, shift_requests):

    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)

    model = cp_model.CpModel()

    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.NewBoolVar(name='shift_n%id%is%i' % (n, d, s))

    for d in all_days:
        for s in all_shifts:
            # model.AddExactlyOne(shifts[(n, d, s)] for n in all_nurses)
            model.Add(sum(shifts[(n, d, s)] for n in all_nurses) == 1)

    for n in all_nurses:
        for d in all_days:
            model.AddAtMostOne(shifts[(n, d, s)] for s in all_shifts)

    # Try to distribute the shifts evenly, so that each nurse works
    # min_shifts_per_nurse shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of nurses, some nurses will
    # be assigned one more shift.
    min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
    if num_shifts * num_days % num_nurses == 0:
        max_shifts_per_nurse = min_shifts_per_nurse
    else:
        max_shifts_per_nurse = min_shifts_per_nurse + 1
    for n in all_nurses:
        num_shifts_worked = 0
        for d in all_days:
            for s in all_shifts:
                num_shifts_worked += shifts[(n, d, s)]
        model.Add(min_shifts_per_nurse <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_nurse)

    # pylint: disable=g-complex-comprehension
    objective_function = sum(shift_requests[n][d][s] * shifts[(n, d, s)]
                             for n in all_nurses
                             for d in all_days
                             for s in all_shifts)
    model.Maximize(objective_function)

    return model, min_shifts_per_nurse, shifts


def solve_model(model):
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    return status, solver


def build_solution(status, shifts, solver, min_shifts_per_nurse):
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('Optimal Solution'.format(status))
        # print('Solution:')
        all_nurses = range(num_nurses)
        all_shifts = range(num_shifts)
        all_days = range(num_days)
        for d in all_days:
            print('Day', d)
            for n in all_nurses:
                for s in all_shifts:
                    if solver.Value(shifts[(n, d, s)]) == 1:
                        if shift_requests[n][d][s] == 1:
                            print('Nurse', n, 'works shift', s, '(requested).')
                        else:
                            print('Nurse', n, 'works shift', s, '(not requested).')
            print()
        print(f'Number of shift requests met = {solver.ObjectiveValue()}',
              f'(out of {num_nurses * min_shifts_per_nurse})')

        # Statistics.
        print('\nStatistics')
        print('  - conflicts: %i' % solver.NumConflicts())
        print('  - branches : %i' % solver.NumBranches())
        print('  - wall time: %f s' % solver.WallTime())
    elif status == cp_model.INFEASIBLE:
        print('Infeasible Problem: No optimal solution found !')


if __name__ == "__main__":
    num_nurses = 5
    num_shifts = 3
    num_days = 7

    #                   # Day1      Day2       Day3       Day4       Day5       Day6        Day7
    #            Shifts 1  2  3
    shift_requests = [[[0, 0, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 1]],  # nurse 1
                      [[0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1]],  # nurse 2
                      [[0, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0], [0, 1, 0], [0, 0, 0]],  # nurse 3
                      [[0, 0, 1], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0]],  # nurse 4
                      [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0]]]  # nurse 5

    model, min_shifts_per_nurse, shifts = build_model(num_nurses, num_shifts, num_days, shift_requests)
    status, solver = solve_model(model)
    build_solution(status, shifts, solver, min_shifts_per_nurse)
