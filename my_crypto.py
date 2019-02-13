# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 17:13:29 2018

@author: marce
"""
import os
import time
from datetime import datetime, date, timedelta
import pandas as pd
import re
import matplotlib.pyplot as plt

os.chdir("C:/Users/marce/Documents/6_DS_Projects/projects/1_Criptocurrencies_webscraping")

try:
    tseries = pd.read_csv("./tseries.csv", index_col = 0)
    tseries['Date'] = pd.to_datetime(tseries['Date'])

except:
    tseries = pd.DataFrame(columns = ['ID', 'Name', 'Price_USD', 'Change_24h_%','My_Amount', 
                                     'My_Amount_USD', 'My_Amount_BRL', 'Date', 'Deposited_BRL'])
    tseries['Date'] = pd.to_datetime(tseries['Date'])
   
#%% My Deposits
'''
Keep this information updated. 
Add an element as needed
'''
deposits =  {
            '18-10-2017': 1200.77, 
            '19-10-2017': 2199.98,
            '20-10-2017': 2000.00, 
            '29-10-2017': 500.02, 
            '30-10-2017': 500.00,
            '31-10-2017': 2650.07,
            '10-01-2017': 1000.00,
            }


deposits_df = pd.DataFrame.from_dict(deposits, orient = 'index')
deposits_df.reset_index(inplace = True)
deposits_df.columns = ['Date', 'Amount_BRL']
deposits_df['Date'] = pd.to_datetime(deposits_df['Date'])
tseries = pd.read_csv("./tseries.csv", index_col = 0)

#%% My Cryptocurrency Amount
'''
Keep this information updated. 
Add new line to 'my_crypto' as needed. 
Cryptocurrency ID needs to be the same as given by 'https://coinmarketcap.com/'
'''
my_crypto = {
            'BTC':     0.27309642,
            'ETH':     0.14985000,
            'WAVES':  19.99996000,
            'EOS':    29.97000000,
            'MIOTA':  54.94500000,
            'ADA':   125.87400000              
            }

new_crypto = {'XXX': 0.00000000}

my_crypto_df = pd.DataFrame.from_dict(my_crypto, orient = 'index')
my_crypto_df.reset_index(inplace = True)
my_crypto_df.columns = ['ID','My_Amount']

my_last_crypto = pd.read_csv("./my_crypto_df.csv", index_col = 0)
my_last_crypto['ID'] == my_crypto_df['ID']

my_crypto_df.to_csv("my_crypto_df.csv", float_format='%.8f')

'''
Extract currency table from website using pandas read_html
'''
url = 'https://coinmarketcap.com/all/views/all/'
read_currency_table = pd.read_html(url)[0]

url2 = 'http://www.infomoney.com.br/mercados/cambio'

dollar = pd.read_html(url2)[0].iloc[0,3]
dollar = float(dollar) / 1000

currency_table = pd.read_html(url)[0]

'''
Splits 'Name' column from scraped table into 'ID' and 'Name'
'''

currency_table.insert(1,'ID',0)
init = []
name = []
for n in currency_table['Name']:
    init.append(n.split()[0])
    name.append(n.split()[1])
currency_table['ID'] = init
currency_table['Name'] = name

#%% My currency table
'''
Subset currency table according to the currencies I possess, while also adding 'my_crypto' info.
'''
my_currency_table = pd.merge(currency_table, my_crypto_df, on = 'ID')

#%% Select relevant columns
my_currency_table = my_currency_table[['ID', 'Name', 'Price', 'My_Amount']]

#%% Adjust columns names
'''
Some names have spaces on it, which is not ideal. 
This part makes collumn names easier to handle
'''
name = ''
col_names = []
for n in my_currency_table.columns.values.tolist():
    try: 
        name = "_".join(n.split())
    except:
        name = n
    name = name.replace('(','')
    name = name.replace(')','')
    if any(n in name for n in ['Price','Market','Volume','Supply']):
        name = name + '_USD' 
    if ('Change' in n):
        name = name + '_%'    
    col_names.append(name)
    
my_currency_table.columns = col_names

#%% Adjust column types
'''
Function to remove special characters from column values.
Transforming to numeric when possible
'''
def adjust_type(s): 
    try:
        s = s.replace('$','')
        s = s.replace('%','')
        s = pd.to_numeric(s)
    except:
        pass
    return(s)
	
my_currency_table = my_currency_table.applymap(adjust_type)
	
#%% My_amount in dollar

my_currency_table['My_Amount_USD'] = my_currency_table['My_Amount'] * my_currency_table['Price_USD']
my_currency_table['My_Amount_BRL'] = my_currency_table['My_Amount_USD'] * dollar

#%% Yields 
'''
time_series 
'''
ts_day =  my_currency_table
ts_day['Date'] = pd.to_datetime(datetime.now())
ts_day['Deposited_BRL'] = deposits_df['Amount_BRL'].sum()

'''
Add information to Time Series Table only if date is new, that is, different from the last date on tseries
'''
try:
    if not (pd.to_datetime(datetime.now()).minute == tseries.loc[tseries.index[-1],'Date'].minute):
        tseries = pd.concat([tseries, ts_day], ignore_index = True, axis = 0)[list(tseries.columns)]
except:
    tseries = pd.concat([tseries, ts_day], ignore_index = True, axis = 0)[list(tseries.columns)]
	
import plotly
plotly.tools.set_credentials_file(username='marceltorretta@gmail.com', api_key='ye8VarVCx4Yq9IsX4BDl')

import plotly.plotly as py
import plotly.graph_objs as go

'''
Yields Time Series
Grouping table by date and getting sum of 'My_Amount_BRL of each group
'''
dates= []
amount_by_date = []
deposited_by_date = []

for name, group in tseries.groupby('Date', sort = False):
    dates.append(name)
    amount_by_date.append(group['My_Amount_BRL'].sum())
    deposited_by_date.append(group.loc[group.index[-1],'Deposited_BRL'])

d_total = go.Scatter(x = dates, y = amount_by_date, name = 'Total')
d_deposited = go.Scatter(x = dates, y = deposited_by_date, line = dict(shape = 'hv', dash = 'dash'), name = 'Cummulative Deposits')

data = [d_total, d_deposited]

l = []
l_name = [] 
d = []

for i in set(tseries['ID']):
    l = list(tseries.loc[tseries['ID'] == i]['My_Amount_BRL'])
    data.append(go.Scatter(x= dates, y = l, name = i, opacity = 0.5))
	
layout = dict(
    title='My Cryptocurrencies Portfolio',
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label='1m',
                     step='month',
                     stepmode='backward'),
                dict(count=6,
                     label='6m',
                     step='month',
                     stepmode='backward'),
                dict(count=1,
                    label='YTD',
                    step='year',
                    stepmode='todate'),
                dict(count=1,
                    label='1y',
                    step='year',
                    stepmode='backward'),
                dict(step='all')
            ])
        )   
    )
)

fig = dict( data = data, layout = layout)
plotly.offline.plot(fig)




    
    




