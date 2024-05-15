import webview
from flask import Flask, render_template, request, redirect, url_for
import folium
from supply_chain_system import search_strategies

app = Flask(__name__)
window = webview.create_window("Supply Chain System", app)

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


@app.route('/')
def logistics():
    return render_template('logistics.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Process the form data
        strategy = request.form.get('strategy')
        wilaya = request.form.get('wilaya')
        month = request.form.get('month')
        products = request.form.get('products')
        quantity = request.form.get('quantity')

        print("Strategy*:", strategy)
        print("Wilaya:", wilaya)
        print("Month:", month)
        print("Products:", products)
        print("Quantity:", quantity)
        
        # Redirect to /map with form data as URL parameters
        return redirect(
            url_for('map', strategy=strategy, wilaya=wilaya, month=month, products=products, quantity=quantity))

    # If it's a GET request, render the search.html template
    return render_template('search.html')


@app.route('/map', methods=['GET', 'POST'])
def map():
    # get data from front-end
    strategy = request.args.get('strategy')
    wilaya = request.args.get('wilaya')
    month = request.args.get('month')
    products = request.args.get('products')
    quantity = request.args.get('quantity')

    print("Strategy:", strategy)
    print("Wilaya:", wilaya)
    print("Month:", month)
    print("Products:", products)
    print("Quantity:", quantity)
    if strategy=="UCS":
       company, solution, cities, companies,min_cost_final, price, time, source_city = search_strategies.perform_search(strategy, wilaya, month, products, quantity)
    else:
        company, solution, cities, companies, price, time, source_city = search_strategies.perform_search(strategy, wilaya, month, products, quantity)
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

    goal_city = state_transition_model[wilaya]["coordinates"]
    path_info_script=f"""
    <script>
        const link = document.createElement('link');

        link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,200..1000;1,200..1000&display=swap';

        document.head.appendChild(link);
        // Get the company_name, price, and number_of_trips variables passed from Flask
        var company_name = "{ company }";
        var price = "{ round(price, 2) }";
        var time = "{ time }";
        var source_city ="{source_city}";

        function createInfoDiv() {{
        // Create a new div element
        var div = document.createElement("div");

        // Set the div's HTML content with the company name, price, and number of trips
        div.innerHTML = "<p>Company name: " + company_name + "</p>" +
                        "<p>Price: " + price + " da </p>" +
                        "<p>Time: " + time + " t </p>"+
                        "<p>Source city: " + source_city + "</p>";

        // Apply CSS styles to the div
        div.style.fontFamily = "Nunito, sans-serif";
        div.style.borderRadius = "12px";
        div.style.boxShadow = "0px 4px 8px rgba(0, 0, 0, 0.2)";
        div.style.width = "20em";
        div.style.padding = "10px";
        div.style.position = "absolute";
        div.style.top = "10px"; // Adjust the top position as needed
        div.style.left = "10px"; // Adjust the left position as needed
        div.style.zIndex = "1000"; // Ensure the div is on top of the map
        div.style.backgroundColor="#708090";  // Set the text color
        div.style.color="#FFFFFF";
        // Append the div to the document body
        document.body.appendChild(div);
    }}

    // Call the function to create the info div
    createInfoDiv();
    
    </script>
    """
    # Coordinates of the center of Algeria
    map_center = [28.0339, 1.6596]

    # Create a map centered around Algeria
    m = folium.Map(location=map_center, zoom_start=5)

    # case where the source city is the same as the transportation city
    for coord in coordinates_source_city:
        for coord_transport in coordinates_transportation_cities:
            if coord == coord_transport:
                folium.Marker([coord[0], coord[1]+ 0.009], icon=folium.Icon(icon='box', prefix='fa', color='blue'),
                              popup='Source City').add_to(m)

    # case where the source city is the same as the target city
    for coord in coordinates_source_city:
        if coord == goal_city:
            folium.Marker([coord[0], coord[1]+0.009], icon=folium.Icon(icon='box', prefix='fa', color='blue'),
                          popup='Source City').add_to(m)

    #case where the truck city is the same as the goal city
    for coord in coordinates_transportation_cities:
        if coord == goal_city:
            folium.Marker([coord[0], coord[1]+0.009], icon=folium.Icon(icon='truck', prefix='fa', color='green'),
                          popup='Truck City').add_to(m)


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
        if city is not solution[len(solution) - 1] and city is not solution[0]:  # add points as marker
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
    m.save('./templates/map.html')

    # Read the content of map.html
    with open('./templates/map.html', 'r') as file:
        map_content = file.read()

    # Append your custom JavaScript code to the content
    custom_script = """
  <script>
  // Function to handle back button click
  function handleBackButtonClick() {
    // Perform custom actions when the back button is clicked
    // For example, you can redirect to a specific URL or trigger an event
    // In this case, you may want to redirect to a route in your Flask app
    window.location.href = "/search";
  }
</script>
  """
    modified_content = map_content + custom_script

    # Write the modified content back to map.html
    with open('./templates/map.html', 'w') as file:
        file.write(modified_content)

    # Return map.html to the front end
    map_content= render_template("map.html")
    return map_content + path_info_script


if __name__ == '__main__':
    # app.run(debug=True)
    webview.start()
