from ortools.sat.python import cp_model
from pandas import DataFrame


def build_model(input_data_instance):
    """
    Build model
    :param input_data_instance:
    :return:
    """
    # Instance model
    model = cp_model.CpModel()

    # Sets
    inputs = input_data_instance["Inputs"]  # List size Li
    outputs = input_data_instance["Outputs"]  # List size Lo

    # Constants
    V = input_data_instance["V"]
    t_min = input_data_instance["Tmin"]
    t_max = input_data_instance["Tmax"]
    V_max_buffer = input_data_instance["VMaxBuffer"]
    number_batches = input_data_instance["NoBatches"]

    # Parameters
    T_in = input_data_instance["Tin"]  # dict size Li
    T_out = input_data_instance["Tout"]  # dict size Lo

    # Variables
    # Binary Variables
    A_I = {(i, k): model.NewBoolVar(name='')
           for i in range(number_batches)
           for k in inputs}
    A_O = {(i, k): model.NewBoolVar(name='')
           for i in range(number_batches)
           for k in outputs}
    # Integer Variables
    # Start/End times
    S_INPUT = {i: model.NewIntVar(lb=t_min,
                                  ub=t_max,
                                  name='')
               for i in range(number_batches)}
    S_BUFFER = {i: model.NewIntVar(lb=t_min,
                                   ub=t_max,
                                   name='')
                for i in range(number_batches)}
    S_OUTPUT = {i: model.NewIntVar(lb=t_min,
                                   ub=t_max,
                                   name='')
                for i in range(number_batches)}
    D_INPUT = {i: model.NewIntVar(lb=t_min,
                                  ub=t_max,
                                  name='')
               for i in range(number_batches)}
    D_BUFFER = {i: model.NewIntVar(lb=1,
                                   ub=t_max,
                                   name='')
                for i in range(number_batches)}
    D_OUTPUT = {i: model.NewIntVar(lb=t_min,
                                   ub=t_max,
                                   name='')
                for i in range(number_batches)}
    E_INPUT = {i: model.NewIntVar(lb=t_min,
                                  ub=t_max,
                                  name='')
               for i in range(number_batches)}
    E_BUFFER = {i: model.NewIntVar(lb=t_min,
                                   ub=t_max,
                                   name='')
                for i in range(number_batches)}
    E_OUTPUT = {i: model.NewIntVar(lb=t_min,
                                   ub=t_max,
                                   name='')
                for i in range(number_batches)}
    # Volume buffer
    V_BUFFER_1 = {i: model.NewIntVar(lb=0,
                                     ub=V_max_buffer,
                                     name='')
                  for i in range(number_batches)}
    V_BUFFER_2 = {i: model.NewIntVar(lb=0,
                                     ub=V_max_buffer,
                                     name='')
                  for i in range(number_batches)}

    # Interval variables (expressions)
    B_INPUT = {i: model.NewIntervalVar(start=S_INPUT[i],
                                       size=D_INPUT[i],
                                       end=E_INPUT[i],
                                       name='')
               for i in range(number_batches)}
    B_BUFFER = {i: model.NewIntervalVar(start=S_BUFFER[i],
                                        size=D_BUFFER[i],
                                        end=E_BUFFER[i],
                                        name='')
                for i in range(number_batches)}
    B_OUTPUT = {i: model.NewIntervalVar(start=S_OUTPUT[i],
                                        size=D_OUTPUT[i],
                                        end=E_OUTPUT[i],
                                        name='')
                for i in range(number_batches)}
    V_BUFFER = {i: model.NewIntervalVar(start=V_BUFFER_1[i],
                                        size=V,
                                        end=V_BUFFER_2[i],
                                        name='')
                for i in range(number_batches)}

    # Constraints
    for i in range(number_batches):
        model.Add(sum(A_I[(i, k)] for k in inputs) == 1)

    for i in range(number_batches):
        model.Add(sum(A_O[(i, k)] for k in outputs) == 1)

    for i in range(number_batches):
        for k in inputs:
            model.Add(D_INPUT[i] == T_in[k]).OnlyEnforceIf(A_I[i, k])
        for k in outputs:
            model.Add(D_INPUT[i] == T_out[k]).OnlyEnforceIf(A_O[i, k])

    for i in range(number_batches):
        model.Add(S_BUFFER[i] == E_INPUT[i])
        model.Add(S_OUTPUT[i] == E_BUFFER[i])

    model.AddNoOverlap2D(B_BUFFER.values(), V_BUFFER.values())

    # objective
    model.Minimize(E_BUFFER[number_batches - 1])

    variables = {'A_I': A_I,
                 'A_O': A_O,
                 'V_BUFFER_1': V_BUFFER_1,
                 'V_BUFFER_2': V_BUFFER_2,
                 'V_BUFFER': V_BUFFER,
                 'B_OUTPUT': B_OUTPUT,
                 'B_INPUT': B_INPUT,
                 'B_BUFFER': B_BUFFER,
                 'E_BUFFER': E_BUFFER,
                 'E_INPUT': E_INPUT,
                 'E_OUTPUT': E_OUTPUT,
                 'S_INPUT': S_INPUT,
                 'S_OUTPUT': S_OUTPUT,
                 'S_BUFFER': S_BUFFER,
                 'D_INPUT': D_INPUT,
                 'D_OUTPUT': D_OUTPUT,
                 'D_BUFFER': D_BUFFER}

    return model, variables


