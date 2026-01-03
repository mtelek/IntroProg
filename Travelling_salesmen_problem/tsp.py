# just copied a random tsp file from github in this folder to check it out
# def run_tsp():
import pandas as pd
import numpy as np
df=pd.read_csv("Dataset TSP.csv", sep=";")

city_names = df.iloc[:, 0].tolist()

dist = df.iloc[:, 1:].to_numpy()
#print(df)
#print(dist.shape)   # (29, 29)
#print(city_names[:5])
#print(df.columns.tolist())

def tsp_nearest_neighbor(dist, start=0):
    n = len(dist)
    visited = [start]
    current = start

    while len(visited) < n:
        next_city = min(
            (i for i in range(n) if i not in visited),
            key=lambda i: dist[current][i]
        )
        visited.append(next_city)
        current = next_city

    return visited
nn_route = tsp_nearest_neighbor(dist, start=0)
#print("NN Route (Index):", nn_route)

def route_length(route, dist):
    total = 0
    for i in range(len(route) - 1):
        total += dist[route[i], route[i + 1]]
    total += dist[route[-1], route[0]]
    return total

nn_length = route_length(nn_route, dist)
print("Route length according to Nearest Neighbour:", nn_length)

def route_to_names(route, city_names):
    return [city_names[i] for i in route]

print(route_to_names(nn_route, city_names))

def two_opt(route, dist):
    best = route
    best_len = route_length(best, dist)
    improved = True

    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route)):
                if j - i == 1:
                    continue

                new_route = best[:i] + best[i:j][::-1] + best[j:]
                new_len = route_length(new_route, dist)

                if new_len < best_len:
                    best = new_route
                    best_len = new_len
                    improved = True

        route = best

    return best, best_len

opt_route, opt_length = two_opt(nn_route, dist)

print("2-Opt length:", opt_length)
print(route_to_names(opt_route, city_names))