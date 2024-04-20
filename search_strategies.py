import helper_function


def merge_bfs_searches(problem, source_cities,
                       companies):  # Function that returns the full path from the company location to the goal city + the company that transported the product
    # Find the nearest source city
    nearest_source_city = helper_function.BFS_optimal_solution(problem, source_cities)
    # Make a new transport problem which its goal city is the found source city
    company_problem = helper_function.TransportProblem("", nearest_source_city[0], state_transition_model)

    # Find the shortest path between the nearest company to the source city
    company_name, nearst_company_city = helper_function.find_optimal_company_solution(company_problem, companies, "BFS")

    # Get the path from the company location to the source city
    company_to_source_problem = helper_function.TransportProblem(nearst_company_city[0], nearest_source_city[0], state_transition_model)
    path_from_company_to_source_city = helper_function.breadth_first_search_helper(company_to_source_problem)
    path_from_company_to_source_city = company_to_source_problem.reconstruct_path(path_from_company_to_source_city)

    # Get the path from the company location to the source city
    source_to_destination_problem = helper_function.TransportProblem(nearest_source_city[0], problem.goal_state, state_transition_model)
    path_from_source_city_to_destination = helper_function.breadth_first_search_helper(source_to_destination_problem)
    path_from_source_city_to_destination = source_to_destination_problem.reconstruct_path(
        path_from_source_city_to_destination)
    # Get the full path
    full_path = path_from_company_to_source_city + path_from_source_city_to_destination
    full_path = list(dict.fromkeys(full_path))  # remove the duplicated keys
    return company_name, full_path


def uniform_cost_search(problem, initial_states):
    solutions = []
    for initial_state in initial_states:
        problem.state = initial_state
        solution_node = helper_function.ucs_helper(problem)
        if solution_node:
            solution_path = []
            node = solution_node
            while node:
                solution_path.insert(0, node)
                node = node.parent
            # solution_path.reverse()
            solutions.append(solution_path)
    return solutions


def UcsCompany(problem, initial_states, companies):
    setSol = uniform_cost_search(problem, initial_states)
    min_cost1 = float('inf')
    min_cost_final = float('inf')
    min_path = None  # path from source city to user wilaya
    best_company = None
    best_path = None  # final path
    min_initial_state = None  # goalstate of ucscompanyhelper

    for path1 in setSol:
        cost1 = path1[-1].cost  # access the  last node (the goal) and get the path cosy

        if cost1 < min_cost1:
            min_cost1 = cost1
            min_path = [node.state for node in path1]  # Convert the path to a list of states
            # Since each (path, cost) corresponds to a specific initial_state in setSol,
            # we don't need to track the initial_state here directly.
            min_initial_state = min_path[0]  # Assuming path is not empty
    # goal_state_of_company=min_initial_state#source_city
    # initial_states_company=companies
    setComp = []  # initial_states for ucs companies

    setComp = [companies[company]['wilaya'] for company in companies]

    problem.set_goal(min_initial_state)  # update the problem goal

    setSolCompanies = uniform_cost_search(problem, setComp)

    for company, path_company_source in zip(companies, setSolCompanies):
        cost_company_source = path_company_source[
            -1].cost  # Get the cost of the last node in the path(the goal so the cost of reaching the goal)
        cost2 = min_cost1 + cost_company_source  # the total cost of transporting the product from the company to the wilaya of user

        if cost2 < min_cost_final:
            min_cost_final = cost2
            best_company = company
            best_path = [node.state for node in path_company_source[
                                                :-1]] + min_path  # the final path of transporting the product from the company to the wilaya of user

    if min_cost_final == float('inf'):
        return None, None, None, None, None

    return best_company, min_cost_final, best_path, min_initial_state, companies[best_company]['wilaya']


# ucs finishes here

def a_star(problem, initial_states_product, initial_states_company):

    #path from source to goal
    second_path = helper_function.a_star_helper(problem, initial_states_product)
    print("path from source to dest: ", second_path)
    # Get the path from the company location to the source city
    company_problem = helper_function.TransportProblem("", second_path[0], state_transition_model)
    company_name, first_path = helper_function.find_optimal_company_solution(company_problem, initial_states_company, "A*")
    print("path from company to source: ", first_path)
    full_path = first_path + second_path
    full_path = list(dict.fromkeys(full_path))

    return company_name, full_path


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

problemLogistic = helper_function.TransportProblem("", "Tizi Ouzou", state_transition_model)
cities = problemLogistic.find_source_city("date", "384000", "10")
companies = problemLogistic.find_company("date", "384000")
company_name, solution = a_star(problemLogistic, cities, companies)
                        #  merge_bfs_searches(problemLogistic, cities, companies)
print("COMPANY: ", end="")
print(company_name)
print("SOLUTION: ", end="")
print(solution)


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
