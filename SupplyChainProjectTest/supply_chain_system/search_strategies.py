from supply_chain_system import helper_function
from supply_chain_system.ChainAndLogistics import TransportProblem
from supply_chain_system.ChainAndLogistics import Node
import folium
def merge_bfs_searches(problem, source_cities, companies):
    ''' 
        problem: instance of problem we're solving
        source_cities: the possible source cities where to get the product from
        companies
        Function that returns the full path from the company location to the goal city + the company
        that transported the product
        
    '''
    
    # Find the nearest source city
    path_from_source_city_to_destination, distance = helper_function.BFS_shortest_path_from_source_city(problem, source_cities)
    # Make a new transport problem which its goal city is the found source city
    company_problem = helper_function.TransportProblem("", path_from_source_city_to_destination[0], state_transition_model)
    
    # Identify the optimal company considering factors like price, time, and distance, and then store its path leading to the nearest source city
    company_name, path_from_company_to_source_city, price, time,_ = helper_function.select_best_company_path(company_problem, companies, distance, "BFS")
    
    path_from_source_city_to_destination = path_from_source_city_to_destination[1:]
    
    # Combine the two paths to generate the full path
    full_path = path_from_company_to_source_city + path_from_source_city_to_destination
    
    
    return company_name, full_path, price, time, path_from_source_city_to_destination[0]
  
    

def merge_ucs_searches(problem, source_cities, companies):
    path_from_source_city_to_destination,cost_problem_source = helper_function.UCS_shortest_path_from_source_city(problem, source_cities)#path and cost from  source city to city of user
   
    company_problem = helper_function.TransportProblem("", path_from_source_city_to_destination[0], state_transition_model)#reset the goal
    
    company_name, path_from_company_to_source_city, price, time,cost_company_source_goal  = helper_function.select_best_company_path(company_problem, companies, cost_problem_source, "UCS")#path and cost from company to source city
    path_from_source_city_to_destination =path_from_source_city_to_destination[1:]
    # Get the full path
    full_path = path_from_company_to_source_city + path_from_source_city_to_destination
    full_path = list(dict.fromkeys(full_path))  # remove the duplicated keys
    min_cost_final = cost_company_source_goal
    return company_name, full_path, min_cost_final, price, time


def a_star(problem, initial_states_product, initial_states_company, product, quantity):
    """
        problem: instance of the problem we're solving
        initital_states_product: possible source cities
        initial_state_company: possible company cities to transport the product 
        product: the product we want to ship
        quantity: the quantity we wand to ship

    """
    #path from source to goal
    second_path = helper_function.a_star_helper(problem, initial_states_product ,"multiple")
    print("path from source to dest: ", second_path)
    
    # Get the path from the company location to the source city
    company_problem = helper_function.TransportProblem("", second_path[0], state_transition_model)
    company_name, first_path, money, time = helper_function.find_optimal_company_solution(company_problem, initial_states_company, "A*", product, quantity)
    print("path from company to source: ", first_path)
    full_path = first_path + second_path
    full_path = list(dict.fromkeys(full_path))
    return company_name, full_path, money, time, second_path[0]


def hill_climbing_solution(problem, initial_states_product, initial_states_company, product, quantity):
    second_path = helper_function.hill_climbing(problem, initial_states_product, "multiple")
    print("path from source to dest: ", second_path)
    company_problem = helper_function.TransportProblem("", second_path[0], state_transition_model)
    company_name, first_path, money, time = helper_function.find_optimal_company_solution(company_problem, initial_states_company, "hill_climbing", product, quantity)
    print("path from company to source: ", first_path)
    full_path = first_path + second_path
    full_path = list(dict.fromkeys(full_path))

    return company_name, full_path, money, time,second_path[0]


def perform_search(strategy, wilaya, month, products, quantity):
    ProblemLogistic = helper_function.TransportProblem("", wilaya, state_transition_model)    
    cities = ProblemLogistic.find_source_city(products, quantity, month)
    companies = ProblemLogistic.find_company(products, quantity)
    
    solution = []
    
    if strategy == "BFS":
        company_name, solution, price, time, source_city = merge_bfs_searches(ProblemLogistic, cities, companies)
    elif strategy == "UCS":
        company_name, solution, min_cost_final, price, time, source_city = merge_ucs_searches(ProblemLogistic, cities, companies)
    elif strategy == "A*":
        company_name, solution, price, time, source_city= a_star(ProblemLogistic, cities, companies, products, quantity)
    elif strategy == "HillClimbing":
        company_name, solution, price, time, source_city = hill_climbing_solution(ProblemLogistic, cities, companies, products, quantity)
    if strategy == "UCS":
       return company_name, solution, cities, companies,min_cost_final, price, time, source_city
    else:
        return company_name, solution, cities, companies, price, time, source_city


# handling transition model
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


