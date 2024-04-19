from ChainAndLogistics import TransportProblem
from ChainAndLogistics import Node
import queue


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
    setSol = []
    for initial_state in initial_states:
        print("initial state: ", initial_state)
        problem.state = initial_state  # update the initial state
        node = breadth_first_search_helper(problem)
        sol = problem.reconstruct_path(node)
        if sol:  # if solution exists append it to the total solutions list
            setSol.append(sol)
    return setSol


# ucs starts here
def ucs_helper(problem, initial_state):
    """Uniform Cost Search algorithm"""
    frontier = [(0, initial_state, [(initial_state, 0)])]  # (total_cost, state, path)
    explored = {}  # Explored nodes and their costs

    while frontier:
        # Sort the frontier by total_cost
        frontier.sort(key=lambda x: x[0])
        # Get the node with the lowest cost
        total_cost, node, path = frontier.pop(0)
        if problem.is_goal_test(Node(node)):  # Check if the current node is the goal state
            return path, total_cost

        # Check if the node has already been explored or if the new path has a lower cost
        if node not in explored or total_cost < explored[node][0]:
            explored[node] = (total_cost, path)  # This ensures that the algorithm keeps track of the lowest-cost path to each explored state.

            # Retrieve neighbors and their costs from the problem
            children = problem.expand_node(Node(node))

            for child in children:
                new_total_cost = total_cost + child.cost
                new_path = path + [(child.state, child.cost)]
                child_node = (new_total_cost, child.state, new_path)
                frontier.append(child_node)

    return None, 0  # return path, total_cost and returns (None, 0) if no solution is found


def ucs(problem, initial_states):
    solution_set = set()
    for initial_state in initial_states:
        solution, total_cost = ucs_helper(problem, initial_state)
        solution = tuple(solution)
        if solution:
            solution_set.add((solution, total_cost))
    return solution_set
#ucs finishes here


# informed search functions start here
def a_star_helper(problem, initial_states_product):
    best_path = None
    smallest_objective_value = float('inf')  # initialize it to the max value

    for possible_initial_state in initial_states_product:
        print("initial state: ", possible_initial_state)
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


def a_star(problem, initial_states_product, initial_states_company):
    second_path = a_star_helper(problem, initial_states_product)
    new_goal = second_path[0]
    initial_goal = problem.get_goal()
    problem.set_goal(new_goal)
    first_path = a_star_helper(problem, initial_states_company)
    full_path = first_path + second_path
    problem.set_goal(initial_goal)  # put the goal state as it was
    return full_path


'''
target_city = input("Enter the city you want to ship to: ")
product = input("Enter product: ")
quantity = input("Enter quantity in kg: ")
month = input("Enter the month of the shipment: ")
'''
# handling transition model
state_transition_model = {}
with open('data/wilaya_frontiere.txt', 'r') as file:
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


problemLogistic = TransportProblem("", "Alger", state_transition_model)
cities = problemLogistic.find_source_city("tomato", "52384000", "6")
companies = problemLogistic.find_company("tomato", "52384000")


# calling the functions and printing (will be changed with a menu eventually)
# A star
'''
solution = a_star(problemLogistic, cities, companies)
counter = 0
print("solution:")
for e in solution:
    print(e)
    #counter += e.cost
#print(counter)

# Breadth-First Search
solutions = breadth_first_search(problemLogistic, cities)

if solutions:
    for i, solution in enumerate(solutions):
        print(f"\nSolution starting from city: {cities[i]}")
        for item in solution:
            print(item)
else:
    print("No solution found for any of the initial states.")

print("------------------------------------"*4)
'''
'''
# Uniform Cost Search
for initial_state in cities:
    solution, total_cost = ucs(state_transition_model, initial_state, target_city)
    if solution:
        print(f"\nSolution starting from city: {initial_state}")
        cumulative_cost = 0  # Initialize cumulative cost
        for i, (node, cost) in enumerate(solution):
            cumulative_cost += cost  # Update cumulative cost
            if i == 0:
                print(f"{node} ({cost:.1f})", end="")
            else:
                print(f" -> {node} ({cumulative_cost:.1f})", end="")
                
        print()
        print(f"Cost of solution is {total_cost:.1f}")
        print(f"Depth of goal node: {len(solution) - 1}")
    else:
        print(f"No solution found starting from city: {initial_state}")
'''

solutions = ucs(problemLogistic, cities)

if solutions:
    for i, solution in enumerate(solutions):
        print(f"\nSolution starting from city: {cities[i]}")
        for item in solution[0]:
            print(item[0])
        print("cost: ", round(solution[1], 2))
else:
    print("No solution found for any of the initial states.")

print("------------------------------------"*4)
