# Analyze Boston

![title](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/gui.png)

The goal of this project was to a path planning algorithm exclusive to Boston that avoiding areas with frequent crime. The project uses Boston crime data since 2015 and Boston street map data, both pulled from https://data.boston.gov/. The crimes.csv file was to large to add to the GitHub repo, so here is the link: https://data.boston.gov/dataset/crime-incident-reports-august-2015-to-date-source-new-system. This project also uses the tkinter python library for graphics, which is more involved to install than other normal python modules: https://tkdocs.com/tutorial/install.html.


## Inital Processing of .geojson Data
Before anything could be done, I needed to parse the "street_data.json" into a graph object stored in a table and remove any disconnected sections of the graph. To create a graph, "parse_street_data.py" identifies intersections in streets using their latitude and longitude coordinates and creates a new node. Nodes are labeled as consecutive integers 0, 1, 2... etc. A second pass is done to determine the edges by using the (latitude,longitude):node mapping. After the all the nodes an edges were parsed, disconnected sections of the graph were identified by a simple BFS. Disconnected street names were recorded and ignored during further processing. This code is found in src/Preprocessing and the final product is "edge_data.csv".

The project uses 3 main algorithms: Dijkstra's, spectral clustering, and sarimax. I have already studied Dijkstra's algorithm, but spectral clustering and sarimax was new to me and I wanted to learn and use them.

## Setup
The bulk of the computational math in the project is setting up the clusters and crime predictions. "setup_main.py" orchestrates the whole process.

## Spectral Clustering
This runs the spectral clustering algorithm on the graph. The Map object in "load_streets.py" produced an adjacency matrix A, where `A[i][j] = A[j][i]` and `A[i][j] = 1/d`, where `d` is the distance from node `i` to node `j`. `D` is the diagonal degree matrix, where `D[i][i]` is the number of edges coming out of node `i`. The laplacian matrix, `L`, is defined as `D - A`, and is also symmetric. The normalized laplacian, Lnorm, is defined as `I - (D^-1/2)L((D^-1/2))`. The k eigenvectors corresponding to the k smallest eigenvalues of Lnorm become n points in k dimensions where the entries of point i are the ith entries of each of the k eigenvectors. These points are fed into a standard clustering algorithm such as k-means.

Spectral clustering on Boston graph with 10 groups:
![An example of spectral clustering on the Boston streets](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/cluster.png)

### Sorting Crimes into Clusters
After clustering the graph, I needed to then match the crimes with the geographical colored groups on the map. The problem looked as follows:
![The problem looked as follows](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/overlap.png)
The black dots represent an instance of a crime at that location, and the map is overlapped with these crimes. You can see most of the crimes overlap perfectly with a street, but some don't. To match these crimes with a colored group in the graph, I used an algorithm similar to BFS. First, I rounded each of the coordinates of the nodes and placed into a cell of a grid of 1100x700 grid. Then, for each crime I rounded it's coordinates and found its corresponding cell in the grid. If the cell that the crime was in also contained a node, then the crime became the same group as the node. Otherwise the algorithm looked for the closest cell that contained a node using simple search pattern of a an expanding square around the original crime's cell.

## Time Series Analysis
Each crime was now associated with a geographical group. The average number of crimes per day on a bi-monthly basis for each cluster was calculated and stored in Data/BiMonthly_Crimes.csv. The first thing I noticed was that crimes rate are seasonal. I think this is because people are generally more likely to be out and about during warmer temperatures and at home during the cold.
Below is the collective crime rates for each cluster.
![monthly](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/monthly_crimes.png)
Because the frequencies are seasonal, I decided to use time series analysis, specifically the SARIMA model from the statsmodels library. SARIMA stands for seasonal (S) auto regressive (AR) integrated (I) moving average (MA). For the project I did not go into depth to understand of the model. I can only explain the basics.

### Autoregressive
An autoregressive model is where a data point can be forcasted by linear combination of past values in the data set:
`y[t] = c + a[0]*y[t-1] + ... + a[p-1]*y[t-p] + ε[t]`, where `y` is the data vaules and `a` is an array of constants and `p` is a parameter of how many past values to use to predict `y[t]`. An autoregrssive model with p is denoted as AR(p). The restictions for `a[i]` for a AR(1) model is that `-1 < a[0] < 1` (there is only 1 element in `a`). For a AR(2) the restrictions are more complicated: `-1 < a[1] < 1`, `a[0] + a[1] > -1`, and `a[0] - a[1] < 1`. The restrictions for AR(p), p > 2 are more complicated and are dealt within the the statsmodels package.

### Moving Average
The moving average model is very similar to the autoregressive model except that it uses a linear combination of `ε[t]` instead of the y values. MA(q) is a model where `y[t] = c + b[0]*ε[t-1] + ... + b[q-1]*ε[t-q] + ε[t]`. Here the next element depends on the past `q` errors from previous calculations.

