import random
from math import sqrt
import pandas as pd
from setup.graph import Graph

import os
data_path = os.path.join(os.path.abspath('..'), 'Data')

class Street:
    def __init__(self, node1, node2, name, length, speed_limit, coords):
        self.coords = coords
        self.node1 = node1
        self.node2 = node2
        self.name = name
        self.speed_limit = speed_limit
        self.length = length

class Map:
    def __init__(self):

        self.min_length = 1000
        self.max_length = -1

        print('Loading map')
        self.streets = {}
        with open(os.path.join(data_path, 'graph_stats.txt'), 'r') as f:
            lines = f.read().split('\n')
            self.size = int(lines[0])
            self.min_lat, self.min_long = [float(x) for x in lines[1].split(',')]
            self.max_lat, self.max_long = [float(x) for x in lines[2].split(',')]

        edge_data = pd.read_csv(os.path.join(data_path, 'edge_data.csv'))
        for i in range(len(edge_data['NODE1'])):
            node1 = int(edge_data['NODE1'][i])
            node2 = int(edge_data['NODE2'][i])
            name = edge_data['NAME'][i]
            length = float(edge_data['LENGTH'][i])
            self.min_length = min(length,self.min_length)
            self.max_length = max(length, self.max_length)
            limit = int(edge_data['SPEEDLIMIT'][i])
            coords = [tuple(coord.split(',')) for coord in edge_data['SHAPE'][i].split(' ')]
            coords = [(float(x), float(y)) for x, y in coords]

            self.streets[tuple(sorted((node1, node2)))] = \
                Street(node1, node2, name, length, limit, coords)

        print('Loaded Map.')

    def get_adj_matrix(self):
        adj_matrix = [[0.0 for j in range(self.size)] for i in range(self.size)]
        for street in self.streets.values():
            adj_matrix[street.node1][street.node2] = 1 / street.length
            adj_matrix[street.node2][street.node1] = 1 / street.length
        return adj_matrix


    def to_graph(self):
        # needs graph
        pass
