"""
 This is a python script of all my functions, for:
- reading data from 2D and 3D netCDFs
- mapping BARRA and AWAP data
"""

# packages for loading netCDFs
from netCDF4 import Dataset, num2date
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats.mstats import mquantiles
from scipy.stats import spearmanr, linregress
from scipy.ndimage import convolve
from scipy.ndimage import binary_dilation
from datetime import timedelta, date, datetime
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
import cartopy.crs as ccrs
import xarray as xr

# Getting data from netCDF files

def load_2D_netCDF(filename, var_name = "mean_prcp", lat_name = "lats", lon_name = "lons"):
    """
    This function loads a two dimensional netCDF.
    Give filename as a string.
    Give name of measured variable.
    Give the names of the two spatial coordinates.
    The function returns the variable, and the two dimenstions
"""
    data = Dataset(filename, 'r')
    var = data[var_name][:]
    lats = data[lat_name][:]
    lons = data[lon_name][:]
    data.close()
    return var, lats, lons

def load_3D_netCDF(filename, var_name = "prcp", lat_name = "lats", lon_name = "lons", time_name = "time"):
    """
    This function loads a three dimensional netCDF.
    Give filename as a string.
    Give name of the measured variable.
    Give the names of the two spatial coordinates.
    Give the name of the time dimension.
    The function returns the variable, the two spatial dimensions, and the times.
"""
    data = Dataset(filename, 'r')
    var = data[var_name][:]
    lats = data[lat_name][:]
    lons = data[lon_name][:]
    time = data[time_name][:]
    time = np.array(time)
    t_unit = data.variables[time_name].units
    t_cal = data.variables[time_name].calendar
    datevar = num2date(time, units = t_unit,calendar = t_cal)
    data.close()
    return var, lats, lons, datevar


def lat_lon_mask(lons_full, lats_full, lon_min, lon_max, lat_min, lat_max):
    """Thie function takes a full list of latitudes and longitudes, and minimum and maximum values for lats and lons. The function returns a 2D mask which specifies True for every coordinate between (and including) the boundaries. the function also returns the shortened lats and lons"""
    # Mask lons
    lon_mask = (lons_full >= lon_min) & (lons_full <= lon_max)
    lons = lons_full[lon_mask]
    # Mask lats
    lat_mask = (lats_full >= lat_min) & (lats_full <= lat_max)
    lats = lats_full[lat_mask]
    # make 2D mask
    lat_lon_mask = lon_mask[np.newaxis, :] & lat_mask[:, np.newaxis]
    return lat_lon_mask, lats, lons

# Mapping AWAP and BARRA data

# specify the colours for the colours mapping for precipitation
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
prcp_colormap = ListedColormap(prcp_colours)



# Specify the levels for each colour segment. 
# These are suitable for Victoria annual rainfall totals for different periods
levels = {}
levels["hour"]  = [0., 0.2,   1,   5,  10,  20,  30,   40,   60,   80,  100,  150]
levels["day"]   = [0., 0.2,  5, 10,  20,  30,  40,  60,  100,  150,  200,  300]
levels["week"]  = [0., 0.2,  10,  20,  30,  50, 100,  150,  200,  300,  500, 1000]
levels["month"] = [0.,  10,  20,  30,  40,  50, 100,  200,  300,  500, 1000, 1500]
levels["year"]  = [0.,  50, 100, 200, 300, 400, 600, 1000, 1500, 2000, 3000, 5000]

# Specify colormaps for frequency plots
# Define a set of levels for annual frequency exceedences
freq_levels = {}
freq_levels['very low'] = [0, 1, 2, 3, 4, 5, 10, 20]
freq_levels['low'] = [0, 1, 2, 5, 10, 20, 30, 40]
freq_levels['med'] = [0, 1, 5, 10, 20, 30, 60, 100]
freq_levels['high'] = [0, 20, 45, 60, 90, 150, 200, 250]
freq_levels['very high'] = [0, 30, 60, 90, 150, 210, 270, 366]

