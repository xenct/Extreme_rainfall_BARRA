# plot the AWAP
## plot a map (help plotting points from https://peak5390.wordpress.com/2012/12/08/matplotlib-basemap-tutorial-plotting-points-on-a-simple-map/ 28-Mar-2018)(help for plotting raster data from https://annefou.github.io/metos_python/04-plotting/ april 5 2018)
#this code works from home

from netCDF4 import Dataset
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

# Get the data
def load_2D_netCDF(filename, var_name, lat_name, lon_name):
    """This function loads a two dimensional netCDF.
    Give filename as a string.
    Give name of measured variable.
    Give the names of the two spatial coordinates.
    The function returns the variable, and the two dimenstions"""
    data = Dataset(filename, 'r')
    var = data[var_name][:]
    lats = data[lat_name][:]
    lons = data[lon_name][:]
    data.close()
    return var, lats, lons

filename = "/g/data3/w42/gt3409/mean_prcp-AWAP-SE-Aust-20120101-to-20120107.nc"
var_name = "mean_prcp"
lat_name = "lats"
lon_name = "lons"

mean_prcp, lats, lons = load_2D_netCDF(filename, var_name, lat_name, lon_name)

# mean_prcp[mean_prcp == 0] = np.NaN


fig = plt.figure() # a new figure window
ax = fig.add_subplot(1, 1, 1) # specify (nrows, ncols, axnum)
ax.set_title(filename, fontsize = 12)

map = Basemap(projection = "mill", llcrnrlon = lons[0], llcrnrlat = lats[-1], urcrnrlon = lons[-1], urcrnrlat = lats[0], resolution = 'l')

map.drawcoastlines()
map.drawmapboundary()
map.drawparallels(np.arange(-90.,120.,5.),labels=[1,0,0,0])
map.drawmeridians(np.arange(-180.,180.,5.),labels=[0,0,0,1])

llons, llats = np.meshgrid(lons, lats)
x,y = map(llons,llats)

cs = map.pcolormesh(x, y, data = mean_prcp, cmap = "Blues") 

# titles
plt.title("AWAP mean daily precipitation from Jan 1 to Jan 7 2012\nSouth East Australia")
plt.xlabel("\n\nLongitude")
plt.ylabel("Latitude\n\n")
cbar = plt.colorbar(shrink = 0.9, extend = "max")
cbar.ax.set_ylabel('Mean Precipitation (mm per day)')

plt.savefig(f"Documents/{filename[0:-2]}png")

