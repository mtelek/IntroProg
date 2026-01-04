import pandas as pd
df=pd.read_csv("Dataset TSP.csv", sep=";") #sep because pandas normally with commas

city_names = df.columns.tolist()[1:] #first column
#print(df.columns.tolist()[1:])

dist = df.iloc[:, 1:].to_numpy()    #only numerical values, saved as NumPy-Array
#print(df)
#print(dist.shape)   # (29, 29)
#print(city_names[:5])
#print(df.columns.tolist())

def tsp_nearest_neighbor(dist, start=0):                #Nearest Neighbour Heuristic
    n = len(dist)               #n is the amount of rows in the df
    visited = [start]           #saves the order of the cities visited
    current = start             #city we are in right now

    while len(visited) < n:     #as long as not every city has been visited
        next_city = min(
            (i for i in range(n) if i not in visited),  #checks not yet visited cities, chooses minimal distance
            key=lambda i: dist[current, i])        #lambda = ad hoc function; chooses city index of minimal distance
        visited.append(next_city)       #chosen city
        current = next_city             #new start city

    return visited
nn_route = tsp_nearest_neighbor(dist, start=0)      #nn route using indices
#print("NN Route (Index):", nn_route)

def route_length(route, dist):    #computes route length
    total = 0
    for i in range(len(route) - 1):                 #creates range using the list from nn
        total += dist[route[i], route[i + 1]]       #searches distance from one city to the next in df, adds to total
    total += dist[route[-1], route[0]]              #return to start city
    return total

nn_length = route_length(nn_route, dist)
print("Route length according to Nearest Neighbour:", nn_length)

def route_to_names(route, city_names):      #Help function, displays route in readable format.
    return [city_names[i] for i in route]

print(route_to_names(nn_route, city_names))

def two_opt(route, dist):       #2-opt
    best = route
    best_len = route_length(best, dist)
    improved = True         #True in order for the while loop to start

    while improved:         #the algorithm runs until no improvements can be found (local optimum)
        improved = False
        for i in range(1, len(route) - 2):      #-2 because start and end have to stay the same
            for j in range(i + 1, len(route)):
                if j - i == 1:                  #if j is the index of the city visited after i -> no 2 opt possible
                    continue                    #j+=1 or if last j then next i

                new_route = best[:i] + best[i:j][::-1] + best[j:]   #flips everything between i and j
                new_len = route_length(new_route, dist)

                if new_len < best_len:          #variables are only updated if the new route is better
                    best = new_route
                    best_len = new_len
                    improved = True

        route = best

    return best, best_len

opt_route, opt_length = two_opt(nn_route, dist)

print("2-opt length:", opt_length)
print(route_to_names(opt_route, city_names))    #although city 1 not mentioned in list end, distance has been added