# specify the colours for the frequency colours mapping, fewer than the precipitation
freq_colours = [
     "#FFFFFF", 
     '#edf8b1',
     '#7fcdbb',
     '#1d91c0',
     '#253494',
     '#081d58',
     "#4B0082"]
freq_colormap = ListedColormap(freq_colours)

#symetrical blu rd colour map with with in centre
from pylab import cm
custom_RdBu = cm.get_cmap("RdBu",20)(np.arange(20))
custom_RdBu[9] = [1,1,1,1]
custom_RdBu[10] = [1,1,1,1]
cmap_custom_RdBu = LinearSegmentedColormap.from_list("RdWtBu", custom_RdBu, 20) 

def map_prcp(data, lats, lons, title = "Title", projection = ccrs.PlateCarree(), latlonbox = [135,155,-45,-30], cmap = prcp_colormap, levels = levels['year'], cmap_label = "cmap label", cmap_extend = 'max'):
    norm = BoundaryNorm(levels, len(levels)-1)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection=projection)
    ax.set_extent(latlonbox) 
    im = plt.pcolormesh(lons, lats, data, transform = projection, cmap = cmap, norm = norm)
#    ax.scatter(np.array(list(HQ_info.values()))[:,1], np.array(list(HQ_info.values()))[:,0], transform = projection, c = 'k', marker = '.')
    ax.coastlines('10m')
    if cmap_extend == "max":
        cbar_ticks = levels[:-1]
    else: # if cbar_ticks == "both"
        cbar_ticks = levels[:]
    cbar = plt.colorbar(im, ticks = cbar_ticks, shrink = 0.8, extend = cmap_extend)
    cbar.ax.set_ylabel(cmap_label)
    cbar.ax.set_xticklabels(levels)
    plt.title(title)
    plt.tight_layout()
    return

def map_dots(data, lats, lons, title = "Title", projection = ccrs.PlateCarree(), latlonbox = [135,155,-45,-30], cmap = prcp_colormap, levels = levels['year'], cmap_label = "cmap label", cmap_extend = 'max'):
    norm = BoundaryNorm(levels, len(levels)-1)
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection=projection)
    ax.set_extent(latlonbox) 
    im = plt.pcolormesh(lons, lats, data, transform = projection, cmap = cmap, norm = norm)
    ax.scatter(AWS_lons, AWS_lats, transform = projection, c = aws_color, marker = 'o', cmap = cmap, norm = norm, edgecolors = 'k')
    ax.coastlines('10m')
    if cmap_extend == "max":
        cbar_ticks = levels[:-1]
    else: # if cbar_ticks == "both"
        cbar_ticks = levels[:]
    cbar = plt.colorbar(im, ticks = cbar_ticks, shrink = 0.8, extend = cmap_extend)
    cbar.ax.set_ylabel(cmap_label)
    cbar.ax.set_xticklabels(levels)
    plt.title(title)
    plt.tight_layout()
    return

def draw_cbar_prcp(levels = levels["year"]):
    """
This function draws a colour bar, extended at the max. 
It is  YlGnBu colourscale with 11 levels, appropriate for annual rainfall. 
The position of the color bar is centred and to the right of the existing plot.
"""
    cbar = plt.colorbar(ticks = levels[:-1], shrink = 0.6, extend = "max", anchor = (0,0.5))
    cbar.ax.set_ylabel('Precipitation (mm)')
    cbar.ax.set_xticklabels(levels)
    return
    
