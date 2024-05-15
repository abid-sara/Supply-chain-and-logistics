import math
from supply_chain_system.ChainAndLogistics import TransportProblem
from supply_chain_system.ChainAndLogistics import Node
import queue


def select_best_company_path(problem, companies, distance, strategy):
    """
    Selects the best company based on a given uninfromed strategy (BFS or UCS) to minimize cost and time.

    Args:
        problem: The transportation problem.
        companies: Dictionary containing information about available companies.
        distance: Distance from the source city to the goal city.
        strategy: Strategy for selecting the company (BFS or UCS).

    Returns:
        Tuple containing the name of the best company, its solution path, price, and time.
    """
    wilayas = list(companies.keys())
    
    if strategy == "BFS":
        solution_set = breadth_first_search(problem, wilayas)
    elif strategy == "UCS":
        solution_set= uniform_cost_search(problem, wilayas)
    else:
        print("Invalid strategy")
        
    #add the distance from the source city to the goal city to each solution in the solution set obtained
    for wilaya in solution_set:
        solution_set[wilaya]["distance travelled"] += distance 
    
    #update the price of each company based on the distance travelled 
    for wilaya in solution_set.keys():
        price = float(companies[wilaya]["price"])
        distance_travelled = float(solution_set[wilaya]["distance travelled"])
        num_of_trips = int(companies[wilaya]["number of trips needed"])
        #update the price
        if distance_travelled==0:
            companies[wilaya]["price"] = price 
            time_spent = num_of_trips
        else:
            companies[wilaya]["price"] = price * distance
            time_spent = distance_travelled * num_of_trips
        
        #add the solution path of each company in the dict + the whole time spent
        companies[wilaya]["solution"] = solution_set[wilaya]["solution"]
        companies[wilaya]["time"] = time_spent
    
    #find the company with the lowest price and time
    company_with_min_cost = min(companies.items(), key=lambda x: x[1]["price"]) #company with the lowest price
    company_with_min_time = min(companies.items(), key=lambda x: x[1]["time"]) #company with the lowest time 
    
    best_company = None #variable to store the best company
    
    ''' Compare the prices and time of the best companies to determine the best option '''
    
    if company_with_min_cost == company_with_min_time: #if we found a company that has both the lowest time and cost
        best_company = company_with_min_cost
    else:
        costs = [company_with_min_cost[1]["price"], company_with_min_time [1]["price"]]
        min_cost = min(costs)
        max_cost = max(costs)
        cost_diff = max_cost - min_cost
        cost_percentage = (cost_diff / min_cost) * 100 if min_cost != 0 else 0

        # Decision based on the cost difference percentage
        if cost_percentage > 10:
            # Prioritize the lowest cost if the difference is significant
            best_company =  company_with_min_cost
        else:
            # Prioritize the lowest time if the cost difference is not significant
            # if we find multiple companies with the lowest time unit possible which is 1, use the cost as a second comparison criteria
            best_company = company_with_min_time       


    company_name = companies[best_company[0]]["company"]
    best_path = companies[best_company[0]]["solution"]
    best_price = companies[best_company[0]]["price"]
    best_time = companies[best_company[0]]["time"]
    best_cost= solution_set[best_company[0]]["distance travelled"]
    # print("here company select")
    # print(company_name ,' ',best_path,' ',best_price,' ',best_time,' ',best_cost)
    return company_name, best_path, best_price, best_time,best_cost
    

