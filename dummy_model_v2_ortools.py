from ortools.sat.python import cp_model
import copy

"""
Modelo dummy de un caso del ejemplo 8 de los workflows del excel con una 
receta dada de pasteurizacion, 1 tanque de producto inicial, 2 tanques de 
producto de destino y 2 pasteurizadores a elegir. (Debería haber soluciones
con solo 1 pasteurizador y con 2 pasteurizadores. Incluiremos CIPs más 
adelante.
"""


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, graph_indicator):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0
        self.__graph_indicator = graph_indicator

    def solution_count(self):
        return self.__solution_count

    def on_solution_callback(self):
        self.__solution_count += 1
        print("--------------------------------------------")
        print("Solucion " + str(self.__solution_count))
        print("Grafo 1: " + str(self.Value(self.__graph_indicator[0])) +
              " ; Grafo 2: " + str(self.Value(self.__graph_indicator[1])))


def transform_graphs(list_of_dict):
    temp = copy.deepcopy(list_of_dict)
    for g in temp:
        for m, n in g:
            if g[m, n] != 0:
                g[m, n] = 1
    return temp


# Diccionario del workflow (Esto se leerá del .json)
workflow = {
    ("area A", "area A"): 0,
    ("area A", "area B"): 0,
    ("area A", "area C"): 0,
    ("area A", "pasteurizer"): "SS",
    ("area B", "area A"): 0,
    ("area B", "area B"): 0,
    ("area B", "area C"): 0,
    ("area B", "pasteurizer"): 0,
    ("area C", "area A"): 0,
    ("area C", "area B"): 0,
    ("area C", "area C"): 0,
    ("area C", "pasteurizer"): 0,
    ("pasteurizer", "area A"): 0,
    ("pasteurizer", "area B"): "SS",
    ("pasteurizer", "area C"): "SS",
    ("pasteurizer", "pasteurizer"): 0,
}

# El reader deberia producir, a partir de este diccionario, 2 grafos con las
# combinaciones de equipamiento posibles (2 en este caso)

graph_list = [{
    ("Tank A", "Tank A"): 0,
    ("Tank A", "Tank B"): 0,
    ("Tank A", "Tank C"): 0,
    ("Tank A", "Pasteurizer 1"): "SS",
    ("Tank A", "Pasteurizer 2"): 0,
    ("Tank B", "Tank A"): 0,
    ("Tank B", "Tank B"): 0,
    ("Tank B", "Tank C"): 0,
    ("Tank B", "Pasteurizer 1"): 0,
    ("Tank B", "Pasteurizer 2"): 0,
    ("Tank C", "Tank A"): 0,
    ("Tank C", "Tank B"): 0,
    ("Tank C", "Tank C"): 0,
    ("Tank C", "Pasteurizer 1"): 0,
    ("Tank C", "Pasteurizer 2"): 0,
    ("Pasteurizer 1", "Tank A"): 0,
    ("Pasteurizer 1", "Tank B"): "SS",
    ("Pasteurizer 1", "Tank C"): "SS",
    ("Pasteurizer 1", "Pasteurizer 1"): 0,
    ("Pasteurizer 1", "Pasteurizer 2"): 0,
    ("Pasteurizer 2", "Tank A"): 0,
    ("Pasteurizer 2", "Tank B"): 0,
    ("Pasteurizer 2", "Tank C"): 0,
    ("Pasteurizer 2", "Pasteurizer 1"): 0,
    ("Pasteurizer 2", "Pasteurizer 2"): 0
},
    {
        ("Tank A", "Tank A"): 0,
        ("Tank A", "Tank B"): 0,
        ("Tank A", "Tank C"): 0,
        ("Tank A", "Pasteurizer 1"): 0,
        ("Tank A", "Pasteurizer 2"): "SS",
        ("Tank B", "Tank A"): 0,
        ("Tank B", "Tank B"): 0,
        ("Tank B", "Tank C"): 0,
        ("Tank B", "Pasteurizer 1"): 0,
        ("Tank B", "Pasteurizer 2"): 0,
        ("Tank C", "Tank A"): 0,
        ("Tank C", "Tank B"): 0,
        ("Tank C", "Tank C"): 0,
        ("Tank C", "Pasteurizer 1"): 0,
        ("Tank C", "Pasteurizer 2"): 0,
        ("Pasteurizer 1", "Tank A"): 0,
        ("Pasteurizer 1", "Tank B"): 0,
        ("Pasteurizer 1", "Tank C"): 0,
        ("Pasteurizer 1", "Pasteurizer 1"): 0,
        ("Pasteurizer 1", "Pasteurizer 2"): 0,
        ("Pasteurizer 2", "Tank A"): 0,
        ("Pasteurizer 2", "Tank B"): "SS",
        ("Pasteurizer 2", "Tank C"): "SS",
        ("Pasteurizer 2", "Pasteurizer 1"): 0,
        ("Pasteurizer 2", "Pasteurizer 2"): 0,
    }
]