# load AWAP and BARRA daily data
prcp_data = {}
for seas in  ['', 'DJF', 'MAM', 'JJA', 'SON']:
    if len(seas)<3:
        seas = 'ann'
        AWAP_file = '/g/data3/w42/gt3409/AWAP/AWAP_PRCP_2010-2015_0.11deg_small.nc'
        prcp_data[f'AWAP_{seas}'], AWAP_lats, AWAP_lons, AWAP_times = load_3D_netCDF( AWAP_file, 'pre', lat_name='lat', lon_name='lon', time_name = 'time')
        BARRA_file = '/g/data3/w42/gt3409/BARRA_R/BARRA_R_daily_prcp_2010-2015_small.nc'
        prcp_data[f'BARRA_{seas}'], BARRA_lats, BARRA_lons, BARRA_times = load_3D_netCDF(BARRA_file, 'prcp')
    else:
        AWAP_file = f'/g/data3/w42/gt3409/AWAP/AWAP_PRCP_2010-2015_0.11deg_small_{seas}.nc'
        prcp_data[f'AWAP_{seas}'], _, _, _ = load_3D_netCDF( AWAP_file, 'pre', lat_name='lat', lon_name='lon')
        BARRA_file = f'/g/data3/w42/gt3409/BARRA_R/BARRA_R_daily_prcp_2010-2015_small_{seas}.nc'
        prcp_data[f'BARRA_{seas}'], _, _, _ = load_3D_netCDF(BARRA_file, 'prcp')
    prcp_data[f'BARRA_{seas}'] = prcp_data[f'BARRA_{seas}']*[np.sum(prcp_data['AWAP_ann'],0)>1]

# Functions to create timeseries from gridded data
def nearest_coord(goal, lats, lons):
    """This function takes a goal location as a tuple, and lists of latitudes and longitudes for gridded data and returns the indices of the closest grid box as a tuple, and the values of the nearest coordinates as a tuple.
    This function requires np. 
    """
    coords = [lats, lons]
    idx = [0,0]
    for i in [0, 1]:
        coords[i] = np.asarray(coords[i])
        idx[i] = np.abs(coords[i] - goal[i]).argmin()
    return tuple(idx), (lats[idx[0]], lons[idx[1]])

# get the values of the closest (2n+1)^2 grids
def values_of_nsquare(data, centre_indices, n = 1):
    """This function gets the values of the closest (2n+1)^2 grids from a tuple pair of indices relating to coordinates of lat and lon in 2D data.
The default of n = 1 describes a grid of 9. 
It returns a list of the values in the square."""
    # Calculate the indices of the closest (2n+1)^2 squares
    # this code should work on edge points but print a Caution message when this occurs
    lat_ix, lon_ix = centre_indices
    n2_square_coords = []
    for i in range(-n, n + 1):
        if (lon_ix + i >= 0) & (lon_ix + i < data.shape[1]): # data.shape[1] ~ len(lons)
            for j in range(-n, n + 1):
                if (lat_ix + j >= 0) & (lat_ix + j < data.shape[0]): # data.shape[0] ~ len(lats)
                    n2_square_coords.append([lat_ix + j, lon_ix + i])
                else:
                    print("Caution. Edge of lats reached.")
        else:
            print(f"Caution. Edge of lons reached. {centre_indices}")
            break
    # for each of the squares coordinates, get the prcp values and find the average
    values = []
    for lat, lon in n2_square_coords:
        values.append(data[lat, lon])
    return values

# this function can be used as a rough estimate to line up BARRA hourly and AWAP daily data
# I plan to make this function redundant by making a file of 9am to 9am BARRA prcp file, rather than this quick and dirty approach which makes 00UTC to 00UTC time
def nsquare_day_prcp(data, centre_indices, n = 1):
    """This function calculates the days rainfall, averages over the (2n+1)^2 grid boxes surrounding the central grid box.
It takes the 3D data, the 2-tuple of indices defining the central grid and an integer n describing the size of the averaging area. 
Returns one prcp value representing the mm of prcp in the square for 24 hours"""
    nsquare_means = [] # the 24 mean hourly rainfalls over (2n+1)^2 grids
    for hour in range(24):
        values = values_of_nsquare(data[hour], centre_indices, n)
        nsquare_means.append(np.mean(values))
    nsquare_day_prcp = np.sum(nsquare_means) # The daily mean value is the sum of the 24 mean values
    return nsquare_day_prcp

