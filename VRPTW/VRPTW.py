from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from utils import write_json


def create_data_model(filename: str = None) -> dict:
    """Stores the data for the problem."""
    data = dict()
    # An array of travel times between locations. Note that this differs from previous examples, which use a distance
    # matrix. If all vehicles travel at the same speed, you will get the same solution if you use a distance matrix or
    # a time matrix, since travel distances are a constant multiple of travel times.
    data['time_matrix'] = [
        [0, 6, 9, 8, 7, 3, 6, 2, 3, 2, 6, 6, 4, 4, 5, 9, 7],
        [6, 0, 8, 3, 2, 6, 8, 4, 8, 8, 13, 7, 5, 8, 12, 10, 14],
        [9, 8, 0, 11, 10, 6, 3, 9, 5, 8, 4, 15, 14, 13, 9, 18, 9],
        [8, 3, 11, 0, 1, 7, 10, 6, 10, 10, 14, 6, 7, 9, 14, 6, 16],
        [7, 2, 10, 1, 0, 6, 9, 4, 8, 9, 13, 4, 6, 8, 12, 8, 14],
        [3, 6, 6, 7, 6, 0, 2, 3, 2, 2, 7, 9, 7, 7, 6, 12, 8],
        [6, 8, 3, 10, 9, 2, 0, 6, 2, 5, 4, 12, 10, 10, 6, 15, 5],
        [2, 4, 9, 6, 4, 3, 6, 0, 4, 4, 8, 5, 4, 3, 7, 8, 10],
        [3, 8, 5, 10, 8, 2, 2, 4, 0, 3, 4, 9, 8, 7, 3, 13, 6],
        [2, 8, 8, 10, 9, 2, 5, 4, 3, 0, 4, 6, 5, 4, 3, 9, 5],
        [6, 13, 4, 14, 13, 7, 4, 8, 4, 4, 0, 10, 9, 8, 4, 13, 4],
        [6, 7, 15, 6, 4, 9, 12, 5, 9, 6, 10, 0, 1, 3, 7, 3, 10],
        [4, 5, 14, 7, 6, 7, 10, 4, 8, 5, 9, 1, 0, 2, 6, 4, 8],
        [4, 8, 13, 9, 8, 7, 10, 3, 7, 4, 8, 3, 2, 0, 4, 5, 6],
        [5, 12, 9, 14, 12, 6, 6, 7, 3, 3, 4, 7, 6, 4, 0, 9, 2],
        [9, 10, 18, 6, 8, 12, 15, 8, 13, 9, 13, 3, 4, 5, 9, 0, 9],
        [7, 14, 9, 16, 14, 8, 5, 10, 6, 5, 4, 10, 8, 6, 2, 9, 0],
    ]
    # An array of time windows for the locations, which you can think of as requested times for a visit.
    # Vehicles must visit a location within its time window.
    data['time_windows'] = [
        (0, 5),    # depot
        (7, 12),   # 1
        (10, 15),  # 2
        (16, 18),  # 3
        (10, 13),  # 4
        (0, 5),    # 5
        (5, 10),   # 6
        (0, 4),    # 7
        (5, 10),   # 8
        (0, 3),    # 9
        (10, 16),  # 10
        (10, 15),  # 11
        (0, 5),    # 12
        (5, 10),   # 13
        (7, 8),    # 14
        (10, 15),  # 15
        (11, 15),  # 16
    ]
    # The number of vehicles in the fleet.
    data['num_vehicles'] = 5
    # The index of the depot (origin)
    data['depot'] = 0

    write_json(filename='./' + filename + '.json', dictionary=data)

    return data