def solve_model(model):
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print('Optimal Solution Founded')
    elif status == cp_model.FEASIBLE:
        print('Feasible Solution Founded')
    elif status == cp_model.INFEASIBLE:
        print('INFEASIBLE Problem')

    return solver, status


def build_response(solver, input_data, variables):
    df_integer = DataFrame(data={
        'No_Bach': [i for i in range(input_data["NoBatches"])],
        'V_Buffer_1': [solver.Value(variables['V_BUFFER_1'][i]) for i in range(input_data["NoBatches"])],
        'V_Buffer_2': [solver.Value(variables['V_BUFFER_2'][i]) for i in range(input_data["NoBatches"])],
        'E_Buffer': [solver.Value(variables['E_BUFFER'][i]) for i in range(input_data["NoBatches"])],
        'S_Buffer': [solver.Value(variables['S_BUFFER'][i]) for i in range(input_data["NoBatches"])],
        'D_Buffer': [solver.Value(variables['D_BUFFER'][i]) for i in range(input_data["NoBatches"])],
        'E_Input': [solver.Value(variables['E_INPUT'][i]) for i in range(input_data["NoBatches"])],
        'E_Output': [solver.Value(variables['E_OUTPUT'][i]) for i in range(input_data["NoBatches"])],
        'S_Input': [solver.Value(variables['S_INPUT'][i]) for i in range(input_data["NoBatches"])],
        'S_Output': [solver.Value(variables['S_OUTPUT'][i]) for i in range(input_data["NoBatches"])],
        'D_Input': [solver.Value(variables['D_INPUT'][i]) for i in range(input_data["NoBatches"])],
        'D_Output': [solver.Value(variables['D_OUTPUT'][i]) for i in range(input_data["NoBatches"])],
    })
    results_binary = {'A_I': {(i, k): solver.Value(variables['A_I'][(i, k)]) for i in range(input_data["NoBatches"])
                              for k in input_data["Inputs"]},
                      'A_O': {(i, k): solver.Value(variables['A_O'][(i, k)]) for i in range(input_data["NoBatches"])
                              for k in input_data["Outputs"]}}

    def create_dataframe_binary(var_name, dim):
        data = []
        for k in input_data[dim]:
            rows = []
            for i in range(input_data["NoBatches"]):
                rows.append(solver.Value(variables[var_name][(i, k)]))
            data.append(rows)

        columns_ = ['Batch_{}'.format(i+1) for i in range(0, input_data["NoBatches"])]
        df = DataFrame(data=data, columns=columns_, index=input_data[dim])
        return df

    df_AI = create_dataframe_binary('A_I', 'Inputs')
    df_AO = create_dataframe_binary('A_O', 'Outputs')

    return df_integer, results_binary, df_AI, df_AO


if __name__ == "__main__":
    input_data = {
        "NoBatches": 10,
        "Inputs": ['IN1', 'IN2', 'IN3'],
        "Outputs": ['ROP1', 'ROP2', 'PAST1', 'PAST2'],
        "V": 10,
        "VMaxBuffer": 30,
        "Tin": {'IN1': int(10 / 10),  # 1
                'IN2': int(10 / 5),  # 2
                'IN3': int(10 / 2)},  # 5
        "Tout": {'ROP1': int(10 / 10),
                 'ROP2': int(10 / 5),
                 'PAST1': int(10 / 10),
                 'PAST2': int(10 / 5)},
        "Tmin": 0,
        "Tmax": 100000
    }

    model, variables = build_model(input_data_instance=input_data)
    solver, status = solve_model(model=model)
    df_integer, results_binary, df_AI, df_AO = build_response(solver=solver,
                                                              input_data=input_data,
                                                              variables=variables)

    print(df_integer)

    print(df_AI)

    print(df_AO)