def find_optimal_company_solution(problem, companies, search_strategy, product, quantity):
    """
    Find the most optimal company location based on the given search strategy.

    Args:
    problem: The problem instance.
    companies (dict): A dictionary containing information about companies and their locations.
    search_strategy (str): The search strategy to use ("BFS", "UCS", "A*").

    Returns:
    tuple: A tuple containing the name of the company and the most optimal solution path.
    """
    # get only the wilayas
    wilayas = list(companies.keys())
    solution = None  # the solution path
    # get the solution path based on the search strategy given
    if search_strategy == "BFS":
        solution = select_best_company_path(problem, wilayas)
    if search_strategy == "UCS":
        solution, min_cost = UCS_shortest_path_from_source_city(problem, wilayas)  # replace it by the function UCS_optimal_solution(
    if search_strategy == "A*":
        # call find truck city heuristic get the wilaya and find the path
        wilaya, company_name, costMoney, costTime = find_truck_city_heuristic(problem, product, quantity)
        solution = a_star_helper(problem, wilaya, "one")

    elif search_strategy == "hill_climbing":
        # call find truck city heuristic get the wilaya and find the path
        wilaya, company_name, costMoney, costTime = find_truck_city_heuristic(problem, product, quantity)
        solution = hill_climbing(problem, wilaya, "one")

        # get the company name that will transport the product
    if solution:
        company_name = companies[solution[0]]["company"]
    else:
        print("No solution found!")
    if search_strategy == "BFS":
        return company_name, solution, min_cost
    if search_strategy == "UCS":
        return company_name, solution, min_cost
    if search_strategy == "A*":
        return company_name, solution, costMoney, costTime
    if search_strategy == "hill_climbing":
        return company_name, solution,costMoney, costTime 
    return company_name, solution


def breadth_first_search_helper(problem):
    """
        This function takes a problem and performs bfs on its states 
    """
    frontier = queue.Queue()
    explored = []
    initial_node = Node(problem.state)
    frontier.put((initial_node.cost, initial_node))

    while not frontier.empty():
        cost, node_chosen = frontier.get()
        if problem.is_goal_test(node_chosen):
            return node_chosen
        explored.append(node_chosen)
        children = problem.expand_node(node_chosen)
        for child_node in children:
            if child_node not in explored:
                frontier.put((child_node.cost, child_node))
    return None


def breadth_first_search(problem, initial_states):
    """
    Performs breadth-first search (BFS) on the given problem starting from each city.

    Args:
    problem: The problem instance to solve using BFS.
    initial_states (list): A list of cities to start the search from.

    Returns:
    dict: A dictionary containing the solutions found for each initial state, along with their costs.
          The keys are the initial states, and the values are dictionaries with "solution" and "distance travelled" lists.
    """
    setSol = {}
    for initial_state in initial_states:
        setSol[initial_state] = {"solution": [], "distance travelled": 0}
        problem.state = initial_state  # update the initial state
        sol = breadth_first_search_helper(problem)
        distance = sol.cost
        solution = problem.reconstruct_path(sol)
        if solution:  # If a solution is found, append it to the total solutions list with its cost
            setSol[initial_state]["solution"] = solution
            setSol[initial_state]["distance travelled"] = distance
    return setSol


def BFS_shortest_path_from_source_city(problem, initial_states): 
    '''
        problem : instance of the problem
        initial_states: possible initial states to which we performed bfs
     Function to retrieve the best solution path from the solutions found for multiple initial states.
    ''' 

    setSol = breadth_first_search(problem, initial_states)
    optimal_solution = setSol[initial_states[0]]  # variable to store the best solution path
    
    # Compare the lengths of solutions found for each initial state to find the shortest solution
    for initial_state in initial_states:
        if setSol[initial_state]["distance travelled"] <= optimal_solution["distance travelled"] and setSol[initial_state]["distance travelled"] > 0:
            # Update the optimal_solution variable to store the solution with the shortest length.
            optimal_solution = setSol[initial_state]
    # we keep only the path of the solution
    solution = optimal_solution["solution"]
    distance_travelled = optimal_solution["distance travelled"]
    return solution, distance_travelled


def ucs_helper(problem):
    frontier = []
    explored = set()
    initial_node = Node(problem.state)
  
    frontier.append((initial_node.cost, initial_node))  # Initial node with cost 0
    '''The frontier is implemented as a priority queue using the heapq module in Python. This ensures that the node with the smallest cumulative cost is always popped from the frontier first.'''

    while frontier:
        frontier.sort(key=lambda x: x[0])  # Sort the frontier by cost
        current_cost, node = frontier.pop(0)  # Pop the node with the lowest cost
        # current_cost, node = heapq.heappop(frontier)
        if problem.is_goal_test(node):
          #  print('ucshelper ', current_cost)
            return node,current_cost
        if node not in explored:
            explored.add(node.state)
            children = problem.expand_node(node)
            for child in children:
                if child.state not in explored:
                    # heapq.heappush(frontier, (child_cost, child))
                    frontier.append((child.cost, child))  # child node have accumulated cost its cost + parent cost (see expand_node function)

    return None,None