def add_model_constraints(routing, data, manager, transit_callback_index):
    """
    The code creates a dimension for the travel time of the vehicles, similar to the dimensions for travel distance or
    demands in previous examples. Dimensions keep track of quantities that accumulate over a vehicle's route.
    In the code above, time_dimension.CumulVar(index) is the cumulative travel time when a vehicle arrives at the
    location with the given index.

    The dimension is created using the AddDimension method, which has the following arguments:

    The index for the travel time callback: transit_callback_index
    An upper bound for slack (the wait times at the locations): 30. While this was set to 0 in the CVRP example,
    the VRPTW has to allow positive wait time due to the time window constraints.
    An upper bound for the total time over each vehicle's route: 30
    A boolean variable that specifies whether the cumulative variable is set to zero at the start of each vehicle's route.
    The name of the dimension.

    """

    # Add Time Windows constraint.
    time = 'Time'
    # Methods to add dimensions to routes; dimensions represent quantities accumulated at nodes along the routes.
    routing.AddDimension(
        evaluator_index=transit_callback_index,  # evaluator_index
        slack_max=30,  # allow waiting time
        capacity=30,  # maximum time per vehicle
        fix_start_cumul_to_zero=False,  # Don't force start cumul to zero.
        name=time)
    time_dimension = routing.GetDimensionOrDie(time)  # Returns a dimension from its name

    # Add time window constraints for each location except depot.
    # It creates a dimension for the travel time of the vehicles
    # Dimensions keep track of quantities that accumulate over a vehicle's route
    # time_dimension.CumulVar(index) is the cumulative travel time when a vehicle arrives at the location with the
    # given index.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == data['depot']:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(l=time_window[0], u=time_window[1])

    # Add time window constraints for each vehicle start node.
    # Fix the time windows for the depot
    depot_idx = data['depot']
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(l=data['time_windows'][depot_idx][0],
                                                u=data['time_windows'][depot_idx][1])

    # Adds a variable to be minimized
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(var=time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(var=time_dimension.CumulVar(routing.End(i)))


def set_search_parameters():
    """
    Sets the default search parameters and a heuristic method for finding the first solution

    PATH_CHEAPEST_ARC: Starting from a route "start" node, connect it to the node which produces
    the cheapest route segment, then extend the route by iterating on the
    last node added to the route.

    PATH_MOST_CONSTRAINED_ARC: Same as PATH_CHEAPEST_ARC, but arcs are evaluated with a comparison-based
    selector which will favor the most constrained arc first

    EVALUATOR_STRATEGY: Same as PATH_CHEAPEST_ARC, except that arc costs are evaluated using the
    function passed to RoutingModel

    SAVINGS: Savings algorithm (Clarke & Wright).
    Reference: Clarke, G. & Wright, J.W.:
    "Scheduling of Vehicles from a Central Depot to a Number of Delivery
    Points"

    SWEEP: Sweep algorithm (Wren & Holliday).
    Reference: Anthony Wren & Alan Holliday: Computer Scheduling of Vehicles
    from One or More Depots to a Number of Delivery Points Operational
    Research Quarterly (1970-1977),
    Vol. 23, No. 3 (Sep., 1972), pp. 333-344


    CHRISTOFIDES: algorithm (actually a variant of the Christofides algorithm
    using a maximal matching instead of a maximum matching, which does
    not guarantee the 3/2 factor of the approximation on a metric travelling
    salesman). Works on generic vehicle routing models by extending a route
    until no nodes can be inserted on it.
    Reference: N Christofides, Worst-case analysis of a new heuristic for
    the travelling salesman problem, Report 388, Graduate School of
    Industrial Administration, CMU, 1976.


    ALL_UNPERFORMED:  insertion heuristics
    Make  nodes inactive. Only finds a solution if nodes are optional (are
    element of a disjunction constraint with a finite penalty cost).

    BEST_INSERTION: Iteratively build a solution by inserting the cheapest node at its
    cheapest position; the cost of insertion is based on the global cost
    function of the routing model. As of 2/2012, only works on models with
    optional nodes (with finite penalty costs).


    PARALLEL_CHEAPEST_INSERTION: Iteratively build a solution by inserting the cheapest node at its
    cheapest position; the cost of insertion is based on the arc cost
    function. Is faster than BEST_INSERTION.

    SEQUENTIAL_CHEAPEST_INSERTION: Iteratively build a solution by constructing routes sequentially, for
    each route inserting the cheapest node at its cheapest position until the
    route is completed; the cost of insertion is based on the arc cost
    function. Is faster than PARALLEL_CHEAPEST_INSERTION.

    LOCAL_CHEAPEST_INSERTION: Iteratively build a solution by inserting each node at its cheapest
    position; the cost of insertion is based on the arc cost function.
    Differs from PARALLEL_CHEAPEST_INSERTION by the node selected for
    insertion; here nodes are considered in decreasing order of distance to
    the start/ends of the routes, i.e. farthest nodes are inserted first.
    Is faster than SEQUENTIAL_CHEAPEST_INSERTION.

    LOCAL_CHEAPEST_COST_INSERTION: Same as LOCAL_CHEAPEST_INSERTION except that the cost of insertion is
    based on the routing model cost function instead of arc costs only.

    GLOBAL_CHEAPEST_ARC: Variable-based heuristics ---
    Iteratively connect two nodes which produce the cheapest route segment.

    LOCAL_CHEAPEST_ARC: Select the first node with an unbound successor and connect it to the
    node which produces the cheapest route segment.

    FIRST_UNBOUND_MIN_VALUE: Select the first node with an unbound successor and connect it to the
    first available node.
    This is equivalent to the CHOOSE_FIRST_UNBOUND strategy combined with
    ASSIGN_MIN_VALUE
    """
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    return search_parameters


def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f'Total cost: {solution.ObjectiveValue()}\n')
    time_dimension = routing.GetDimensionOrDie('Time')
    total_time = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle ({}):\n'.format(vehicle_id + 1)
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)
            plan_output += 'Node:{0} Time({1},{2}) -> '.format(manager.IndexToNode(index),
                                                               solution.Min(time_var),
                                                               solution.Max(time_var))
            index = solution.Value(routing.NextVar(index))
        # When the end is reached
        time_var = time_dimension.CumulVar(index)
        plan_output += 'Node:{0} Time({1},{2})\n'.format(manager.IndexToNode(index),
                                                         solution.Min(time_var),
                                                         solution.Max(time_var))
        plan_output += 'Time of the route: {} min\n'.format(solution.Min(time_var))
        print(plan_output)
        total_time += solution.Min(time_var)
    print('Total time of all routes: {}min'.format(total_time))


