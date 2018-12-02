import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

"""Beaufort is a station on the High-Quality data set.
Beaufort site number: 089005
commenced: 1922
lat: -37.4483
lon: 143.3657
elevation: 450m
BOM district name: Western Plains
Less than 50km from Creswick"""

filename = 'IDCJAC0009_089005_1800/IDCJAC0009_089005_1800_Data.csv'
station = "Beaufort"


col_names = ["YYYY", "MM", "DD", "prcp", "accum_period", "Quality"]
station_df = pd.read_csv(filename, usecols = [2,3,4,5,6,7], skiprows = [0], parse_dates = [[0,1,2]], names = col_names, index_col = "YYYY_MM_DD")

# rough time series plot
station_df.plot(x="YYYY_MM_DD", y = "prcp")

# rough histogram plot
station_df.plot(x="YYYY_MM_DD", y = "prcp", kind = "hist", bins=120, xlim = [0, 30], ylim = [0, 4000])

# plot completeness
# Get start and end year. the range between these two will be the x axis of the graph
start_year = station_df["YYYY_MM_DD"].iloc[0].year
end_year = station_df["YYYY_MM_DD"].iloc[-1].year
# for each year, find the proportion of not NaNs of the number of years
# find number of days in year
day_tally = {}
for day in station_df["YYYY_MM_DD"]:
    day_tally[day.year] = day_tally.get(day.year, 0) + 1
# find prcp data is NaN
nan_tally = {}
for record in station_df.itertuples():
    if np.isnan(record[2]):    # if the rainfall amount is NaN then
        nan_tally[record[1].year] = nan_tally.get(record[1].year, 0) + 1
# Calculate completeness
completeness = []
for year in range(start_year, end_year + 1):
    try:
        completeness.append((day_tally[year] - nan_tally[year]) / day_tally[year])
    except KeyError:
        completeness.append(1)
# plot barchart
plt.bar(np.arange(start_year, end_year + 1), completeness, width = 1., align = "edge")
plt.xlim(start_year, end_year)
plt.ylim(0, 100)
plt.xlabel("Year")
plt.ylabel("Proportion of records")
plt.title(f"{station} Completeness")
fig = plt.gcf()
fig.set_size_inches(10, 2)
plt.savefig(f"{station}_Completeness.png")

## plot a map (help plotting points from https://peak5390.wordpress.com/2012/12/08/matplotlib-basemap-tutorial-plotting-points-on-a-simple-map/ 28-Mar-2018)
#from mpl_toolkits.basemap import Basemap
#map = Basemap(projection = "mill", llcrnrlon = 135, llcrnrlat = -45, urcrnrlon = 155, urcrnrlat = -30, resolution = 'l')
#map.drawcoastlines()
#map.drawmapboundary()
#
#lons = [143.3657,]
#lats = [-37.4483,]
#x, y = map(lons, lats)
#map.plot(x, y, "ro", markersize = 24)
#labels = [station,]
#for label, xpt, ypt in zip(labels, x, y):
#    plt.text(xpt + 10000, ypt + 5000, label)
#
#plt.show()
#

# Plot time series for 2010 to 2016
start_date = pd.datetime(2010, 1, 1)
end_date = pd.datetime(2015, 12, 31)

BARRA_period_data = station_df[start_date:end_date]

plt.plot(x = BARRA_period_data["YYYY_MM_DD"], y = BARRA_period_data["prcp"])
plt.title(f"{station} rainfall timeseries")
plt.xlabel("Year")
plt.ylabel("Precipitation (mm)")
plt.show()

# Check the range of accumulation periods
BARRA_period_data["accum_period"].value_counts()
# there are some accumulations up to 2 weeks in the beaufort record
# the quality for all accumulations have been marked with a 'Y'
# from the metadata txt file:
# i) If the Quality Flag = Y, then the data have completed the normal quality control
#    process and we do not believe them to be suspect or wrong;
# I am unsure whether this means that we should take this as a single value for 
# the last date, or to average the prcp value over the accumulation period

# Checking the record of maximum value that seems like a big outlier: 
BARRA_period_data[BARRA_period_data["prcp"] == np.max(BARRA_period_data["prcp"])]
# Out[170]: 
#             prcp  accum_period Quality
# YYYY_MM_DD                            
# 2011-01-14  96.8           1.0       Y#this date corresponds to big flooding in 2011

# group each record by the month-day date and find the mean of every date
# plot the mean rainfall per date including days of no rainfall 
# In the case of Feb 29, all feb 29s are averaged and stored as feb 29. 
# This will not be as smooth as other dates

# Build 2 lists. xticks_locs for the location of the first of the months and
# xticks_labels for the three letter month labels "Jan", "Feb", etc
xticks_locs = []
xticks_labels = []
for i in range(1,13):
    xticks_locs.append(pd.datetime(2000, i, 1).strftime('%m%d'))
    xticks_labels.append(pd.datetime(2000, i, 1).strftime('     %b'))

# Plot the average rainfall for each date for BARRA period    
plt.plot(BARRA_period_data.groupby(BARRA_period_data.index.strftime("%m%d"))["prcp"].mean())
plt.title(f"Mean rainfall for every date in {station}")
plt.xlabel("Date")
plt.xticks(xticks_locs, xticks_labels)
plt.xlim(0, 366)
plt.ylim(0)
plt.ylabel("Daily Mean Precipitation (mm)")
plt.grid(axis = 'y')
fig = plt.gcf()
fig.set_size_inches(10, 4)
plt.savefig(f"{station}_Mean_prcp_per_date_2010_2016.png")

# plt for record length
plt.plot(station_df.groupby(station_df.index.strftime("%m%d"))["prcp"].mean())
plt.title(f"Mean rainfall for every date in {station}")
plt.xlabel("Date")
plt.xticks(xticks_locs, xticks_labels)
plt.xlim(0, 366)
plt.ylim(0)
plt.ylabel("Daily Mean Precipitation (mm)")
plt.grid(axis = 'y')
fig = plt.gcf()
fig.set_size_inches(10, 4)
plt.savefig(f"{station}_Mean_prcp_per_date_1882_2016.png")