def uniform_cost_search(problem, initial_states):
    setSol={}
    solutions = []
    for initial_state in initial_states:
        setSol[initial_state] = {"solution": [], "distance travelled": 0}
        problem.state = initial_state #update the initial state
        solution_node,cost = ucs_helper(problem)
        if solution_node:
            solution_path = []
            node = solution_node
            while node:
                solution_path.insert(0, node.state)
                node = node.parent
            # solution_path.reverse()
            solutions.append(solution_path)
            setSol[initial_state]["solution"] = solution_path
            setSol[initial_state]["distance travelled"] = cost
           # print('here ucs cost search', setSol[initial_state]["distance travelled"] )
    return setSol


def UCS_shortest_path_from_source_city(problem, initial_states):
    
    setSol = uniform_cost_search(problem, initial_states)
    #print('here ucs_shortest ', setSol)
    min_cost = float('inf')
    min_path = None  # path from source city to user wilaya
    for initial_state in initial_states:
        cost = setSol[initial_state]["distance travelled"]  # access the cost stored in setSol dictionary
        
        # print("from shorteeest ucs ")
        # print(min_cost)
        if cost < min_cost:
            min_cost = cost
            min_path = setSol[initial_state]# Convert the path to a list of states

            # Since each (path, cost) corresponds to a specific initial_state in setSol,
            # we don't need to track the initial_state here directly.
        # min_initial_state = min_path[0]  # Assuming path is not empty
    
    solution = min_path["solution"]
    return solution, min_cost


def a_star_helper(problem, initial_states_product, parameter):
    """
    problem:
    initial_states_product: possible source cities, or company cities
    parameter: indicates if we have a single initial state or not
    return: path of the solution
        This function is the usual a star, but we have multiple path
        so along the search we keep the best path only
    """

    best_path = None
    smallest_objective_value = float('inf')  # initialize it to the max value

    frontier = queue.PriorityQueue()
    explored = []

    if parameter == 'one': #if there is only one initial state
        initial_state = initial_states_product
        root = Node(initial_state)
        frontier.put((root.cost + problem.heuristic(root.state), root))
    else: #if we have multiple initial states
        for possible_initial_state in initial_states_product:
            root = Node(possible_initial_state)
            frontier.put((root.cost + problem.heuristic(root.state), root))

    while frontier:
        chosen_node = frontier.get()[1]
        if problem.is_goal_test(chosen_node):
            objective_value = chosen_node.cost + problem.heuristic(chosen_node.state)
            if objective_value < smallest_objective_value:
                smallest_objective_value = objective_value
                explored.append(chosen_node)
                best_path = problem.reconstruct_path(chosen_node)  # Reconstruct the path
            break

        explored.append(chosen_node)
        children = problem.expand_node(chosen_node)

        for child in children:
            if child not in explored and child.state not in [n[1].state for n in frontier.queue]:
                frontier.put((child.cost + problem.heuristic(child.state), child))

    return best_path


def hill_climbing_search(problem):
    current_node = Node(problem.state)
    best_path = None
    best_length = float('inf')  # Initialize the best length to infinity

    while True:
        neighbors = problem.expand_node(current_node)
        if not neighbors:
            best_path = problem.reconstruct_path(current_node)
            best_length = len(best_path)
            return best_path, best_length
        best_neighbor = min(neighbors, key=lambda n: problem.heuristic(n.state))

        if problem.heuristic(best_neighbor.state) >= problem.heuristic(current_node.state):
            best_path = problem.reconstruct_path(current_node)
            best_length = len(best_path)
            return best_path, best_length
        else:
            current_node = best_neighbor
            if problem.is_goal_test(current_node):
                best_path = problem.reconstruct_path(current_node)
                best_length = len(best_path)
                return best_path, best_length
        return [], 0  # Return an empty path and length 0 if no solution is found


