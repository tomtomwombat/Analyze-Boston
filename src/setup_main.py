import setup.load_streets
import setup.clustering
import setup.calc_crime_freq
import setup.time_series
import os, shutil

data_path = os.path.join(os.path.abspath('..'), 'Data')

def delete_folder_contents(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e: print(e)


WIDTH = 1100
HEIGHT = 700
num_clusters = 25

street_map = load_streets.Map()
scale_long = HEIGHT / (street_map.max_long - street_map.min_long)
scale_lat = WIDTH / (street_map.max_long - street_map.min_long)

print('Spectral clustering graph...')
clustering.cluster_graph(street_map, num_clusters)
print('Clustering crimes...')
clustering.cluster_crimes(street_map, WIDTH, HEIGHT)
print('done clustering.')


print('Deleting old data in Data/BiMonthly_Crimes')
delete_folder_contents(os.join(data_path, 'BiMonthly_Crimes'))

freqs = calc_crime_freq.calc_crime_counts(num_clusters)
calc_crime_freq.write_crime_frequencies(freqs, num_clusters)
print('Generated %d files in \'BiMonthly_Crimes\'')

print('Deleting old data in Data/BiMonthly_Crimes_with_Forecast')
delete_folder_contents(os.join(data_path, 'BiMonthly_Crimes'))

time_series.predict_all_crimes(num_clusters)
print('Generated %d files in \'BiMonthly_Crimes_with_Forecast\'')


print('done.')
