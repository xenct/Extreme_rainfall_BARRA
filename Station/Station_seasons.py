"""The purpose of this script is to read in the csv files
 of the list of stations and to make plots of the data"""

# Import packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.basemap import Basemap

# Get data info from txt file. theres a bit of a weird for morewell. its too long
AWS_info = pd.read_fwf("/home/563/gt3409/Documents/AWS_data/AWS_sites.txt", 
  names = ['ID', 
           'name',
           "name2",
           "lat",
           "lon",
           "start_month",
           "start_year",
           "end_month",
           "end_year",
           "years",
           "complete",
           "AWS",
           "district"])

# Read in the data
def station_df_from_csv(file):
 """This function take the filename of a csv file containing 
station data and returns a dataframe with four fields:
 "YYYY-MM-DD", "prcp", "accum_period", and "Quality". """
 # name of fields in csv file
 col_names = [
  "YYYY",
  "MM",
  "DD",
  "prcp",
  "accum_period",
  "Quality"]
 
 # read in the csv file
 station_df = pd.read_csv(
  f"{file_location}{filename}",
  usecols = [2,3,4,5,6,7],
  skiprows = [0],
  parse_dates = [[0,1,2]],
  names = col_names)
 return station_df

#write a dictionary to store all the dataframes of the AWS data
file_location = "/home/563/gt3409/Documents/AWS_data/"
station_dataframes = {}
for ID in AWS_info["ID"]:
    filename = f"IDCJAC0009_{ID}_1800_Data.csv"
    station_dataframes[ID] = station_df_from_csv(file = f"{file_location}{filename}")

def date_subset(data, start_date, end_date):
    """This function takes a dictionary of station dataframes with ids as the keys, and writes a new dicitonary, but only from the start date to the end_date"""
    subset_data = {}
    for ID in data.keys():
       start_index = data[ID].index[data[ID]["YYYY_MM_DD"] == start_date].tolist()[0]
       end_index = data[ID].index[data[ID]["YYYY_MM_DD"] == end_date].tolist()[0]
       # Select  the data for tha BARRA time period
       subset_data[ID] = data[ID][start_index : end_index]
    return subset_data

data = station_dataframes
start_date = pd.datetime(2010, 1, 1)
end_date = pd.datetime(2016, 1, 1)
#subset the aws data to the BARRA period
BARRA_period_data = date_subset(data, start_date, end_date)

# get the mean prcp for each season
seasons = ["DJF", "MAM", "JJA", "SON"]
season_mean_prcp = {"Station_ID": seasons}
for ID in BARRA_period_data.keys():
    array = BARRA_period_data[ID].values
    means = [0, 0, 0, 0]
    for record in array:
        record_date = record[0]
        prcp = record[1]
        if np.isnan(prcp):
            prcp = 0
        means[(record_date.month)%12//3] += prcp/6
    season_mean_prcp[ID] = [round(x,1) for x in means]

# Map the dots!
#the following maps the AWS location on a shadedrelief map and labels the station with the town names
title = "AWS Station Locations"
loc_labels = ["Mildura",
 "Horsham",
 "Bendigo",
 "Wangaratta",
 "Falls Creek",
 "Orbost",
 "Morwell",
 "  Melbourne",
 "  Wallan",
 "Ballarat\n",
 "Cape Otway",
 "Hamilton"]

fig = plt.figure(figsize = (4,3)) # a new figure window
ax = fig.add_subplot(1, 1, 1) # specify (nrows, ncols, axnum)
ax.set_title(title, fontsize = 12)

map = Basemap(projection = "mill", llcrnrlon = 140, llcrnrlat = -40, urcrnrlon = 151, urcrnrlat = -33, resolution = 'l')

map.shadedrelief()
map.drawcoastlines()
map.drawrivers(color = 'b')
map.drawparallels(np.arange(-90.,120.,1.),labels=[1,0,0,0], linewidth = 0.25)
map.drawparallels(np.arange(-90.,120.,5.),labels=[0,0,0,0])
map.drawmeridians(np.arange(-180.,180.,1.),labels=[0,0,0,0], linewidth = 0.25)
map.drawmeridians(np.arange(-180.,180.,5.),labels=[0,0,0,1])

x, y = map(list(AWS_info['lon']),list(AWS_info['lat']))
map.scatter(x, y, 10, marker = 'o',color= 'k')

for i in range(len(AWS_info)):
    plt.text(x[i], y[i], loc_labels[i], ha = 'left', va = 'bottom', weight = 'semibold', fontsize=8)
plt.title(title)
plt.xlabel("\nLongitude")
plt.ylabel("Latitude\n\n")

# plt.show()
plt.savefig(f"/home/563/gt3409/Documents/images/{title}.png")


# plot the seasons:
def map_AWS_prcp(data, AWS_info = AWS_info):
    # Make colour map
    levels = [.15, .2, .25, .3, .35, .4]
    #prcp_cmap = matplotlib.colors.ListedColormap(prcp_colours)
    prcp_cmap = plt.cm.get_cmap("YlGnBu", len(levels)-1)
    norm = matplotlib.colors.BoundaryNorm(levels, len(levels)-1)
    # make a 2-by-2 plot of the four seasons
    f, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2,2)
    f.suptitle("Seasonal contribution to annual rainfall")
    ax = [ax1, ax2, ax3, ax4]
    seasons = ["DJF", "MAM", "JJA", "SON"]
    for i in range(4):
        ax[i].set_title(seasons[i], fontsize = 12)
        map = Basemap(projection = "mill", llcrnrlon = 140, llcrnrlat = -40, urcrnrlon = 151, urcrnrlat = -33, resolution = 'l', ax = ax[i])
        map.drawcoastlines()