def hill_climbing(problem, initial_states, param):
    if param == 'one':
        # if there is a single initial state
        problem.state = initial_states
        solution, length = hill_climbing_search(problem)
        print("sol one param: ", solution)
        return solution
    else:
        # If there are multiple initial states to start from
        setSolutions = {}
        for initial_state in initial_states:
            setSolutions[initial_state] = {"solution": [], "length": 0}
            problem.state = initial_state
            solution, length = hill_climbing_search(problem)  # Modified to return both solution and length
            setSolutions[initial_state]["solution"] = solution
            setSolutions[initial_state]["length"] = length

        best_root = min(initial_states, key=lambda state: problem.heuristic(state))
        optimal_solution = setSolutions[best_root]
        return optimal_solution["solution"]

    

def find_truck_city_heuristic(problem, product, quantity):
    """
    :param problem:  takes the problem
    :param product: product we want to ship
    :param quantity: quantity we want to ship
    :return: a city of the company that has the trucks for transportation
        this function will loop through the possible companies to transport the product, then chooses one company based on the
        following conditions:
        find a company that has both the smallest cost and time unit (suppose that a time unit is the number of trips required
        based on the capacity of the company)
        else calculate the percentage of difference between the costs of different companies and then
        chose one company according to the time or the cost
    """

    elements = problem.find_company(product, quantity)  # dictionary wilaya: {company, #of trips, price}
    results = []  # set of tuples (wilaya,company, the estimated cost,time)
    print(elements)
    for wilaya, details in elements.items():
        print("wilaya: ", wilaya)
        price = details["price"]
        print("price: ", price)
        estimated_distance = problem.heuristic(wilaya)
        wilaya_Node = Node(wilaya)  # create a node to test if the wilaya is a goal node, if so then put the estimated distance as 1 not 0 (because logically the company will not do the transportation for free)
        if problem.is_goal_test(wilaya_Node):
            estimated_distance = 1
        print("estimated distance: ", estimated_distance)
        estimated_cost = estimated_distance * price
        print("estimated cost: ", estimated_cost)
        estimated_time = details["number of trips needed"]
        print("estimated time: ", estimated_time)
        results.append((wilaya, details["company"], estimated_cost, estimated_time))

    # now find the company that has the lowest cost and the lowest time if found
    result_cost = min(results, key=lambda x: x[2])
    result_time = min(results, key=lambda x: x[3])
    if result_time == result_cost:  # if we found a company that has both the lowest time and cost return it
        return result_time
    else:  # calculate the percentage to see the difference of costs between the cities
        costs = [result[2] for result in results]
        max_cost = max(costs)  # take the maximum cost in the set
        min_cost = min(costs)  # take the minimum cost in the set
        cost_diff = max_cost - min_cost
        cost_percentage = (cost_diff / min_cost) * 100 if min_cost != 0 else 0

        # Decision based on the cost difference percentage
        if cost_percentage > 10:
            # Prioritize the lowest cost if the difference is significant
            best_option = min(results, key=lambda x: x[2])
        else:
            # Prioritize the lowest time if the cost difference is not significant
            # if we find multiple companies with the lowest time unit possible which is 1, use the cost as a second comparison criteria
            best_option = min(results, key=lambda x: (x[3], x[2]))
        return best_option


state_transition_model = {}
with open('supply_chain_system/data/wilaya_frontiere.txt', 'r') as file:
    for line in file:
        city_coord, neighbors_string = line.strip().split(': ')
        city, coordinates_string = city_coord.strip().split(',', 1)
        coordinates = tuple(float(coord) for coord in coordinates_string.strip('()').split(', '))
        state_transition_model[city] = {
            "coordinates": coordinates,
            "neighbors": {}
        }
        for neighbor_info in neighbors_string.split(', '):
            neighbor_city, distance_str = neighbor_info.split('; ')
            distance = float(distance_str)
            state_transition_model[city]["neighbors"][neighbor_city] = distance
            