**Sara's part:**

1. find source city function
2. breadth_first_search_helper + breadth_first_search function (with nada)
3. handling transition model code
4. files: wheat.txt, date.txt, potatoes_early.txt, potatoes_season.txt, potatoes_late.txt
5. Added the path cost in transition model
6. a star helper + a star function
7. reconstruct path function to display the solution’s path
8. added the get_cowl_flew_distance + heuristic functions for the informed strategies
9. visualization

Solution explanation:

- find source function: first we will filter through the files for the appropriate product file and then find the cities that have the product in the required quantity
 and the given period of time this function will return a list of these states (cities), these are the possible roots (starting point) of the search,
 we then do multiple dfs choosing a city returned from the function as the root each time, we get multiple solutions for the path so we chose the one will the smallest
 number of cities it went through. This way we guarante the availablity of the goods with the required quantity and the appropriate season
    
- For the informed search: the g(n) is the actual cost (which is the car distance between the cities according to google maps), h(n) is the straight line distance
between the cities (used the formula given in lab 7) for this we need the coordinates of the cities present in the transition model
As said before, we will use the same idea of the find source city to find the possible roots, but while performing the search, we’ll keep the best path
(in terms of obejctive value) and return that as the solution
- For visualization, a python package called foluim was used, so to get the visualization you need to install the package and have internet,
it shows in bleu the cities that have the product with the needed quantity and that season, so all possible source cities, and in green the possible cities
where the trucks that can transport that product with that quantity are, and then in red, the goal city where we want to transport and finally the path

**Nada's part:**
**Sabrina's part:**
**Wissal's part:**