# Handy date range function
def date_range(start_date, end_date):
    """This function takes a start date and an end date as datetime date objects.
It returns a list of dates for each date in order starting at the first date and ending with the last date. Requires: from datetime import timedelta, date, datetime"""
    return [start_date + timedelta(x) for x in range((end_date - start_date).days + 1)]

def BARRA_daily_ts(start_date, end_date, station_coords, n = 0):
    """This function combines multiple functions here:
- date_range()
- load_3D_netCDF()
- nearest_coord()
- values_of_nsquare()
takes start and end dates, the name of the varaible, station coordinates for the goal loaction, and n for the size of the (2n+1)^2 box.
The function returns the dates for the timseries and the timseries of daily prcp amounts."""
    # Specify the date range
    dates = date_range(start_date, end_date)
    day_prcp = []
    for DATE in dates: # for each date
        filename = f"/g/data3/w42/gt3409/BARRA_R/daily_prcp/{DATE.year}/{DATE.month:02d}/accum_prcp-BARRA_R-v1-daily-{DATE.strftime('%Y%m%d')}.nc" # get the unique filename 
        try:
            prcp, lats, lons= load_2D_netCDF(filename, 'prcp') # load all the data for that day
            centre_indices, _ = nearest_coord(station_coords, lats, lons) # Get the indices of the nearest grid box
            day_prcp.append(values_of_nsquare(prcp, centre_indices, n)) # Write a list of mean daily prcp totals as day_prcp
        except Exception:
            day_prcp.append(np.nan)
            continue
    return dates, day_prcp

# The following gets the AWAP data, lats, lons and times.
def get_AWAP(filename = ["/home/563/gt3409/Documents/AWAP_PRCP_2010-2011_0.5deg_land.nc", "/home/563/gt3409/Documents/AWAP_PRCP_2012-2013_0.5deg_land.nc"]):
    """THis function loads the AWAP data from the netCDF file, and changes the AWAP times to datetime.dates"""
    AWAP_start_date = date(2010,1,1)
    AWAP_end_date = date(2013,12,31)
    AWAP = {}
    times = {}
    for i in range(len(filename)):
        AWAP[i], lats, lons, times[i] = load_3D_netCDF(filename[i], "pre", "lat", "lon", "time")
    AWAP_data = np.concatenate((AWAP[0], AWAP[1]), axis = 0)
    times = np.concatenate((times[0],times[1]))
    # From the YYYYMMDD. format of AWAP dates, I will extract the start and end date as datetime.date objects to use as dates.
    AWAP_start_date = date(int(str(times[0])[0:4]), int(str(times[0])[4:6]), int(str(times[0])[6:8]))
    AWAP_end_date = date(int(str(times[-1])[0:4]), int(str(times[-1])[4:6]), int(str(times[-1])[6:8]))
    times = date_range(AWAP_start_date, AWAP_end_date)
    return AWAP_data, lats, lons, times

def AWAP_daily_square(data, lats, lons, times, start_date, end_date, station_coords= (-37.6655, 144.8321), n = 1):
    dates = date_range(start_date, end_date)
    indices, coords = nearest_coord(station_coords, lats, lons)
#    indices = (indices[0], indices[1])
    AWAP_box = []
    ix1 = times.index(start_date)
    ix2 = times.index(end_date)+1
    data = data[ix1:ix2]
    for day in data:
        values = values_of_nsquare(day, indices, n)
        AWAP_box.append(np.nanmean(values))
    return dates, AWAP_box