demand = {
    "product_name": "product B",
    "date": "20/02/2022",
    "amount": 30000
}

equipment_list = ["Start Batch", "Tank A", "Tank B", "Tank C",
                  "Pasteurizer 1: Warmup",
                  "Pasteurizer 1: Processing", "Pasteurizer 1: Shutdown",
                  "Pasteurizer 2: Warmup", "Pasteurizer 2: Processing",
                  "Pasteurizer 2: Shutdown"]

# El graph list anterior habría que expandirlo con el pasteurizer graph para
# que resulte el siguiente grafo

graph_list = [
    {(m, n): 0 for m in equipment_list for n in equipment_list},
    {(m, n): 0 for m in equipment_list for n in equipment_list}
]

graph_list[0]["Start Batch", "Pasteurizer 1: Warmup"] = "SS"
graph_list[0]["Tank A", "Pasteurizer 1: Processing"] = "SS"
graph_list[0]["Pasteurizer 1: Warmup", "Pasteurizer 1: Processing"] = "FS"
graph_list[0]["Pasteurizer 1: Processing", "Pasteurizer 1: Shutdown"] = "FS"
graph_list[0]["Pasteurizer 1: Processing", "Tank B"] = "SS"
graph_list[0]["Pasteurizer 1: Processing", "Tank C"] = "SS"

graph_list[1]["Start Batch", "Pasteurizer 2: Warmup"] = "SS"
graph_list[1]["Tank A", "Pasteurizer 2: Processing"] = "SS"
graph_list[1]["Pasteurizer 2: Warmup", "Pasteurizer 2: Processing"] = "FS"
graph_list[1]["Pasteurizer 2: Processing", "Pasteurizer 2: Shutdown"] = "FS"
graph_list[1]["Pasteurizer 2: Processing", "Tank B"] = "SS"
graph_list[1]["Pasteurizer 2: Processing", "Tank C"] = "SS"

# Esto habría que calcularlo de alguna forma, en este caso es la demanda

batch_size = {("workflow 1", "recipe 1"): 30000}
number_batches = {("workflow 1", "recipe 1"): 1}
flow_rate = 20000 / 3600

# This is read from the recipe

pasteurizer_input = {"product A": 1}
pasteurizer_output = {"product B": 0.3,
                      "product C": 0.7}

# this would be read from the recipe

pasteurizer_utilities = {
    ("Warmup", "Duration"): 15000,
    ("Warmup", "Power"): 20,
    ("Warmup", "Steam"): 0,
    ("Warmup", "Water"): 0,
    ("Warmup", "Chilled Water"): 10,
    ("Warmup", "Air"): 4,
    ("Processing", "Duration"): batch_size["workflow 1", "recipe 1"] /
                                flow_rate,  # Esto habría que afinarlo
    ("Processing", "Power"): 30,
    ("Processing", "Steam"): 0,
    ("Processing", "Water"): 0,
    ("Processing", "Chilled Water"): 25,
    ("Processing", "Air"): 6,
    ("Shutdown", "Duration"): 20000,
    ("Shutdown", "Power"): 25,
    ("Shutdown", "Steam"): 0,
    ("Shutdown", "Water"): 0,
    ("Shutdown", "Chilled Water"): 5,
    ("Shutdown", "Air"): 5,
}

