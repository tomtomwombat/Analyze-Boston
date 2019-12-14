# Analyze Boston

![title](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/gui.png)

The goal of this project was to a path planning algorithm exclusive to Boston that avoiding areas with frequent crime. The project uses Boston crime data since 2015 and Boston street map data, both pulled from https://data.boston.gov/. The crimes.csv file was to large to add to the GitHub repo, so here is the link: https://data.boston.gov/dataset/crime-incident-reports-august-2015-to-date-source-new-system. This project also uses the tkinter python library for graphics, which is more involved to install than other normal python modules: https://tkdocs.com/tutorial/install.html.

Before anything could be done, I needed to parse the "street_data.json" into a graph object stored in a table and remove any disconnected sections of the graph. To create a graph, "parse_street_data.py" identifies intersections in streets using their latitude and longitude coordinates and creates a new node. Nodes are labeled as consecutive integers 0, 1, 2... etc. A second pass is done to determine the edges by using the (latitude,longitude):node mapping. After the all the nodes an edges were parsed, disconnected sections of the graph were identified by a simple BFS. Disconnected street names were recorded and ignored during further processing. This code is found in src/Preprocessing and the final product is "edge_data.csv".

The project uses 3 main algorithms: Dijkstra's, spectral clustering, and sarimax. I have already studied Dijkstra's algorithm, but spectral clustering and sarimax was new to me and I wanted to learn and use them.

The bulk of the computational math in the project is setting up the clusters and crime predictions. "setup_main.py" orchestrates the whole process.
(1) This runs the spectral clustering algorithm on the graph. The Map object in "load_streets.py" produced an adjacency matrix A, where A[i][j] = A[j][i] and A[i][j] is 1/d, where d is the distance from node i to node j. D is the diagonal degree matrix, where D[i][i] is the number of edges coming out of node i. The laplacian matrix, L, is defined as D - A, and is also symmetric. The normalized laplacian, Lnorm, is defined as I - (D^-1/2)L((D^-1/2)). The k eigenvectors corresponding to the k smallest eigenvalues of Lnorm become n points in k dimensions where the entries of point i are the ith entries of each of the k eigenvectors. These points are fed into a standard clustering algorithm such as k-means.

Spectral clustering on Boston graph with 10 groups:
![An example of spectral clustering on the Boston streets](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/cluster.png)

(2) After clustering the graph, I needed to then match the crimes with the geographical colored groups on the map. The problem looked as follows:
![The problem looked as follows](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/overlap.png)
The black dots represent an instance of a crime at that location, and the map is overlapped with these crimes. You can see most of the crimes overlap perfectly with a street, but some don't. To match these crimes with a colored group in the graph, I used an algorithm similar to BFS. First, I rounded each of the coordinates of the nodes and placed into a cell of a grid of 1100x700 grid. Then, for each crime I rounded it's coordinates and found its corresponding cell in the grid. If the cell that the crime was in also contained a node, then the crime became the same group as the node. Otherwise the algorithm looked for the closest cell that contained a node using simple search pattern of a an expanding square around the original crime's cell.

(3) Each crime was now associated with a geographical group. The average number of crimes per day on a bi-monthly basis for each cluster was calculated and stored in Data/BiMonthly_Crimes.csv. The first thing I noticed was that crimes rate are seasonal. I think this is because people are generally more likely to be out and about during warmer temperatures and at home during the cold.
![monthly](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/monthly_crimes.png)

Using the SARIMAX model from the statsmodels I 