def main():
    """Solve the VRP with time windows."""
    # Instantiate the data problem.
    data = create_data_model('data\instance')

    # Create index manager (manager) and routing model
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),  # No. nodes/locations
                                           data['num_vehicles'],  # No. vehicles
                                           data['depot'])  # source index
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    # Set up call back
    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add problem constraints
    add_model_constraints(routing, data, manager, transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = set_search_parameters()

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print_solution(data, manager, routing, solution)


if __name__ == "__main__":
    main()

    # For each location on a route, Time(a,b) is the solution window: the vehicle that visits the location must do so
    # in that time interval to stay on schedule.

    # Route for vehicle (1):
    # Node:0 Time(0,0) -> Node:9 Time(2,3) -> Node:14 Time(7,8) -> Node:16 Time(11,11) -> 0 Time(18,18)
    # Time of the route: 18min

    # At location 9, the solution window is Time(2,3), which means the vehicle must arrive there between times 2 and 3.
    # Note that the solution window is contained in the constraint time window at that location, (0, 3), given in the
    # problem data. The solution window starts at time 2 because it takes 2 units of time
    # (the 0, 9 entry of the time matrix) to get from the depot to location 9.
    #
    # Why can the vehicle depart location 9 anytime between 2 and 3? The reason is that since the travel time from
    # location 9 to location 14 is 3, if the vehicle leaves anytime before 3, it will arrive at location 14 before time
    # 6, which is too early for its visit. So the vehicle has to wait somewhere, and if the driver wanted to, he or she
    # could wait at location 9 until time 3 without delaying completion of the route.
    #
    # You may have noticed that some solution windows (e.g. at locations 9 and 14) have different start and end times,
    # but others (e.g. on routes 2 and 3) have the same start and end time. In the former case, the vehicles can wait
    # until the end of the window before departing, while in the latter, they must depart as soon as they arrive.
