from setup.graph import Graph
import random
import tkinter
import pandas as pd
from setup.load_streets import Map
import math
import os

data_path = os.path.join(os.path.abspath('..'), 'Data')



WIDTH = 1100 # width of window
HEIGHT = 700 # height of window
num_cats = 25

street_map = Map()
scale_long = HEIGHT / (street_map.max_long - street_map.min_long)
scale_lat = WIDTH / (street_map.max_long - street_map.min_long)

def canvas_coords(lat, long):
    lat -= street_map.min_lat
    long -= street_map.min_long

    lat *= scale_lat
    long *= scale_long
    return lat,long

colors = []
cat_sizes = [0 for i in range(num_cats)]
with open(os.path.join(data_path, 'node_colors.txt'), 'r') as f:
    line = f.read().split(' ')
    for l in line:
        try:
            colors.append(int(l))
            cat_sizes[int(l)] += 1
        except: pass

# Date,Cat --> val
dates = []
crime_vals = {}
min_crime = 10000
max_crime = -1
for i in range(num_cats):
    file_name = os.path.join(data_path, 'BiMonthly_Crimes_with_Forecast/monthly_crime%d.csv'%i)
    predictions = pd.read_csv(file_name)
    for j in range(len(predictions)):
        key = (i,predictions['date'][j])
        if i == 0: dates.append(predictions['date'][j])
        val = predictions['freq'][j]/float(cat_sizes[i])
        min_crime = min(min_crime, val)
        max_crime = max(max_crime, val)
        crime_vals[key] = val


def crime_to_color(val):
    global min_crime, max_crime
    rng = max_crime - min_crime
    norm_crime = 1 + (val - min_crime)/rng

    log_norm = math.log(norm_crime)/math.log(2)
    final_norm = log_norm
    return (int(255*final_norm), int(255*(1-final_norm)),0)

def get_edge_weight(crime_val, length):
    global crime_val_weight

    norm_crime = (crime_val - min_crime)/ \
                 (max_crime - min_crime)

    norm_length = (length - street_map.min_length) / \
                  (street_map.max_length - street_map.min_length)
    norm_length *= street_map.min_length



    return crime_val_weight * norm_crime + (1 - crime_val_weight) * norm_length

DATE = '2015-6-15'
SRC = random.randint(0, street_map.size - 1)
DEST = random.randint(0, street_map.size - 1)
crime_val_weight = 0

print(num_cats)
for i in range(num_cats):
    print(crime_vals[(i,DATE)])
print(min_crime, max_crime)


graph = Graph(street_map.size)
for street in street_map.streets.values():
    cat1 = colors[street.node1]
    cat2 = colors[street.node2]
    crime_val1 = crime_vals[(cat1,DATE)]
    crime_val2 = crime_vals[(cat2,DATE)]

    edge_weight = get_edge_weight((crime_val1+crime_val2)/2, street.length)
    graph.addEdge(street.node1, street.node2, edge_weight)
    graph.addEdge(street.node2, street.node1, edge_weight)

path = graph.dijkstra(SRC, DEST)

def update_edge_weights():
    global DATE

    for i in range(street_map.size):
        for j in range(len(graph.graph[i])):
            node1 = i
            node2 = graph.graph[i][j][0]

            cat1 = colors[node1]
            cat2 = colors[node2]
            crime_val1 = crime_vals[(cat1, DATE)]
            crime_val2 = crime_vals[(cat2, DATE)]

            edge_weight = get_edge_weight((crime_val1 + crime_val2) / 2, street.length)

            graph.graph[i][j][1] = edge_weight

window = tkinter.Tk()
canvas = tkinter.Canvas(window, bg='black', height=HEIGHT, width=WIDTH)
canvas.pack(side='left')

street_lines = {}
for street in street_map.streets.values():
    cat1 = colors[street.node1]
    crime_val1 = crime_vals[(cat1, DATE)]
    color = '#%02x%02x%02x' % crime_to_color(crime_val1)
    street_shape = []
    for i in range(1, len(street.coords)):
        start_lat, start_long = canvas_coords(*street.coords[i - 1])
        end_lat, end_long = canvas_coords(*street.coords[i])

        street_shape.append(canvas.create_line(start_lat, start_long,
                                               end_lat, end_long,
                                               fill=color, width=1))
    street_lines[(street.node1, street.node2)] = street_shape
