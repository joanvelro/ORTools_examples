"""
A nurse scheduling problem

In the next example, a hospital supervisor needs to create a schedule for four nurses over a three-day period, subject
to the following conditions:

    Each day is divided into three 8-hour shifts.
    Every day, each shift is assigned to a single nurse, and no nurse works more than one shift.
    Each nurse is assigned to at least two shifts during the three-day period.

The following sections present a solution to the nurse scheduling problem.

https://developers.google.com/optimization/scheduling/employee_scheduling
"""

from ortools.sat.python import cp_model


def build_model(all_nurses, all_days, num_shifts, num_days, num_nurses):
    # instance model
    model = cp_model.CpModel()

    # Create variables
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

    # Assign nurses to shifts:
    # Each shift is assigned to a single nurse per day.
    # Each nurse works at most one shift per day.
    # For each shift, the sum of the nurses assigned to that shift is 1.
    for d in all_days:
        for s in all_shifts:
            model.Add(sum(shifts[(n, d, s)] for n in all_nurses) == 1)
    # each nurse works at most one shift per day.
    # For each nurse, the sum of shifts assigned to that nurse is at most 1
    # ("at most" because a nurse might have the day off).
    for n in all_nurses:
        for d in all_days:
            model.AddAtMostOne(shifts[(n, d, s)] for s in all_shifts)

    # Assign shifts evenly
    # Try to distribute the shifts evenly, so that each nurse works min_shifts_per_nurse shifts.
    # If this is not possible, because the total number of shifts is not divisible by the number of nurses,
    # some nurses will be assigned one more shift.
    # each nurse works at least two shifts in the three-day period.
    # // Python integer division operator,  which returns the floor of the usual quotient.
    min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
    if num_shifts * num_days % num_nurses == 0:
        max_shifts_per_nurse = min_shifts_per_nurse
    else:
        max_shifts_per_nurse = min_shifts_per_nurse + 1
    for n in all_nurses:
        num_shifts_worked = []
        for d in all_days:
            for s in all_shifts:
                num_shifts_worked.append(shifts[(n, d, s)])
        model.Add(min_shifts_per_nurse <= sum(num_shifts_worked))
        model.Add(sum(num_shifts_worked) <= max_shifts_per_nurse)

    # Update solver parameters
    # In a non-optimization model, you can enable the search for all solutions.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    # Enumerate all solutions.
    solver.parameters.enumerate_all_solutions = True

    return model, solver, shifts


# Register a Solutions Callback
# You need to register a callback on the solver that will be called at each solution.

class NursesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, shifts, num_nurses, num_days, num_shifts, limit):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._num_nurses = num_nurses
        self._num_days = num_days
        self._num_shifts = num_shifts
        self._solution_count = 0
        self._solution_limit = limit

    def on_solution_callback(self):
        self._solution_count += 1
        print('Solution %i' % self._solution_count)
        for d in range(self._num_days):
            print('Day %i' % d)
            for n in range(self._num_nurses):
                is_working = False
                for s in range(self._num_shifts):
                    if self.Value(self._shifts[(n, d, s)]):
                        is_working = True
                        print('  Nurse %i works shift %i' % (n, s))
                if not is_working:
                    print('  Nurse {} does not work'.format(n))
        if self._solution_count >= self._solution_limit:
            print('Stop search after %i solutions' % self._solution_limit)
            self.StopSearch()

    def solution_count(self):
        return self._solution_count


# Display the first five solutions.
# data
num_nurses = 4
num_shifts = 3
num_days = 3
all_nurses = range(num_nurses)
all_shifts = range(num_shifts)
all_days = range(num_days)
solution_limit = 5

model, solver, shifts = build_model(all_nurses=all_nurses,
                                    all_days=all_days,
                                    num_shifts=num_shifts,
                                    num_days=num_days,
                                    num_nurses=num_nurses)
solution_printer = NursesPartialSolutionPrinter(shifts=shifts,
                                                num_nurses=num_nurses,
                                                num_days=num_days,
                                                num_shifts=num_shifts,
                                                limit=solution_limit)

# invoke the solver
solver.Solve(model, solution_printer)

# Statistics.
print('\nStatistics')
print('  - conflicts      : %i' % solver.NumConflicts())
print('  - branches       : %i' % solver.NumBranches())
print('  - wall time      : %f s' % solver.WallTime())
print('  - solutions found: %i' % solution_printer.solution_count())
