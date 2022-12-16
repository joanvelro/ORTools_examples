from ortools.sat.python import cp_model
import pandas

number_batches = 10
inputs = ['IN1', 'IN2', 'IN3']
outputs = ['ROP1', 'ROP2', 'PAST1', 'PAST2']
V = 10
V_max_buffer = 30
T_in = {'IN1': int(V / 10),
        'IN2': int(V / 5),
        'IN3': int(V / 2)}
T_out = {'ROP1': int(V / 10),
         'ROP2': int(V / 5),
         'PAST1': int(V / 10),
         'PAST2': int(V / 5)}

t_min = 0
t_max = 100000

model = cp_model.CpModel()

A_I = {(i, k): model.NewBoolVar('')
       for i in range(number_batches)
       for k in inputs}

for i in range(number_batches):
    model.Add(sum(A_I[(i, k)] for k in inputs) == 1)

A_O = {(i, k): model.NewBoolVar('')
       for i in range(number_batches)
       for k in outputs}

for i in range(number_batches):
    model.Add(sum(A_O[(i, k)] for k in outputs) == 1)

S_INPUT = {i: model.NewIntVar(t_min, t_max, '')
           for i in range(number_batches)}
S_BUFFER = {i: model.NewIntVar(t_min, t_max, '')
            for i in range(number_batches)}
S_OUTPUT = {i: model.NewIntVar(t_min, t_max, '')
            for i in range(number_batches)}
D_INPUT = {i: model.NewIntVar(t_min, t_max, '')
           for i in range(number_batches)}
D_BUFFER = {i: model.NewIntVar(1, t_max, '')
            for i in range(number_batches)}
D_OUTPUT = {i: model.NewIntVar(t_min, t_max, '')
            for i in range(number_batches)}
for i in range(number_batches):
    for k in inputs:
        model.Add(D_INPUT[i] == T_in[k]).OnlyEnforceIf(A_I[i, k])
    for k in outputs:
        model.Add(D_INPUT[i] == T_out[k]).OnlyEnforceIf(A_O[i, k])

E_INPUT = {i: model.NewIntVar(t_min, t_max, '')
           for i in range(number_batches)}
E_BUFFER = {i: model.NewIntVar(t_min, t_max, '')
            for i in range(number_batches)}
E_OUTPUT = {i: model.NewIntVar(t_min, t_max, '')
            for i in range(number_batches)}
B_INPUT = {i: model.NewIntervalVar(S_INPUT[i], D_INPUT[i], E_INPUT[i], '')
           for i in range(number_batches)}
B_BUFFER = {i: model.NewIntervalVar(S_BUFFER[i], D_BUFFER[i], E_BUFFER[i], '')
            for i in range(number_batches)}
B_OUTPUT = {i: model.NewIntervalVar(S_OUTPUT[i], D_OUTPUT[i], E_OUTPUT[i], '')
            for i in range(number_batches)}
V_BUFFER_1 = {i: model.NewIntVar(0, V_max_buffer, '')
              for i in range(number_batches)}
V_BUFFER_2 = {i: model.NewIntVar(0, V_max_buffer, '')
              for i in range(number_batches)}
V_BUFFER = {i: model.NewIntervalVar(V_BUFFER_1[i], V, V_BUFFER_2[i], '')
            for i in range(number_batches)}

for i in range(number_batches):
    model.Add(S_BUFFER[i] == E_INPUT[i])
    model.Add(S_OUTPUT[i] == E_BUFFER[i])

model.AddNoOverlap2D(B_BUFFER.values(), V_BUFFER.values())

model.Minimize(E_BUFFER[number_batches - 1])

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    print('ole')
elif status == cp_model.FEASIBLE:
    print('feasible')

df = pandas.DataFrame({
    'bin': [solver.Value(V_BUFFER_1[i]) for i in range(number_batches)],
    'time': [solver.Value(E_BUFFER[i]) for i in range(number_batches)]
})
print(df)
