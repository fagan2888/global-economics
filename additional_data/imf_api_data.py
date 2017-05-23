import requests
import pandas as pd
import os, csv, re, sys

# URL for the IMF JSON Restful Web Service, IFS database, and Australian export prices series

#import price index data (indicator: PMP_IX)
#export price index data (indicator: PXP_IX)
url = 'http://dataservices.imf.org/REST/SDMX_JSON.svc/CompactData/IFS/Q.AU.PXP_IX.?startPeriod=1957&endPeriod=2017'

# Get data from the above URL using the requests package
data = requests.get(url).json()

# Load data into a pandas dataframe
auxp = pd.DataFrame(data['CompactData']['DataSet']['Series']['Obs'])
baseyr = auxp[-1]['@BASE_YEAR'] 

# Show the last five observiations
print(auxp.tail())

# Rename columns
auxp.columns = ['baseyear','auxp','date']

# Set the price index series as a float (rather than string)
auxp.auxp = auxp.auxp.astype(float)

# Read the dates as quarters and set as the dataframe index
rng = pd.date_range(pd.to_datetime(auxp.date[0]), periods=len(auxp.index), freq='QS')
auxp = auxp.set_index(pd.DatetimeIndex(rng))
del auxp['date']

# Show last five rows
print(auxp.tail())

# Save cleaned datafrane as a csv file
auxp.to_csv('/Users/dariaulybina/Desktop/georgetown/global-economics/additional_data/data/AU_PXP_IX.csv', header=True)

# Title and text with recent value
title = 'Australia Export Prices (index, {}=100)'.format(baseyr)
recentdate = auxp.dropna().index[-1].strftime('%B %Y')
recentval = auxp.dropna()[-1]
recent = 'Most recent: {}: {}'.format(recentdate, recentval)

# Basic plot
ax = auxp.plot(title=title, colormap='Set1')
ax.set_xlabel(recent)