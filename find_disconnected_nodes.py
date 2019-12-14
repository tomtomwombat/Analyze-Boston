'''
This script loads the map data and generates an adjacency matrix for the graph.
A breadth first search is performed on the graph to identify and streets that
are not actually connected to the main street network.

After printing the disconnected nodes, I pasted this list in to 'parse_street_data.py'
and ignored all the streets that are disconnected.
'''




import random
from load_streets import Map

street_map = Map()
A = street_map.get_adj_matrix()

vis = [0 for i in range(len(A))] # 1 if vis[node] has been visited by BFS else 0
cur = random.randint(0, street_map.size - 1) # random start node
vis[cur] = 1

def get_neighbors(index):
    """Returns all the nodes that connect to index node"""
    next_nodes = []
    for j in range(street_map.size):
        if A[index][j] == 1 and vis[j] == 0:
            next_nodes.append(j)
            vis[j] = 1
    return next_nodes

nodes = get_neighbors(cur)

# BFS until no nodes in the stack
while len(nodes) > 0:
    new_nodes = []
    for n in nodes:
        new_nodes.extend(get_neighbors(n))
    nodes = new_nodes

# print all the disconnected nodes
disconnected = []
for i in range(len(vis)):
    if vis[i] == 0:
        disconnected.append(street_map.streets[i].name)
print(disconnected)