pasteurizer_graph = {
    ("Warmup", "Warmup"): 0,
    ("Warmup", "Processing"): "FS",
    ("Warmup", "Shutdown"): 0,
    ("Processing", "Warmup"): 0,
    ("Processing", "Processing"): 0,
    ("Processing", "Shutdown"): "FS",
    ("Shutdown", "Warmup"): 0,
    ("Shutdown", "Processing"): 0,
    ("Shutdown", "Shutdown"): 0,
}

# Esto tiene que ser una variable, si no nunca compensa conectar 2 past.

time_of_step_lookup = {
    "Start Batch": 0,
    "Tank A": 0,
    "Tank B": 0,
    "Tank C": 0,
    "Pasteurizer 1: Warmup": 15000,
    "Pasteurizer 1: Processing": "Variable",
    "Pasteurizer 1: Shutdown": 20000,
    "Pasteurizer 2: Warmup": 15000,
    "Pasteurizer 2: Processing": "Variable",
    "Pasteurizer 2: Shutdown": 20000,
}

# Esto saldría del date de la demanda

time_horizon = 33002

graph_list_num = transform_graphs(graph_list)

maximum_graph = {(m, n): sum(g[m, n] for g in graph_list_num) for m in
                 equipment_list for n in equipment_list}

for m, n in maximum_graph:
    if maximum_graph[m, n] >= 1:
        maximum_graph[m, n] = 1

model = cp_model.CpModel()

graph_indicator = {k: model.NewBoolVar('') for k in range(len(graph_list))}

model.Add(sum(graph_indicator[k] for k in range(len(graph_list))) >= 1)

graph = {(m, n): model.NewBoolVar('') for m in equipment_list
         for n in equipment_list}
for m in equipment_list:
    for n in equipment_list:
        model.Add(graph[m, n] == maximum_graph[m, n]).OnlyEnforceIf(
            [graph_indicator[0], graph_indicator[1]])
        model.Add(graph[m, n] == graph_list_num[0][m, n]).OnlyEnforceIf(
            [graph_indicator[0], graph_indicator[1].Not()])
        model.Add(graph[m, n] == graph_list_num[1][m, n]).OnlyEnforceIf(
            [graph_indicator[1], graph_indicator[0].Not()])

process_start = {(m, n): model.NewIntVar(0, time_horizon, '') for
                 m in equipment_list for n in equipment_list}

# Hacemos el time step variable

time_of_step = {m: model.NewIntVar(0, time_horizon, '') for
                m in equipment_list}

for m in equipment_list:
    if time_of_step_lookup[m] != "Variable":
        model.Add(time_of_step[m] == time_of_step_lookup[m])
    else:
        model.Add(time_of_step[m] == 18000).OnlyEnforceIf(
            [graph_indicator[0].Not(), graph_indicator[1]])
        model.Add(time_of_step[m] == 18000).OnlyEnforceIf(
            [graph_indicator[0], graph_indicator[1].Not()])
        model.Add(time_of_step[m] == 17995).OnlyEnforceIf(
            [graph_indicator[0], graph_indicator[1]])

        # Hay que ver como meter la division. Esto hay que refinarlo de todas
        # formas.

# Para esto hay que ver bien como usar las IntervalVar.

for m in equipment_list:
    for n in equipment_list:
        if graph_list[0][m, n] == "SS" or graph_list[1][m, n] == "SS":
            for l in equipment_list:
                model.Add(process_start[m, n] == process_start[l, m]
                          ).OnlyEnforceIf([graph[m, n], graph[l, m]])
        elif graph_list[0][m, n] == "FS" or graph_list[1][m, n] == "FS":
            for l in equipment_list:
                model.Add(process_start[m, n] == process_start[l, m] +
                          time_of_step[m]).OnlyEnforceIf([graph[m, n],
                                                          graph[l, m]])
        model.Add(process_start[m, n] == 0).OnlyEnforceIf(graph[m, n].Not())

solver = cp_model.CpSolver()
solution_printer = SolutionPrinter(graph_indicator)
solver.parameters.enumerate_all_solutions = True
status = solver.Solve(model, solution_printer)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print('At least 1 solution')
    solution = {(m, n): solver.Value(process_start[m, n]) for
                m in equipment_list for n in equipment_list}
    # print(solution)
else:
    print('No solution found.')

# PENDIENTE REAJUSTE PARA MÁS DE 1 BATCH, PARA MÁS DE UNA RECETA.