#        map.drawrivers(color = 'b')
#        map.drawparallels(np.arange(-90.,120.,1.),labels=[0,0,0,0], linewidth = 0.25)
        map.drawparallels(np.arange(-90.,120.,5.),labels=[1,0,0,0], linewidth = 0.5, color = 'w')
#        map.drawmeridians(np.arange(-180.,180.,1.),labels=[0,0,0,0], linewidth = 0.25)
        map.drawmeridians(np.arange(-180.,180.,5.),labels=[0,0,0,1], linewidth = 0.5, color = 'w')
        x, y = map(list(AWS_info['lon']),list(AWS_info['lat']))
        m_scatter = map.scatter(x, y, s= 50, c= data[i], marker = 'o', edgecolors = 'k', cmap = prcp_cmap, norm = norm)
#        cbar = map.colorbar(m_scatter)
    f.subplots_adjust(right = 0.8)
    cax = f.add_axes([0.45, 0.2, 0.4, 0.6]) #[left, bottom, width, height]
    cax.axis("off")
    cbar = map.colorbar(m_scatter, ax = cax, size = '3%', extend = "both")
    plt.show()
    return

data = np.zeros((4, len(AWS_info)))
for i in range(4):
    for j in range(len(AWS_info)):
        ID = AWS_info['ID'][j]
        data[i, j] = season_mean_prcp[ID][i]

#map_AWS_prcp(data = data)

annual_prcp = np.zeros(len(AWS_info))
for i in range(len(AWS_info)):
    annual_prcp[i] = sum(season_mean_prcp[AWS_info['ID'][i]])

data_prop = np.zeros((4, len(AWS_info)))
for i in range(4):
    for j in range(len(AWS_info)):
        ID = AWS_info['ID'][j]
        data_prop[i, j] = season_mean_prcp[ID][i] / sum(data[:,j])

map_AWS_prcp(data = data_prop)



# plot stacked barchart

data = data_prop
r = np.arange(len(data[0]))
bottom = 0
colors = ['y', 'r', 'c', 'm']
for i in range(4):
    plt.bar(r, data[i], bottom = bottom, color = colors[i], width = 0.85)
    bottom += data[i]
plt.yticks(np.arange(0, 1.1, 0.25))
plt.xticks([])
plt.ylim(0,1)
plt.grid()
plt.title("Seasonal contribution of precipitation")
plt.legend(labels = seasons)
plt.show()












