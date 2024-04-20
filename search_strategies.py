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
def ucs_helper(problem):
    frontier = []
    explored = set()
    initial_node = Node(problem.state)
   # heapq.heappush(frontier, (0, initial_node))
    frontier.append((initial_node.cost, initial_node))  # Initial node with cost 0
    '''The frontier is implemented as a priority queue using the heapq module in Python. This ensures that the node with the smallest cumulative cost is always popped from the frontier first.'''

    while frontier:
        frontier.sort(key=lambda x: x[0])  # Sort the frontier by cost
        current_cost, node = frontier.pop(0)  # Pop the node with the lowest cost
        #current_cost, node = heapq.heappop(frontier)
        if problem.is_goal_test(node):
            return node
        if node not in explored:
         explored.add(node.state)
         children = problem.expand_node(node)
         for child in children:
            if child.state not in explored:
                #heapq.heappush(frontier, (child_cost, child))
                frontier.append((child.cost, child))# child node have accumulated cost its cost + parent cost (see expand_node function)


    return None
def uniform_cost_search(problem, initial_states):
    solutions = []
    for initial_state in initial_states:
        problem.state = initial_state
        solution_node = ucs_helper(problem)
        if solution_node:
            solution_path = []
            node = solution_node
            while node:
                solution_path.insert(0, node)
                node = node.parent
            #solution_path.reverse()
            solutions.append(solution_path)
    return solutions


def UcsCompany(problem,initial_states,companies):
    setSol=uniform_cost_search(problem,initial_states)
    min_cost1 = float('inf')
    min_cost_final = float('inf')
    min_path = None#path from source city to user wilaya
    best_company = None
    best_path = None#final path
    min_initial_state = None#goalstate of ucscompanyhelper

    for path1 in setSol:
        cost1=path1[-1].cost #access the  last node (the goal) and get the path cosy

        if cost1 < min_cost1:
            min_cost1 = cost1
            min_path = [node.state for node in path1]  # Convert the path to a list of states
            # Since each (path, cost) corresponds to a specific initial_state in setSol,
            # we don't need to track the initial_state here directly.
            min_initial_state = min_path[0]  # Assuming path is not empty
    #goal_state_of_company=min_initial_state#source_city
    #initial_states_company=companies
    setComp=[]#initial_states for ucs companies
    
    setComp = [companies[company]['wilaya'] for company in companies]

    problem.set_goal(min_initial_state)#update the problem goal

    setSolCompanies=uniform_cost_search(problem,setComp)

    for company, path_company_source in zip(companies, setSolCompanies):
        cost_company_source = path_company_source[-1].cost  # Get the cost of the last node in the path(the goal so the cost of reaching the goal)
        cost2=min_cost1+cost_company_source #the total cost of transporting the product from the company to the wilaya of user 
        
        if cost2 <min_cost_final:
            min_cost_final = cost2
            best_company = company
            best_path = [node.state for node in path_company_source[:-1]] + min_path  # the final path of transporting the product from the company to the wilaya of user 
    
    if min_cost_final == float('inf'):
        return None, None, None ,None,None

    return best_company, min_cost_final, best_path ,min_initial_state,companies[best_company]['wilaya']

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


target_city = input("Enter the city you want to ship to: ")
product = input("Enter product: ")
quantity = input("Enter quantity in kg: ")
month = input("Enter the month of the shipment: ")
problemLogistic = TransportProblem("", target_city, state_transition_model)
cities = problemLogistic.find_source_city(product, quantity, month)
companies = problemLogistic.find_company(product, quantity)

best_company, min_cost, best_path ,min_initial_state,wilaya_company=UcsCompany(problemLogistic,cities,companies)
print(f"source_city : {min_initial_state}")
print(f"The best company is {best_company} in wilaya {wilaya_company}")

print(f"The minimum cost is {min_cost}")
print(f"path : {best_path}")
# calling the functions and printing (will be changed with a menu eventually)
# A star
'''
solution = a_star(problemLogistic, cities, companies)
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
'''