# timeseries
def plot_BARRA_timeseries_lines(start_date, end_date, station_coords):
    dates, BARRA_single = BARRA_daily_ts(start_date, end_date, station_coords, n = 0)
    _, BARRA_nine       = BARRA_daily_ts(start_date, end_date, station_coords, n = 1)
    #_, BARRA_25         = BARRA_daily_ts(start_date, end_date, station_coords, n = 2)
    _, BARRA_121        = BARRA_daily_ts(start_date, end_date, station_coords, n = 5) #Similar (bit less) coverage to AWAP_nine
    fig = plt.figure(figsize=(10,4))
    ax1 = fig.add_subplot(111)
    plt.grid(axis = 'y')
    ax1.plot(dates, BARRA_single, label = "BARRA single")
    ax1.plot(dates, BARRA_nine, label = "BARRA nine")
    ax1.plot(dates, BARRA_121, label = "BARRA 121")
    plt.legend()
    plt.title(f"{dates[1].strftime('%B %Y')} Melbourne Precipitation")
    plt.xlabel("Date")
    plt.xticks(dates, [date.day for date in dates])
    plt.ylabel("Daily Precipitation (mm)")
    plt.show()
    return

def plot_AWAP_BARRA_AWS_timeseries(AWAP_data, BARRA_data, AWS_data, start_date = date(2012,1,1), end_date = date(2013,1,1), coords = (-37.6655, 144.8321)):
    dates = date_range(start_date, end_date)
    fig = plt.figure(figsize=(10,4))
    ax1 = fig.add_subplot(111)
    plt.grid(axis = 'y')
    ax1.plot(dates, BARRA_data, label = "BARRA")
    ax1.plot(dates, AWAP_data,  label = "AWAP")
    ax1.plot(dates, AWS_data,   label = "AWS")
    plt.legend()
    plt.title(f"{dates[1].strftime('%B %Y')} Melbourne Precipitation")
    plt.xlabel("Date")
    plt.xticks(dates, [date.day for date in dates])
    plt.ylabel("Daily Precipitation (mm)")
    plt.show()
    return    

# Get the 2012 years station data from Melbourne airport
# filename = "/home/563/gt3409/Documents/IDCJAC0009_086282_2012_Data.csv"
def get_AWS_data(filename):
   col_names = ["YYYY", "MM", "DD", "prcp", "accum_period", "Quality"]
   station = pd.read_csv(filename, usecols = [2,3,4,5,6,7], skiprows = [0], parse_dates = [[0,1,2]], names = col_names, index_col = "YYYY_MM_DD")
   return station

# Number of days above a threshold
def freq_above_threshold(data, threshold = 1.0):
    """This function takes prcp data and count the number of times the data exceeds a threshold in (mm).
    The default threshold defines a standard wet day as defined by ETCCDI, given that the period of the data is daily."""
    count = 0
    for datum in data:
        if datum >= threshold:
            count += 1
    return count

# for gridded data. counts the number of days above a threshold
def freq_exceed_2d(data, threshold = 1.0):
    """for gridded data as np.array count the number of days the prcp for that cell is equal or greater than the threshold (mm). the default value is 1.0mm, the ETCCDI definition of a 'wet day'."""
    counts_array = np.zeros(data[0].shape)
    for day in range(len(data)):
    # if the value of the cell exceeds the threshold, then update the cell count by one (remebering that the mask of true and false can be a mask of 1s and 0s.
        counts_array += (data[day] > threshold)&(data[day] < 900)
    return counts_array

# function to plot a quantile-quantile plot.
def qqplot(data1, data2):
    """This function takes two distributions and plots the 100 quantiles of the second against the 100 quantiles of the first.
     The function does not require the two datasets to be the same size.
     The function use matplotlib.pyplot as plt and mquantiles from scipy.stats.mstats"""
    data1_quantiles = mquantiles(data1, prob = np.arange(0,1,0.0001))
    data2_quantiles = mquantiles(data2, prob = np.arange(0,1,0.0001))
    plt.scatter(x= data1_quantiles, y= data2_quantiles, marker = '.')
    maximum = max(max(data1_quantiles), max(data2_quantiles))
    minimum = min(min(data1_quantiles), min(data2_quantiles))
    plt.plot([minimum, maximum], [minimum, maximum], color = 'r')
    return


