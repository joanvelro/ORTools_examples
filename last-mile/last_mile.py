"""
Optimize E-Commerce Last-Mile Delivery with Python
Organize your routes to deliver parcels with a minimum number of drivers using optimization models with python

If you travel to first and second-tier cities of China, you will find on the street many delivery drivers

They take the parcels from small warehouses called customer service centres
located in each neighbourhood and deliver them to the final customers.

These centres are key elements of the Logistics Network of the major courier companies in China.
They provide a large geographical coverage for last-mile delivery and a huge competitive advantage by offering
the best service level and delivery lead time in the market.

Before arriving at your door, your parcel will be picked up from the vendor’s warehouse, transit through several
regional distribution centres and will finally arrive at the service centre of your neighbourhood.

When your parcel arrives at the centre, you will receive a notification on your phone to inform you that a courier
 will deliver your parcel during the day.

This article will present a solution to optimize the last-mile delivery from these centres to reduce the costs and
ensure a uniform distribution of the workload to each driver.

Problem Statement
You are a manager in a local service centre with

* 4 drivers in your team
* 15 parcel capacity per vehicle
* 16 destinations to cover in the neighbourhood named Dj with j in [1, 16]
* D0 is the centre
* 1 route per driver

https://www.samirsaci.com/optimize-e-commerce-last-mile-delivery-with-python/

Capacitated vehicle routing problem (CVRP) with Google OR-Tools

OR-Tools is an open-source collection of Google with tools for combinatorial optimization.
The objective is to find the best solution out of a very large set of possible solutions.

Let us try to use this library to build the optimal routes.

Conclusion
This model can help the centre manager to

Optimize his fleet with full utilization of his drivers and vehicles
Ensure that the workload is equally distributed among each driver
Question:

What could be the results with higher capacity (boxes) per driver?
What could be the results if we have a weight or volume constraint?
I let you test it and share your results (or questions) in the comment area.

"""
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp  # This struct holds all parameters for the default search.
import pandas as pd
import numpy as np



def load_data_from_excel(excel_file):
    # Import Distance Matrix
    df_distance = pd.read_excel(excel_file, index_col=0)

    # Transform to Numpy Array
    distance_matrix = df_distance.to_numpy()

    # Create dictionnary with data
    data = dict()
    data['DistanceMatrix'] = distance_matrix
    print("{:,} destinations".format(len(data['DistanceMatrix'][0]) - 1))

    # Orders quantity (Boxes)
    data['Demands'] = [0, 1, 1, 2, 4, 2, 4, 8, 8, 1, 2, 1, 2, 4, 4, 8, 8]
    # Vehicles Capacities (Boxes)
    data['VehiclesCapacity'] = [15, 15, 15, 15]
    # Fleet informations
    # Number of vehicles
    data['NoVehicles'] = 4
    # Location of the depot
    data['Depot'] = 0

    return data


# Create Dataframe of Matrix Distance
def create_excel(data):
    n_col = len(data['DistanceMatrix'][0])
    n_row = len(data['DistanceMatrix'])
    list_row = ['row' + str(i) for i in range(n_row)]
    list_col = ['col' + str(i) for i in range(n_row)]

    matrix = np.array(data['DistanceMatrix'])
    df = pd.DataFrame(data=matrix, index=list_row, columns=list_col)
    df.to_excel('df_distance_matrix.xlsx')


def distance_callback(from_index, to_index):
    """Returns the distance between the two nodes."""
    # Convert from routing variable Index to distance matrix NodeIndex.
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return data['DistanceMatrix'][from_node][to_node]


def demand_callback(from_index):
    """Returns the demand of the node."""
    # Convert from routing variable Index to demands NodeIndex.
    from_node = manager.IndexToNode(from_index)
    return data['Demands'][from_node]


def process_solution(solution):
    if solution:
        total_distance = 0
        total_load = 0
        print('\n')
        print('Routes')
        print('-'*25)
        for vehicle_id in range(data['NoVehicles']):
            index = routing.Start(vehicle_id)
            plan_output = 'Route for driver {}:\n'.format(vehicle_id)
            route_distance = 0
            route_load = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_load += data['Demands'][node_index]
                plan_output += '    Node({0})/Parcels({1}) -> '.format(node_index, route_load)
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id)
            plan_output += ' {0} Parcels({1})\n'.format(manager.IndexToNode(index),
                                                        route_load)
            plan_output += '\tDistance of the route: {} (m)\n'.format(route_distance)
            plan_output += '\tParcels Delivered: {} (parcels)\n'.format(route_load)
            print(plan_output)
            total_distance += route_distance
            total_load += route_load
        print('Total distance of all routes: {:,} (m)'.format(total_distance))
        print('Parcels Delivered: {:,}/{:,}'.format(total_load, sum(data['Demands'])))
    else:
        print('No Solution')


if __name__ == "__main__":
    data = load_data_from_excel(excel_file='df_distance_matrix.xlsx')

    # Create the routing index manager.
    # Manager for any NodeIndex <-> variable index conversion.The routing solver uses variable indices internally and
    # through its API.These variable indices are tricky to manage directly because one Node can correspond to a
    # multitude of variables, depending on the number of times they appear in the model, and if they're used as start
    # and/or end points. This class aims to simplify variable index usage, allowing users to use NodeIndex instead.
    manager = pywrapcp.RoutingIndexManager(len(data['DistanceMatrix']),
                                           data['NoVehicles'],
                                           data['Depot'])

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint.
    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_callback_index,
                                            0,  # null capacity slack
                                            data['VehiclesCapacity'],  # vehicle maximum capacities
                                            True,  # start cumul to zero
                                            'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.FromSeconds(1)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    process_solution(solution)
