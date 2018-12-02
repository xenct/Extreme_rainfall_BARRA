# plot the AWAP
## plot a map (help plotting points from https://peak5390.wordpress.com/2012/12/08/matplotlib-basemap-tutorial-plotting-points-on-a-simple-map/ 28-Mar-2018)(help for plotting raster data from https://annefou.github.io/metos_python/04-plotting/ april 5 2018)
#this code works from /g/data3/w42/gt3409/

from netCDF4 import Dataset
import matplotlib.pyplot as plt
import matplotlib
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

filename = "/g/data3/w42/gt3409/mean_prcp-AWAP-SE-Aust-20120101-to-20131231.nc"
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

prcp_colours = [
 "#FFFFFF", 
 '#ffffd9',
 '#edf8b1',
 '#c7e9b4',
 '#7fcdbb',
 '#41b6c4',
 '#1d91c0',
 '#225ea8',
 '#253494',
 '#081d58',
 "#4B0082"]


prcp_colormap = matplotlib.colors.ListedColormap(prcp_colours)

levels = [0., 50, 100, 200, 300, 400, 600, 1000, 1500, 2000, 3000, 5000]

norm = matplotlib.colors.BoundaryNorm(levels, 11)

cs = map.pcolormesh(x, y, data = mean_prcp * 365, norm=norm, cmap = prcp_colormap) 

# titles
plt.title("AWAP Mean Annual Precipitation for 2012-2013\nSoutheast Australia")
plt.xlabel("\n\nLongitude")
plt.ylabel("Latitude\n\n")
cbar = plt.colorbar(ticks = levels[:-1], shrink = 0.9, extend = "max")
cbar.ax.set_ylabel('Annual Precipitation (mm)')
cbar.ax.set_xticklabels(levels)

#plt.savefig(f"Documents/{filename[-46:-3]}.png")

