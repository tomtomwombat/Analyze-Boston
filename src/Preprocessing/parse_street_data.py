'''
Here we parse the raw street data. We create a graph where each node is
an intersection of streets.
'''

import json
import os

WIDTH = 1200  # width of window
HEIGHT = 800  # height of window

min_lat = 100000
min_long = 100000
max_lat = -100000
max_long = -100000
lats = []
longs = []
st_ids = []
lens = []
speedlimits = []


# The list below is a list of disconnected streets in the raw data
# It is found by running 'find_disconnected_nodes.py'

bad_names = ['Interstate_93__16977', 'Trinity__12530', 'Seymour__12056', 'Albert__11941', 'Thompson__12548',
             'Ramp__17032', 'Ramp__17054', 'Ramp__16887', 'Thompson__11940', 'Sever__12054', "Copp's_Hill__11969",
             'Interstate_93__16976', 'Third_Street__11939', 'Carlson__1195', 'Ramp__17009', 'Bowdoin__11587',
             'Interstate_93__16955', "Saint_Paul's__16818", 'William_C_Kelly__18443', 'Bryon__17017',
             "Saint_Mary's__17046", 'Playstead__11942', 'Westgate__15736', 'Bonad__18251', 'Interstate_93__16889',
             'Ramp__11675', "Saint_Mary's__15535", 'Ocean__18558', 'Monmouth__11933', 'Long_Island__18551',
             'Lovell_Island__17887', 'Bryon__15572', 'Liberty__17856', 'Long_Island__18555', 'Ramp__16963',
             'Long_Island__18552', 'Ocean__18557', 'Leverett__12044', 'Bonad__11113', 'Weston__11990', 'Tafts__18562',
             'Bonad__18250', 'Rev_Anthony_Ciao__17877', 'Trelawney__12055', 'Interstate_93__16888',
             'Interstate_93__16978', 'Rev_Anthony_Ciao__17878', 'Deer_Island__18564', 'Castle_Island__11040',
             'Bryon__15571', 'Thornton__18242', 'Long_Island__18550', 'Ramp__16956', 'Interstate_93__11690',
             'Wilder__17862', 'Bryon__16987', 'Quincy__11962', 'Vernon__16723', 'Greenwood__11134', 'Ocean__18559',
             'Waverly__11105', 'Northern__18528', 'International__12560', 'Spectacle_Isle__11071', 'Long_Island__18554',
             'Ramp__16886', 'Winthrop__12053', 'Tafts__18563', 'Long_Island__18553', 'Interstate_93__16908',
             'Post_Office__11583', 'Broadlawn__16986', 'Long_Island__18556', 'Broadlawn__15573', 'Tafts__18561',
             'Trinity__12531', 'Copley__17063', 'Reservoir__18662', 'Ramp__17044', 'Sherman__17039', 'Ramp__17010']

data_path = os.path.join(os.path.abspath('../..'), 'Data')
with open(os.path.join(data_path, 'street_data.json'), 'r') as json_file:
    data = json.load(json_file)
    for k in data:

        if '_'.join(k.split(' ')) in bad_names: # Ignore disconnected node
            print(k)
            continue

        coords = list(data[k]['coordinates'])
        zcoords = list(zip(*coords))
        lts = zcoords[1]
        lngs = zcoords[0]

        # I used this bool to 'zoom in' on the map by only accepting
        # streets within a small subsection of Boston
        # if lts[0] > -71.05 or lts[0] < -71.15: continue
        # if lngs[0] > 42.25 or lngs[0] < 42.2: continue

        min_lat = min(min_lat, min(lts))
        min_long = min(min_long, min(lngs))
        max_lat = max(max_lat, max(lts))
        max_long = max(max_long, max(lngs))

        st_ids.append(k)
        lats.append(list(lts))
        longs.append(list(lngs))
        lens.append(data[k]['SHAPElen'])
        speedlimits.append(data[k]['SPEEDLIMIT'])

scale_long = HEIGHT / (max_long - min_long)
scale_lat = WIDTH / (max_lat - min_lat)


# Street intersections will become nodes in the graph
nodes = set() # Keep track of all the unique street ends coordinates.
for i in range(len(lats)):
    street_lats = lats[i]
    street_longs = longs[i]

    lat1 = street_lats[0]
    lat2 = street_lats[-1]
    long1 = street_longs[0]
    long2 = street_longs[-1]
    nodes.add((lat1, long1))
    nodes.add((lat2, long2))

coord_to_id = {} # Map street intersection coordinates to node id
count = 0
for lat, long in nodes:
    coord_to_id[(lat, long)] = count
    count += 1

with open(os.path.join(data_path, 'edge_stats.txt'), 'w+') as f:
    f.write(str(count) + '\n')
    f.write(str(min_lat) + ',' + str(min_long) + '\n')
    f.write(str(max_lat) + ',' + str(max_long) + '\n')

with open(os.path.join(data_path, 'edge_data.csv'), 'w+') as f:
    f.write('NODE1,NODE2,NAME,LENGTH,SPEEDLIMIT,SHAPE\n')
    for i in range(len(lats)):
        street_lats = lats[i]
        street_longs = longs[i]

        lat1 = street_lats[0]
        lat2 = street_lats[-1]
        long1 = street_longs[0]
        long2 = street_longs[-1]

        node1 = coord_to_id[(lat1, long1)]
        node2 = coord_to_id[(lat2, long2)]

        # node1 node2 name len speedlimit coords
        f.write(str(node1) + ',')
        f.write(str(node2) + ',')
        f.write('_'.join(st_ids[i].split(' ')) + ',')
        f.write(str(lens[i]) + ',')
        f.write(str(speedlimits[i]) + ',')

        line = ' '.join([str(street_lats[j]) + ',' + str(street_longs[j]) \
                         for j in range(len(street_lats))])
        f.write('\"' + line + '\"')
        f.write('\n')