def redraw_directions(path):
    for d in directions:
        canvas.delete(d)
    y = 105
    prev_street_name = None
    for i in range(1, len(path)):
        street = street_map.streets[tuple(sorted((path[i-1],path[i])))]
        name = ' '.join(street.name.split('__')[0].split('_'))
        if name == prev_street_name: continue
        current_date_text = canvas.create_text(WIDTH - 100,y,fill="white",
                                       font="Times 15 italic bold",
                                       text=name)
        directions.append(current_date_text)
        y+=17
        prev_street_name = name

def delete_path(path):
    for i in range(1, len(path)):

        street = street_map.streets[tuple(sorted((path[i-1],path[i])))]

        cat1 = colors[street.node1]
        crime_val1 = crime_vals[(cat1, DATE)]
        color = '#%02x%02x%02x' % crime_to_color(crime_val1)

        for(ID) in street_lines[(street.node1,street.node2)]:
            canvas.itemconfig(ID, fill=color, width=1)

def color_path(path):
    for i in range(1, len(path)):
        street = street_map.streets[tuple(sorted((path[i-1],path[i])))]

        for(ID) in street_lines[(street.node1,street.node2)]:
            canvas.itemconfig(ID, fill='cyan', width=3)
            
tkinter.Label(window, text="Date:").pack()
date_scale = tkinter.Scale(window, from_=0, to=len(dates)-1, orient='horizontal')
date_scale.pack()



def rand_src():
    global SRC, path
    SRC = random.randint(0, street_map.size - 1)
    delete_path(path)
    path = graph.dijkstra(SRC, DEST)
    color_path(path)
    redraw_directions(path)

def rand_dest():
    global DEST, path
    DEST = random.randint(0, street_map.size - 1)
    delete_path(path)
    path = graph.dijkstra(SRC, DEST)
    color_path(path)
    redraw_directions(path)

src_button = tkinter.Button(window, text='Random Start', command=rand_src)
dest_button = tkinter.Button(window, text='Random Destination', command=rand_dest)

src_button.pack()
dest_button.pack()

tkinter.Label(window, text="% Crime weight").pack()
weight_scale = tkinter.Scale(window, from_=0, to=100, orient='horizontal')
weight_scale.pack()

current_date_text = canvas.create_text(WIDTH - 150,40,fill="white",
                                       font="Times 20 italic bold",
                                       text='Crime rates on ' + DATE)
direc_text = canvas.create_text(WIDTH - 100,80,fill="white",
                                       font="Times 20 italic bold",
                                       text='Directions:')
directions = []

def mouse_release(event):
    global DATE, path, crime_val_weight

    if DATE != dates[date_scale.get()]:
        DATE = dates[date_scale.get()]
        update_edge_weights()
        draw_streets()
        path = graph.dijkstra(SRC, DEST)
        color_path(path)
        canvas.itemconfig(current_date_text,
                          text='Crime rates on ' + DATE)
        redraw_directions(path)

    if crime_val_weight != float(weight_scale.get()) / 100:
        crime_val_weight = float(weight_scale.get()) / 100
        update_edge_weights()
        delete_path(path)
        path = graph.dijkstra(SRC, DEST)
        color_path(path)
        redraw_directions(path)

def draw_streets():
    # Draw the streets
    for street in street_map.streets.values():
        cat1 = colors[street.node1]
        crime_val1 = crime_vals[(cat1, DATE)]
        color = '#%02x%02x%02x' % crime_to_color(crime_val1)

        IDs = street_lines[(street.node1, street.node2)]

        for ID in IDs:
            canvas.itemconfig(ID, fill=color, width=1)

color_path(path)
redraw_directions(path)

print('done')

window.bind('<ButtonRelease-1>', mouse_release)
window.mainloop()
print('done')