### Differencing
Differencing is the process of transforming the data such that the new values become the difference between consecutive old values. For example given a list `y = [1, 1, 2, 3, 5]` the first difference is `y' = [0, 1, 1, 2]`. 

### ARIMA
The ARIMA model is the AR itegrated with the MA. The 3 parameters of an ARIMA model are p,d, and q, where p is the AR(p) order, d is the number of differences used on the data, and q is the order of MA(q). The expansion of the model is 
`z[t] = c + (a[0]*z[t-1] + ... + a[p-1]*y[t-p]) + (b[0]*ε[t-1] + ... + b[q-1]*ε[t-q]) + ε[t]`, where `z` is the dth difference of `y`. 

### SARIMA
Finally a seasonaly component must be added. The difference between seasonal and cyclic behavior is that seasonal is cyclic but alligned with the seasons or months. The new paramenters of the SARIMA model are (P,D,Q) and m. m is number of observations per year, so if crimes frequencies were recorded monthly m would be 12 and for this project crime frequencies were calculated bi monthly so m is 24.

To find the best (p,d,q) and (P,D,Q) parameters for the model I used a "grid search" meaning that I tried all combinations of the parameters over a small range and compared their performance. The performance of the model with certain parameters was measured by the Akaike’s Information Criterion (AIC). AIC = -2log(L) + 2(p + q + k + 1). L is a likelyhood function of y, the data, and k = 0 if c = 0 else k = 1.

After picking the set of parameters with the smallest AIC, I tested it on all the crimes in Boston. 
![pred 1](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/monthly_prediction.png)

Using the same model  I then predicted the crime frequencies about 2 years into the future for each geographical cluster. The image below is an example plot of such prediction.
![pred 1](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/bimonthly_predictions.png)
It is less clear that the frequencies for a specifc cluster is seasonal, however you can see a slight peak every 24 halfmonths after the starting point of August (summer is highest frequencies of crimes). The orange prediction line predicts a spike around 120 half months after August 2015, which is the summer of 2020. The uncertaintity of the SARIMA model's predictions increases the further into the future they are. 

There is a trade off with number of clusters and accuracy of the predictions. Obviosuly the predictions and seasonality are more obvious when using all the crime data, but a single cluster would not help much trying to disguish different geographical locations from each other based off of crime. If a 100 clusters were used I would have high "resolution" in the graph but the edge weights would not be accurate as I would not have much data for each SARIMA model. I chose 15 clusters because I thought it was the middle ground, this is just arbitrary. 

## Constructing the Graph

Finally I had the historical crime frequenceis and the predicted crime frequencies for all 15 clusters in Boston. Each edge of nodes u and v was weighted by a linear combination of its "crime value" and length. The crime value was determined by the crime rate of the cluster u was in plus the crime rate of the cluster v was in and divided by two and then multilied by the length of the street. This was to ensure that when crossing a high crime rate area that the shortest path is taken within that area. When drawing the map I colored the clusters based on their crime rates. Red mean higher crime rate and green means lower crime rate. As you change the time scale you can see that colors of each cluster change slightly. The % crime weight slider changes the values of the edges by adjusting the weight of the crime value and length. So if % crime weight was at 50 then the value of each edge is `.5*crime_value + .5*length`.

The graph search algorithm used was Dijkstra's algorithm which is a good algorithm to find minimum path from A to B in a graph. Below is the path when the % crime weight is 0, meaning that the path completly ignored the crime rates of the streets. ![comp1](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/compare1.png)
You can see that the path goes straight through the red area (high crime area). After turing the % crime weight to 100, the length of the path is ignored and the crime rates are fully considered. 
![comp2](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/compare2.png)
You can see that the red region is totally avoided! Instead the algorithm finds a safer route through the greener areas around the red region.

## Further improvements

### Crime Rates throughout the Day
The main improvment I thought of was a path planning algorithm that considered the time of day. It is quite obvious that the crime frequencies during the day are not random. Below is a plot of the number of crimes into total since 2015 vs when in the day they occurred. 
![hour](https://github.com/thomaspendock/Analyze-Boston/blob/master/Images/crimes_per_hour.png) 
You can see that minimum rate is around 4am to 6am and the maximum is during the afternon. The "spikey" nature is interesting. I think this is because police officers are more likely to record the time as a whole number for example 12:00 instead of 12:03, hence the upward spike during whole number hours. It would have been good to also incorporate a model for each cluster based off of the time of day and then use that in the edge values.

### Different Types of Crimes
The crimes.csv file also contained the type of crime that was committed, which this project completely ignore. The project could have not used geographical clusters and instead used a linear combination of predicted rates for multiple different types of crimes. Say someone wasn't worried about being mugged but was worried about having their car stolen or being in a car accident, then the user could tell the program to weight the car crashes rate or car theft rate more highly.
