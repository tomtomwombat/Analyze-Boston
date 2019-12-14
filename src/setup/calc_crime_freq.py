'''
Reads crime data and calculates the average number of crimes per day for each 2 weeks in each community.
'''

import pandas as pd
from setup.time_series import get_biweekly_dates
import os

data_path = os.path.join(os.path.abspath('../..'), 'Data')
days_per_month = [31, 28, 31, 30,
                  31, 30, 31, 31,
                  30, 31, 30, 31]

days_per_halfmonth = []
for month in days_per_month:
    days_per_halfmonth.append(month // 2)
    days_per_halfmonth.append(month // 2 + (month % 2))
month_to_days = [sum(days_per_month[:i]) for i in range(12)]
halfmonth_to_days = [sum(days_per_halfmonth[:i]) for i in range(24)]


def calc_crime_counts(num_communities):
    print('reading csv')
    data = pd.read_csv(os.path.join(data_path, 'colored_crimes.csv'))
    print('read csv')

    # (date : count) dictionary for each color
    biweekly_crimes = [{} for i in range(num_communities)]
    all_dates = get_biweekly_dates((2015, 6, 1), 102)
    for d in all_dates:
        print(d)
        for i in range(num_communities):
            k = tuple([int(x) for x in d.split('-')])
            biweekly_crimes[i][k] = 0

    for i in range(len(data)):



        # Print parsing progress
        if i % 100000 == 0: print(i, len(data))

        # Parse string
        dt_str = data['TIME'][i]
        str_date = dt_str.split(' ')[0]
        yr, mn, dy = str_date.split('-')

        # Figure out which half of the month the date is in
        first_half = days_per_month[int(mn)-1]//2
        day = 1 if int(dy) <= first_half else days_per_month[int(mn)-1] - first_half
        rounded_date = (int(yr), int(mn), int(day))

        color = data['COLOR'][i]

        # Increment count
        if rounded_date in biweekly_crimes[color]:
            biweekly_crimes[color][rounded_date] += 1
        else:
            biweekly_crimes[color][rounded_date] = 1



    return biweekly_crimes

def write_crime_frequencies(biweekly_crimes, num_communities):
    for i in range(num_communities):
        with open(os.path.join(data_path, 'BiMonthly_Crimes/monthly_crime' + str(i) + '.csv'), 'w+') as f:
            f.write('\"date\",\"freq\"\n')

            # We skip the first and last dates because they have incomplete data
            for (y, m, d) in sorted(biweekly_crimes[i].keys())[1:-1]:
                count = biweekly_crimes[i][(y, m, d)]
                num_days = days_per_halfmonth[2 * m - 2 + int(d != 1)]

                freq = float(count) / float(num_days)
                f.write('%d-%d-%d,%f\n' % (y, m, d, freq))
