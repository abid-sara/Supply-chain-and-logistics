from math import radians, sin, cos, sqrt, atan2


class Node:
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

    def the_goal(self):
        return self.goal_state

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

    def print_node(self, message, node):
        print("Action = ", end=" ")
        print(node.action, end=" \n")
        print(message, end=" \n")
        print(node.state)

    def print_solution_path(self, node):
        solution_path = []
        while node is not None:
            solution_path.append(node.state)
            node = node.parent
        solution_path.reverse()
        print("Solution Path:")
        for state in solution_path:
            print(state)

    def find_source_city(self, product, quantity, season_month):  # function to find the city where to get the product from
        print("in find source city function**************************************")
        product_file = None
        if product == "wheat":
            product_file = open("data/wheat.txt", 'r')
        elif product == "dates":
            product_file = open("data/date.txt", 'r')
        elif product == "tomatoes":
            product_file = open("data/tomato.txt", 'r')
        elif product == "orange":
            product_file = open("data/orange.txt", 'r')
        elif product == "lemon":
            product_file = open("data/lemon.txt", 'r')
        elif product == "mandarin":
            product_file = open("data/mandarin.txt", 'r')
        elif product == "pomelo":
            product_file = open("data/pomelos.txt", 'r')
        elif product == "potatoes" and season_month == 3 or season_month == 4:
            product_file = open("data/potatoes_early.txt", 'r')
        elif product == "potatoes" and season_month == 11 or season_month == 12 or season_month == 1:
            product_file = open("data/potatoes_season.txt", 'r')
        elif product == "potatoes" and season_month in range(5, 8):
            product_file = open("data/potatoes_late.txt", 'r')

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

    # informed strategy related  functions
    def get_cowl_flew_distance(self, city_name, goal_city_name):
        #get coordinates from the file
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

