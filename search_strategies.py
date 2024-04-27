import helper_function
import folium


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


#for ucs
def merge_ucs_searches(problem, source_cities,
                       companies):  
    nearest_source_city,cost_problem_source = helper_function.UCS_optimal_solution(problem, source_cities)#path and cost from  source city to city of user
    company_problem = helper_function.TransportProblem("", nearest_source_city[0], state_transition_model)#reset the goal

    company_name, nearst_company_city,cost_company_source  = helper_function.find_optimal_company_solution(company_problem, companies, "UCS")#path and cost from company to source city
    company_to_source_problem = helper_function.TransportProblem(nearst_company_city[0], nearest_source_city[0], state_transition_model)
    path_from_company_to_source_city = helper_function.ucs_helper(company_to_source_problem)
    cost1=path_from_company_to_source_city.cost
    path_from_company_to_source_city = company_to_source_problem.reconstruct_path(path_from_company_to_source_city)
    source_to_destination_problem = helper_function.TransportProblem(nearest_source_city[0], problem.goal_state, state_transition_model)
    path_from_source_city_to_destination = helper_function.ucs_helper(source_to_destination_problem)
    cost2=path_from_source_city_to_destination.cost

    path_from_source_city_to_destination = source_to_destination_problem.reconstruct_path(
        path_from_source_city_to_destination)
    # Get the full path
    full_path = path_from_company_to_source_city + path_from_source_city_to_destination
    full_path = list(dict.fromkeys(full_path))  # remove the duplicated keys
    min_cost_final=cost1+cost2
    return company_name, full_path ,min_cost_final



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

def hill_climbing_solution(problem, initial_states_product, initial_states_company):

    second_path = helper_function.hill_climbing(problem, initial_states_product)
    print("path from source to dest: ", second_path)
    company_problem = helper_function.TransportProblem("", second_path[0], state_transition_model)
    company_name, first_path = helper_function.find_optimal_company_solution(company_problem, initial_states_company, "hill_climbing")
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

problemLogistic = helper_function.TransportProblem("", "Adrar", state_transition_model)
cities = problemLogistic.find_source_city("lemon", "384000", "12")
companies = problemLogistic.find_company("lemon", "384000")
company_name, full_path ,min_cost_final= merge_ucs_searches(problemLogistic, cities,companies)  
print(company_name)
print(full_path)
print(min_cost_final)
company_name2, full_path2=hill_climbing_solution(problemLogistic, cities, companies)
print(company_name2)
print(full_path2)
# companies = problemLogistic.find_company("date", "384000")
# #company_name, solution = a_star(problemLogistic, cities, companies)
#                         #  merge_bfs_searches(problemLogistic, cities, companies)
# print("COMPANY: ", end="")
# print(company_name)
# print("SOLUTION: ", end="")
# print(solution)


# Coordinates of the center of Algeria 
map_center = [28.0339, 1.6596]

# Create a map centered around Algeria
m = folium.Map(location=map_center, zoom_start=5)

# get the coordinates of the source cities
coordinates_source_city = []
for city in cities:
    city_coordinates = state_transition_model[city]["coordinates"]
    coordinates_source_city.append(city_coordinates)

# get the coordinates of the truck cities
coordinates_transportation_cities = []
for city in list(companies.keys()):
    city_coordinates = state_transition_model[city]["coordinates"]
    coordinates_transportation_cities.append(city_coordinates)

# goal_city =target_city  !!!!!!!!!!!!!will use this afterwards!!!!!!!!!!!!!!!!!!!!!
goal_city = state_transition_model["Ouargla"]["coordinates"]

# Add markers for source cities
for coord in coordinates_source_city:
    folium.Marker(
        location=[coord[0], coord[1]],
        popup='Source City',
        icon=folium.Icon(color='blue', icon='box', prefix='fa')
    ).add_to(m)

# Add markers for truck cities
for coord in coordinates_transportation_cities:
    folium.Marker(
        location=[coord[0], coord[1]],
        popup='Truck City',
        icon=folium.Icon(color='green', icon='truck', prefix='fa')
    ).add_to(m)

# Add a marker for the goal city
folium.Marker(
    location=[goal_city[0], goal_city[1]],
    popup='Goal City',
    icon=folium.Icon(color='red', icon='flag')
).add_to(m)

# path coordinates
path = []
for city in solution:
    coordinates = state_transition_model[city]["coordinates"]
    if city is not solution[len(solution)-1] and city is not solution[0]:  # add points as marker
        folium.CircleMarker(
            location=[coordinates[0], coordinates[1]],
            radius=4,
            popup="passed by",
            color='black',
            fill=True,
            fill_color='black'
        ).add_to(m)
    path.append(coordinates)

# Add lines for the path
folium.PolyLine(path, color='blue').add_to(m)

# Save to an HTML file
m.save('map.html')

