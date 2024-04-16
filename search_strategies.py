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
            explored.append(node_chosen)
            return explored
        explored.append(node_chosen)
        children = problem.expand_node(node_chosen)
        for child in children:
            if child not in explored and child not in frontier.queue:
                frontier.put(child)
    return None


def breadth_first_search(problem, initial_states):
    setSol = []
    for initial_state in initial_states:
        print("initial state: ", initial_state, "£$$$$$$$$"*3)
        problem.state = initial_state  # update the initial state
        sol = breadth_first_search_helper(problem)
        if sol:  # if solution exists append it to the total solutions list
            setSol.append(sol)
    return setSol


# ucs starts here
def path_cost(path):
    total_cost = sum(cost for _, cost in path)
    return total_cost, path[-1][0]  # if two items have the same total_cost, then sort by node name (alphabetically)


def get_total_cost(x):  # will be used in extracting the total cost from each tuple from the frontier
    return x[0]


def ucs(graph, initial_state, goal):
    """Initialize the frontier with the starting state and its cost of 0
       The frontier is represented as a list of tuples, where each tuple contains:
       (total_cost, state, path)
       This allows us to easily sort the frontier by the total cost of the paths,
       which is the key requirement for the Uniform Cost Search algorithm."""
    frontier = [(0, initial_state, [(initial_state, 0)])]  # (total_cost, state, path)
    explored = {}  # Explored nodes and their costs

    while frontier:
        # Sort the frontier by total_cost
        frontier.sort(key=get_total_cost)

        # Get the node with the lowest cost
        total_cost, node, path = frontier.pop(0)

        if node == goal:
            return path, total_cost

        # Check if the node has already been explored or if the new path has a lower cost
        if node not in explored or total_cost < explored[node][0]:
            explored[node] = (total_cost, path)  # This ensures that the algorithm keeps track of the lowest-cost path to each explored state.

            # Retrieve neighbors and their costs from the graph
            neighbors = graph.get(node, {})

            for neighbor, neighbor_cost in neighbors.items():
                new_total_cost = total_cost + neighbor_cost
                new_path = path + [(neighbor, neighbor_cost)]
                child_node = (new_total_cost, neighbor, new_path)
                frontier.append(child_node)

    return None, 0   # return path, total_cost and returns (None, 0) if no solution is found
#ucs finishes here


# informed search functions start here
def a_star(problem, initial_states):
    best_path = None
    smallest_objective_value = float('inf')

    for possible_initial_state in initial_states:
        print("initial state: ", possible_initial_state)
        frontier = queue.PriorityQueue()
        explored = []

        root = Node(possible_initial_state)
        frontier.put((root, root.cost + problem.heuristic(root.state)))

        while frontier:
            chosen_node = frontier.get()[0]
            print("chosen node inside the a star: ", chosen_node.state)

            if problem.is_goal_test(chosen_node):
                objective_value = chosen_node.cost + problem.heuristic(chosen_node.state)
                print(chosen_node.cost)
                print("objective value: ", objective_value, "smallest value: ", smallest_objective_value)
                if objective_value < smallest_objective_value:  # if this is the smallest heuristic then it is the best root to take hence the best path solution is found
                    smallest_objective_value = objective_value
                    explored.append(chosen_node)
                    best_path = explored  # Copy the explored list to best_path
                break

            explored.append(chosen_node)
            print("explored:")
            for el in explored:
                print(el.state)
            children = problem.expand_node(chosen_node)

            for child in children:
                print("child: ", child.state)
                if child not in explored and child.state not in [n[0].state for n in frontier.queue]:
                    print("a*: ", child.cost + problem.heuristic(child.state))
                    frontier.put((child, child.cost + problem.heuristic(child.state)))

    return best_path


target_city = input("Enter the city you want to ship to: ")
product = input("Enter product: ")
quantity = input("Enter quantity in kg: ")
month = input("Enter the month of the shipment: ")

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


problemLogistic = TransportProblem("", target_city, state_transition_model)
cities = problemLogistic.find_source_city(product, quantity, month)
print("cities as initial state: ", cities)


# calling the functions and printing (will be changed with a menu eventually)
'''
# A star
solution = a_star(problemLogistic, cities)
print("solution:")
for e in solution:
    print(e.state)


# Breadth-First Search
solutions = breadth_first_search(problemLogistic, cities)

if solutions:
    for i, solution in enumerate(solutions):
        print(f"\nSolution starting from city: {cities[i]}")
        for item in solution:
            print(item.state)
else:
    print("No solution found for any of the initial states.")

print("------------------------------------"*4)

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


