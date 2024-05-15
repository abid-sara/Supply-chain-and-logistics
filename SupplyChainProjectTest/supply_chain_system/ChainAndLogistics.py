from math import radians, sin, cos, sqrt, atan2


class Node:
    """
        This class represents the node 
    """
    def __init__(self, state, parent=None, action=None, cost=0, heuristic=0.0):
        self.state = state
        self.parent = parent  # node
        self.action = action  # action performed to get to this node
        self.cost = cost  # (incremented with each newly expanded node)
        if parent is None:  # root node
            self.depth = 0  # level in the graph 0 for the root node
        else:
            self.depth = parent.depth + 1  # parent level + 1
        self.heuristic = heuristic

    def __hash__(self):  # It converts the state (nested list) into a tuple (since lists are not hashable)
        return hash(tuple(tuple(self.state)))

    def __eq__(self, other):
        return self.state == other.state

    def __gt__(self, other):
        return self.cost <= other.cost


class TransportProblem:
    def __init__(self, initial_state, goal_state, state_transition_model, actions="", path_cost=0):
        self.state = initial_state
        self.goal_state = goal_state
        self.state_transition_model = state_transition_model
        self.actions = actions
        self.path_cost = path_cost

    def is_goal_test(self, goal_test):
        return goal_test.state == self.goal_state

    def apply_action(self, action):
        self.state = action
        return self.state

    def get_valid_actions(self, state):
        if state in self.state_transition_model:
            neighbors = self.state_transition_model[state]["neighbors"]
            return neighbors
        else:
            return []

    def expand_node(self, node):
        state = node.state
        valid_actions = self.get_valid_actions(state)
        child_nodes = []
        for action in valid_actions:
            child_state = self.apply_action(action)
            cost_child = self.state_transition_model[state]["neighbors"][child_state]
            child_node = Node(child_state, parent=node, action=action, cost=node.cost + cost_child)
            child_nodes.append(child_node)
        return child_nodes

    def reconstruct_path(self, node):
        """
            Function to get the path of the solution
        """
        path = []
        while node:
            path.insert(0, node.state)  # Insert at the beginning to maintain the correct order
            node = node.parent
        return path

    def find_source_city(self, product, quantity,season_month):  
        """
            product: the product we want to ship
            quantity: the quantity we want to ship
            season_month: the month of the shipment (should be the same as the products season)
            returns a list of cities

            This function opens the appropriate data file, then reads it and puts the appropriate wilayas
            where the product is available, with the desired quantity in the desired month in a list

        """
        product_file = None
        if product == "wheat":
            product_file = open("supply_chain_system/data/wheat.txt", 'r')
        elif product == "date":
            product_file = open("supply_chain_system/data/date.txt", 'r')
        elif product == "tomato":
            product_file = open("supply_chain_system/data/tomato.txt", 'r')
        elif product == "orange":
            product_file = open("supply_chain_system/data/orange.txt", 'r')
        elif product == "lemon":
            product_file = open("supply_chain_system/data/lemon.txt", 'r')
        elif product == "mandarine":
            product_file = open("supply_chain_system/data/mandarin.txt", 'r')
        elif product == "pomelo":
            product_file = open("supply_chain_system/data/pomelos.txt", 'r')
        elif product == "clementine":
            product_file = open("supply_chain_system/data/clementine.txt", 'r')
        elif product == "potato" and season_month == "3" or season_month == "4":
            product_file = open("supply_chain_system/data/potatoes_early.txt", 'r')
        elif product == "potato" and season_month == "11" or season_month == "12" or season_month == "1":
            product_file = open("supply_chain_system/data/potatoes_season.txt", 'r')
        elif product == "potato" and int(season_month) in range(5, 8):
            product_file = open("supply_chain_system/data/potatoes_late.txt", 'r')

        cities = []
        for line in product_file:
            parts = line.strip().split(',')
            city = parts[0]
            produced_quantity = float(parts[1])
            if produced_quantity != 0:
                production_season = [int(season) for season in parts[2:]]
                for month in production_season:
                    if int(month) == int(season_month) and produced_quantity >= float(quantity):
                        cities.append(city)
        return cities

    def find_company(self, product, quantity):
        """
        Find companies capable of transporting the given product based on their capacity and product compatibility.

        Args:
        product (str): The type of product to be transported.
        quantity (str): The quantity of the product to be transported, in kilograms.

        Returns:
        dict: A dictionary containing information about the companies capable of transporting the product,
              including their names, locations, available capacities, and the estimated number of trucks needed.
        """
        # convert the capacity from KG to Tonne
        quantity_in_tonne = float(quantity) / 1000

        with open("supply_chain_system/data/companies.txt", "r", encoding="utf-8") as company_file:
            companies = {}
            if int(quantity) > 0:
                for line in company_file:
                    parts = line.strip().split(', ')
                    products = parts[4].split('& ')
                    if product in products or 'all' in products:  # check if the company transport the product
                        name = parts[0]
                        wilaya = parts[1]
                        num_of_trucks_available = parts[2]
                        capacity = parts[3]
                        price = float(parts[5]) * float(quantity)
                        if name in companies:  # we check if the company already exists in the dictionary so, we append the new capacity to the list of capacities, and add the number of trucks available corresponding to this capacity
                            companies[name]["capacities"].append(capacity)
                            companies[name]["number of trucks available"].append(num_of_trucks_available)
                        else:  # we add the company to the dictionary and create a list of capabilities
                            companies[name] = {
                                "wilaya": wilaya,
                                "number of trucks available": [num_of_trucks_available],
                                "capacities": [capacity],
                                "number of trips needed": 0,
                                "price": price
                            }

                #calculate the number of trips needed for each company to transport the quantity given
                for company in companies:
                    num_of_available_capacities = len(companies[company]["capacities"])
                    quantity_left = quantity_in_tonne
                    num_of_trips_needed = 0
                    
                    while quantity_left > 0:
                        index = num_of_available_capacities - 1  # Initialize the index for iterating through the list of capacities (starting from the highest capacity in the list)
                        num_of_trips_needed += 1
                        for current_capacity in list(reversed(companies[company]["capacities"])):
                            # convert the capacity to float
                            current_capacity = int(current_capacity[:-1])
                            
                            # convert the number of trucks available in this capacity to integer
                            available_trucks = int(companies[company]["number of trucks available"][index])
                            index -= 1

                            # calculate the quantity that can be transported with the current capacity
                            this_quantity = current_capacity * available_trucks

                            # update the quantity that is left
                            quantity_left -= this_quantity
                            
                            #if we got the whole quantity we break the loop
                            if quantity_left <= 0:
                                companies[company]["number of trips needed"] = num_of_trips_needed
                                break
                
                #make two temporary dictionaries to store the company with the lowest price and the company with the lowest time in each wilaya
                wilaya_company_cost = {}  # store the companies with lowest price in each wilaya
                wilaya_company_time = {}  # store the companies with lowest number of trips in each wilaya
                for company in companies:
                    wilaya = companies[company]["wilaya"] 
                    price = float(companies[company]["price"])
                    num_of_trips_needed = int(companies[company]["number of trips needed"])
                    
                    #get the company with lowest price
                    if wilaya in wilaya_company_cost:
                        min_price = float(wilaya_company_cost[wilaya]["price"])
                        if price <= min_price:
                            wilaya_company_cost[wilaya] = {"company": company, "number of trips needed": num_of_trips_needed, "price": price}
                    else:
                        wilaya_company_cost[wilaya] = {"company": company, "number of trips needed": num_of_trips_needed, "price": price}
                    
                    #get the company with lowest price
                    if wilaya in wilaya_company_time:
                        min_price = int(wilaya_company_time[wilaya]["price"])
                        if price <= min_price:
                            wilaya_company_time[wilaya] = {"company": company, "number of trips needed": num_of_trips_needed, "price": price}
                    else:
                        wilaya_company_time[wilaya] = {"company": company, "number of trips needed": num_of_trips_needed, "price": price}
            
                #compare the two dictionaries and choose the best company for each wilaya and store them in a new dict
                wilaya_company = {}
                for wilaya in wilaya_company_time:
                    company_name_01 = wilaya_company_time[wilaya]["company"]
                    company_name_02 = wilaya_company_cost[wilaya]["company"]
                    
                    num_trips_01 = wilaya_company_time[wilaya]["number of trips needed"]
                    num_trips_02 = wilaya_company_cost[wilaya]["number of trips needed"]
                    
                    #percentage of difference between the two 'times', needed for later to compare
                    time_percent = (max(num_trips_01, num_trips_02) - min(num_trips_01, num_trips_02))/100
                    
                    cost_01 = wilaya_company_time[wilaya]["price"]
                    cost_02 = wilaya_company_cost[wilaya]["price"]
                    
                    #percentage of difference between the two prices, needed for later to compare
                    cost_percent = (max(cost_01, cost_02) - min(cost_01, cost_02))/100
                    
                    #case where the companies have the same cost and time
                    if cost_01 == cost_02 and num_trips_01 == num_trips_02:  # choose randomly
                        wilaya_company[wilaya] = {"company": company_name_01, "number of trips needed": num_trips_01, "price": cost_01}
                    
                    #cases where we have to choose the company with the lowest price
                    elif (cost_01 > cost_02 and num_trips_01 > num_trips_02) or (num_trips_01 == num_trips_02 and cost_02 < cost_01):
                        wilaya_company[wilaya] = {"company": company_name_02, "number of trips needed": num_trips_02, "price": cost_02}
                    
                    #cases where we have to choose the company with the lowest number of trips
                    elif (cost_01 < cost_02 and num_trips_01 < num_trips_02) or (num_trips_01 == num_trips_02 and cost_01 < cost_02) or (cost_01 == cost_02 and num_trips_01 < num_trips_02):
                        wilaya_company[wilaya] = {"company": company_name_01, "number of trips needed": num_trips_01, "price": cost_01}
                    
                    #choosing between two companies where it's difficult to decide whether to prioritize the one with the lowest price or the shortest delivery time
                    elif (cost_01 < cost_02 and num_trips_01 > num_trips_02) or (cost_01 > cost_02 and num_trips_01 < num_trips_02) or (cost_01 == cost_02 and num_trips_02 < num_trips_01):
                        if time_percent >= cost_percent:
                            wilaya_company[wilaya] = {"company": company_name_02, "number of trips needed": num_trips_02, "price": cost_02}
                        else:
                            wilaya_company[wilaya] = {"company": company_name_01, "number of trips needed": num_trips_01, "price": cost_01}
                      
            else:
                print("No transportation needed.")

        return wilaya_company

    # informed strategy related  functions
    def get_cowl_flew_distance(self, city_name, goal_city_name):
        """
            city_name:  the departure city's name
            goal_city_name: the arrival city's name
            returns an estimated value of the distance (straight line distance)
        """
        # get coordinates from the file
        city_coordinates = self.state_transition_model[city_name]["coordinates"]
        goal_city_coordinates = self.state_transition_model[goal_city_name]["coordinates"]
        lat1 = city_coordinates[0]
        lon1 = city_coordinates[1]
        lat2 = goal_city_coordinates[0]
        lon2 = goal_city_coordinates[1]

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        # Calculate the straight-line distance using Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        h = 6371 * c  # Radius of the Earth in kilometers
        return round(h, 2)

    def heuristic(self, state):
        return self.get_cowl_flew_distance(state, self.goal_state)
