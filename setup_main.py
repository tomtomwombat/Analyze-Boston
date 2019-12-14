import load_streets
import clustering
import calc_crime_freq
import time_series


WIDTH = 1100
HEIGHT = 700
num_clusters = 25

street_map = load_streets.Map()
scale_long = HEIGHT / (street_map.max_long - street_map.min_long)
scale_lat = WIDTH / (street_map.max_long - street_map.min_long)

clustering.cluster_graph(street_map, num_clusters)
clustering.cluster_crimes(street_map, WIDTH, HEIGHT)

freqs = calc_crime_freq.calc_crime_counts(num_clusters)
calc_crime_freq.write_crime_frequencies(freqs, num_clusters)
print('Generated %d files in \'Monthly_Crimes\'')

time_series.predict_all_crimes(num_clusters)
print('Generated %d files in \'BiMonthly_Crimes_with_Forecast\'')
