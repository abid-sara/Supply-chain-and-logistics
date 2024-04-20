from ChainAndLogistics import TransportProblem
from ChainAndLogistics import Node
import queue


def find_optimal_company_solution(problem, companies, search_strategy):
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
        solution = BFS_optimal_solution(problem, wilayas)
    if search_strategy == "UCS":
        solution = None  # replace it by the function
    if search_strategy == "A*":
        solution = a_star_helper(problem, wilayas)

    # get the company name that will transport the product
    if solution:
        company_name = companies[solution[0]]["company"]
    else:
        print("No solution found!")

    return company_name, solution


def breadth_first_search_helper(problem):
    frontier = queue.Queue()
    explored = []
    initial_node = Node(problem.state)
    frontier.put(initial_node)

    while not frontier.empty():
        node_chosen = frontier.get()
        if problem.is_goal_test(node_chosen):
            return node_chosen
        explored.append(node_chosen)
        children = problem.expand_node(node_chosen)
        for child in children:
            if child not in explored and child not in frontier.queue:
                frontier.put(child)
    return None


def breadth_first_search(problem, initial_states):
    """
    Performs breadth-first search (BFS) on the given problem starting from each city.

    Args:
    problem: The problem instance to solve using BFS.
    initial_states (list): A list of cities to start the search from.

    Returns:
    dict: A dictionary containing the solutions found for each initial state, along with their lengths.
          The keys are the initial states, and the values are dictionaries with "solution" and "length" lists.
    """
    setSol = {}
    for initial_state in initial_states:
        setSol[initial_state] = {"solution": [], "length": 0}
        problem.state = initial_state  # update the initial state
        sol = breadth_first_search_helper(problem)
        solution = problem.reconstruct_path(sol)
        if solution:  # If a solution is found, append it to the total solutions list with its length
            sol_length = len(solution)
            setSol[initial_state]["solution"] = solution
            setSol[initial_state]["length"] = sol_length
    return setSol


def BFS_optimal_solution(problem,
                         initial_states):  # Function to retrieve the best solution path from the solutions found for multiple initial states.
    setSol = breadth_first_search(problem, initial_states)
    optimal_solution = setSol[initial_states[0]]  # variable to store the best solution path

    # Compare the lengths of solutions found for each initial state to find the shortest solution
    for initial_state in initial_states:
        if setSol[initial_state]["length"] <= optimal_solution["length"] and setSol[initial_state]["length"] > 0:
            # Update the optimal_solution variable to store the solution with the shortest length.
            optimal_solution = setSol[initial_state]
    # we keep only the path of the solution
    optimal_solution = optimal_solution["solution"]
    return optimal_solution


# ucs starts here
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
            return node
        if node not in explored:
            explored.add(node.state)
            children = problem.expand_node(node)
            for child in children:
                if child.state not in explored:
                    # heapq.heappush(frontier, (child_cost, child))
                    frontier.append((child.cost, child))  # child node have accumulated cost its cost + parent cost (see expand_node function)

    return None


# informed search functions start here
def a_star_helper(problem, initial_states_product):
    best_path = None
    smallest_objective_value = float('inf')  # initialize it to the max value

    for possible_initial_state in initial_states_product:
        frontier = queue.PriorityQueue()
        explored = []
        root = Node(possible_initial_state)
        frontier.put((root.cost + problem.heuristic(root.state), root))

        while frontier:
            chosen_node = frontier.get()[1]
            if problem.is_goal_test(chosen_node):
                objective_value = chosen_node.cost + problem.heuristic(chosen_node.state)
                if objective_value < smallest_objective_value:  # if this is the smallest heuristic then it is the best root to take hence the best path solution is found
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
