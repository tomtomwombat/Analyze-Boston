import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
import os

data_path = os.path.join(os.path.abspath('../..'), 'Data')


warnings.filterwarnings("ignore")

days_per_month = [31, 28, 31, 30,
                  31, 30, 31, 31,
                  30, 31, 30, 31]

days_per_halfmonth = []
for month in days_per_month:
    days_per_halfmonth.append(month // 2)
    days_per_halfmonth.append(month // 2 + (month % 2))

month_to_days = [sum(days_per_month[:i]) for i in range(12)]
halfmonth_to_days = [sum(days_per_halfmonth[:i]) for i in range(24)]

def get_biweekly_dates(start, num):
    dates = []
    y, m, d = start#(2019, 9, 1)  # tuple([int(x) for x in df['date'][-1].split('-')])
    for i in range(num+1):
        date = '%d-%d-%d' % (y, m, d)
        if d == 1:
            d = days_per_halfmonth[m * 2 - 1]
        elif m == 12:
            d = 1
            m = 1
            y += 1
        else:
            d = 1
            m += 1

        dates.append(date)
    return dates

def predict_crime_freq(df, pred_steps):

    y = df['freq']

    my_order = (2, 1, 1)
    my_seasonal_order = (2, 1, 0, 24)
    mod = SARIMAX(y,
                  order=my_order,
                  seasonal_order=my_seasonal_order,
                  enforce_stationarity=False,
                  enforce_invertibility=False)
    results = mod.fit()

    # Producing and Visualizing Forecasts
    pred_uc = results.get_forecast(steps=pred_steps).predicted_mean.tolist()
    for i in range(len(pred_uc)):
        pred_uc[i] = max(0, pred_uc[i])

    return pred_uc


def predict_all_crimes(num_clusters):

    for i in range(num_clusters):
        file_name = os.path.join(data_path, 'BiMonthly_Crimes/monthly_crime%d.csv'%i)

        # Add data to this data frame
        df = pd.read_csv(file_name)

        # Predict using this data frame
        df_predict = pd.read_csv(file_name, parse_dates=['date'], index_col='date')
        pred_list = predict_crime_freq(df_predict, 50)


        pred_dict = {'date': [], 'freq': []}
        dates = get_biweekly_dates((2019,9,1), len(pred_list))
        for j in range(len(pred_list)):
            pred_freq = pred_list[j]
            pred_dict['date'].append(dates[j])
            pred_dict['freq'].append(pred_freq)

        pred_dict['date'] = list(df['date']) + pred_dict['date']
        pred_dict['freq'] = list(df['freq']) + pred_dict['freq']
        predicted_crimes = pd.DataFrame(pred_dict)
        p = os.path.join(data_path, 'BiMonthly_Crimes_with_Forecast/monthly_crime%d.csv'%i)
        predicted_crimes.to_csv(p)








'''

p = d = q = range(0, 3)
pdq = list(itertools.product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
print('Examples of parameter combinations for Seasonal ARIMA...')
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[2]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[3]))
print('SARIMAX: {} x {}'.format(pdq[2], seasonal_pdq[4]))

count = 0
log = open('log.txt', 'w+')
for param in pdq:
    for param_seasonal in seasonal_pdq:
        count += 1
        print(count, len(pdq) * len(seasonal_pdq))
        try:
            model = SARIMAX(df['freq'],order=param, seasonal_order=param_seasonal,enforce_stationarity=False,enforce_invertibility=False)
            results = model.fit(disp=0)
            log_line = 'ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic)
            log.write(log_line+'\n')

        except:
            continue

log.close()

'''
